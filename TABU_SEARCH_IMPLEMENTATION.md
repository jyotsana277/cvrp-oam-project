# Tabu Search Implementation Guide

Comprehensive guide to the Tabu Search refinement component.

## Table of Contents
1. [TS Overview](#ts-overview)
2. [Core Concepts](#core-concepts)
3. [Neighborhood Structure](#neighborhood-structure)
4. [Tabu List Management](#tabu-list-management)
5. [Aspiration Criteria](#aspiration-criteria)
6. [Search Process](#search-process)
7. [Parameter Tuning](#parameter-tuning)
8. [Implementation Details](#implementation-details)
9. [Enhancements](#enhancements)
10. [Convergence Analysis](#convergence-analysis)

---

## TS Overview

### What is Tabu Search?

Tabu Search is a local search metaheuristic that:
- **Moves** to neighbor solutions iteratively
- **Remembers** recently visited solutions (tabu list)
- **Forbids** moves to tabu solutions (prevents cycling)
- **Accepts** worse solutions occasionally (escape local optima)
- **Tracks** best solution ever found

### Why Tabu Search for CVRP?

| Property | Advantage |
|----------|-----------|
| Local Optimization | Refines solutions quickly |
| Memory | Prevents revisiting solutions |
| Escape Mechanism | Accepts worse moves (controlled) |
| Deterministic | No randomness (reproducible) |
| Integration | Combines well with GA |

### TS vs Other Local Search Methods

```
Method           | Speed | Quality | Robustness | Memory
Random Restart   | Fast  | Poor    | Low        | None
Hill Climbing    | Fast  | Medium  | Low        | None
Simulated Ann.   | Medium| Medium  | Medium     | None
Tabu Search      | Medium| Good    | High       | Yes (tabu list)
```

---

## Core Concepts

### Move Definition

**What is a Move?**

In our CVRP TS, a move relocates one customer between routes:

```
Move = (from_route, customer_index, to_route, insert_position)

Example:
  Move = (0, 2, 1, 3)
  Meaning: Take 3rd customer from route 0, insert at position 3 in route 1
```

### Solution Space

**Set of all feasible solutions** reachable from current solution:

```
Current Solution:
  Route 1: [0, 1, 3, 0]
  Route 2: [0, 2, 4, 0]

Neighbor 1 (move customer 1 to route 2):
  Route 1: [0, 3, 0]
  Route 2: [0, 2, 4, 1, 0]

Neighbor 2 (move customer 2 to route 1):
  Route 1: [0, 1, 3, 2, 0]
  Route 2: [0, 4, 0]

... (many more neighbors)
```

### Objective Function

**What we optimize**: Total distance

```
f(solution) = Sum of all route distances
           = Sum over all routes of (distance traveled + return to depot)

Minimize f(solution)
```

---

## Neighborhood Structure

### 1-Exchange (Relocation) Neighborhood

**Move Type**: Relocate customer between routes

**Definition**:
```
For each customer i in route r1:
  For each other route r2:
    For each position p in r2:
      Generate neighbor by:
        1. Remove i from r1
        2. Insert i at position p in r2
        3. Verify feasibility
```

**Neighborhood Size**:
$$|N| = \text{routes} \times \text{avg customers per route} \times \text{routes} \times \text{positions}$$

Typically: $O(r^2 \times n)$ where $r$ = routes, $n$ = customers

**Example**:
```
Current: Route1=[0,1,3,0], Route2=[0,2,4,0]
Customer 1 from Route 1:
  - Move to Route2, position 1: [0,1,2,4,0]
  - Move to Route2, position 2: [0,2,1,4,0]
  - Move to Route2, position 3: [0,2,4,1,0]
  
(Similar for other customers and routes)
```

### Feasibility Constraint

**Only valid moves** produce feasible solutions:

```
Move is feasible if:
  1. Source route remains valid (depot intact)
  2. Target route respects capacity:
     load(target_route) + demand(customer) ≤ capacity
  3. Solution is connected (all customers served)
```

**Implementation**:
```python
def is_move_feasible(move, routes, demands, capacity):
    from_route_idx, cust_idx, to_route_idx, insert_pos = move
    
    # Check target capacity
    target_route = routes[to_route_idx]
    customer = routes[from_route_idx][cust_idx + 1]
    new_load = sum(demands[c] for c in target_route if c != 0)
    new_load += demands[customer]
    
    return new_load <= capacity
```

---

## Tabu List Management

### Tabu List Concept

**Purpose**: Prevent revisiting recently explored solutions

**Mechanism**: 
- Track recently made moves
- Forbid inverse/similar moves for N iterations
- When move tenure expires, remove from list

### Move Representation

```
Move = (from_route, customer, to_route, position)

Example moves that are tabu:
  Move: (0, 2, 1, 3) - Move customer 2 from route 0 to route 1
  Tenure: 10 iterations
  
After iteration 5:
  Remaining tenure: 5 iterations (10 - 5)
  
After iteration 10:
  Move expires from tabu list
```

### Tabu Tenure

**Definition**: How long moves stay tabu (in iterations)

```
Tabu Tenure = 10 (default)
  ↓
Iteration 1: Move added to tabu, tenure = 10
Iteration 2: Tenure = 9
...
Iteration 10: Tenure = 1
Iteration 11: Tenure expires, move removed
```

**Effects of Tabu Tenure**:

```
Tenure | Effect | Convergence
  5    | Short memory, allow revisiting | Fast, risky
 10    | Balanced (recommended) | Medium, good quality
 15    | Long memory, restrict search | Slow, thorough
 20+   | Very restrictive | Very slow
```

**Adaptive Tenure**:
```python
def adaptive_tabu_tenure(problem_size, iteration):
    """Increase tenure as search progresses"""
    base_tenure = 10
    return base_tenure + (iteration // 100)  # Increases every 100 iterations
```

### Tabu List Update

**Algorithm**:
```
UpdateTabuList(tabu_list, new_move):
  1. Decrease all tenures by 1
  2. Remove expired moves (tenure ≤ 0)
  3. Add new_move with tenure = tabu_tenure
```

**Implementation**:
```python
def update_tabu_list(tabu_list, new_move, tabu_tenure=10):
    # Decrease tenure
    updated_list = {}
    for move, tenure in tabu_list.items():
        if tenure - 1 > 0:
            updated_list[move] = tenure - 1
    
    # Add new move
    updated_list[new_move] = tabu_tenure
    
    return updated_list
```

### Tabu List Data Structure

**Efficient Implementation**:
```python
class TabuList:
    def __init__(self, max_size=100):
        self.tabu_dict = {}  # move → tenure
        self.max_size = max_size
    
    def add(self, move, tenure):
        """Add move with tenure"""
        self.tabu_dict[move] = tenure
        # Keep size reasonable
        if len(self.tabu_dict) > self.max_size:
            oldest_move = min(self.tabu_dict, key=self.tabu_dict.get)
            del self.tabu_dict[oldest_move]
    
    def is_tabu(self, move):
        """Check if move is tabu"""
        return move in self.tabu_dict and self.tabu_dict[move] > 0
    
    def decay(self):
        """Decrease all tenures"""
        for move in list(self.tabu_dict.keys()):
            self.tabu_dict[move] -= 1
            if self.tabu_dict[move] <= 0:
                del self.tabu_dict[move]
```

---

## Aspiration Criteria

### Purpose

Override tabu status when beneficial:

```
Without aspiration:
  Tabu move always forbidden
  → Can get stuck in local optima
  
With aspiration:
  Tabu move allowed if better than best-ever
  → Escape local optima while still restricting cycling
```

### Aspiration by Objective Value

**Most Common Type** (used in our implementation):

```
ACCEPT tabu move IF:
  neighbor_cost < best_cost_ever_found
  
Rationale:
  - If solution better than any before, worthy of exploration
  - Even if tabu (may be revisiting region)
  - Overrides tabu restriction
```

**Implementation**:
```python
def check_aspiration_criteria(move, neighbor_distance, best_distance):
    """Accept tabu move if better than best ever"""
    return neighbor_distance < best_distance
```

### Example

```
Best solution ever: distance = 1200
Current tabu list: [Move A, Move B, Move C]

Iteration 5:
  Candidate neighbor from tabu move A: distance = 1150
  
  Is tabu? Yes, Move A in tabu list
  Aspiration criteria: 1150 < 1200? YES
  
  Decision: ACCEPT move (aspiration override)
  Update: best_distance = 1150

Iteration 6:
  Candidate neighbor from Move A again: distance = 1170
  
  Is tabu? Yes
  Aspiration criteria: 1170 < 1150? NO
  
  Decision: REJECT move (tabu, aspiration fails)
```

### Other Aspiration Criteria (Advanced)

**Aspiration by History**:
```python
def aspiration_by_history(move, move_frequency):
    """Accept tabu move if rarely used"""
    return move_frequency[move] < threshold
```

**Aspiration by Value & Count**:
```python
def aspiration_by_both(neighbor_distance, best_distance, 
                      move_frequency, move, threshold_freq):
    return (neighbor_distance < best_distance * 1.01 and 
            move_frequency[move] < threshold_freq)
```

---

## Search Process

### Single Iteration

```
Algorithm: TabuSearchIteration
Input: current_solution, tabu_list, best_solution, best_distance
Output: next_solution, next_distance, improved

1. Generate neighborhood of current solution
2. Evaluate all feasible neighbors
3. For each neighbor:
     a. Calculate distance
     b. Check if move is tabu
     c. Apply aspiration criteria if tabu
     d. Rank non-tabu neighbors
4. Select best non-tabu neighbor
5. If no non-tabu neighbors, stop (local optimum)
6. Move to selected neighbor
7. Update tabu list
8. If neighbor improves best → update best_solution
9. Return selected neighbor and updated tabu list
```

**Pseudo-code**:
```python
def tabu_search_iteration(current_routes, tabu_list, best_distance):
    # Generate neighborhood
    neighbors = generate_neighborhood(current_routes)
    
    best_neighbor = None
    best_neighbor_distance = float('inf')
    best_neighbor_move = None
    aspiration_applied = False
    
    # Evaluate all neighbors
    for neighbor_routes, move in neighbors:
        neighbor_distance = calculate_distance(neighbor_routes)
        is_tabu = is_move_tabu(move, tabu_list)
        
        # Check aspiration
        if is_tabu and neighbor_distance < best_distance:
            is_tabu = False
            aspiration_applied = True
        
        # Select best non-tabu
        if not is_tabu and neighbor_distance < best_neighbor_distance:
            best_neighbor = neighbor_routes
            best_neighbor_distance = neighbor_distance
            best_neighbor_move = move
    
    # If no valid move found, stop
    if best_neighbor is None:
        return current_routes, current_distance, False
    
    # Update tabu list
    tabu_list = update_tabu_list(tabu_list, best_neighbor_move)
    
    return best_neighbor, best_neighbor_distance, True
```

### Full Tabu Search Loop

```
Algorithm: TabuSearch
Input: initial_solution, max_iterations, tabu_tenure
Output: best_solution, best_distance

1. current = initial_solution
2. best = initial_solution
3. best_distance = calculate_distance(best)
4. tabu_list = empty
5. iteration_count = 0

WHILE iteration_count < max_iterations:
  6a. next, next_distance, improved = TabuSearchIteration(...)
  6b. IF improved = FALSE: BREAK (no valid moves)
  6c. current = next
  6d. IF next_distance < best_distance:
      i.   best = next
      ii.  best_distance = next_distance
      iii. Print "New best found!"
  6e. iteration_count += 1
  6f. IF iteration_count % 10 = 0: Print progress

7. Return best, best_distance
```

### Convergence Behavior

```
Distance
    ↑
  1500 |*                    Starting solution
       | \
  1400 |  \*
       |   |\
  1300 |   | \*
       |   |  | \*
  1250 |   |  |  *-*  Oscillation around local optimum
       |   |  |  \| \
  1200 |   |  |___*  * (best found)
       |   |
  1150 |___|____________(theoretical global optimum)
       └─────────────────→ Iteration
       0  5  10  15  20  25
```

---

## Parameter Tuning

### Tabu Tenure

**Recommended Values**:
```
Small problems (n < 30):    Tenure = 5-8
Medium (30-100):            Tenure = 10-15
Large (100+):               Tenure = 20-25
```

**Tuning Strategy**:
```python
def find_optimal_tenure(initial_solution, problem_size):
    """Auto-tune tabu tenure"""
    base_tenure = int(problem_size ** 0.3)  # Scales with problem size
    return max(5, min(25, base_tenure))  # Clamp to [5, 25]
```

### Iteration Count

**Typical Settings**:
```
Quick test:         5-10 iterations
Standard:           20-30 iterations
Thorough:           50+ iterations
```

**Relationship to GA**:
- In hybrid: TS iterations = 1/2 to 1/3 of GA generations
- Example: GA 30 gens → TS 10-15 iterations per gen

### Neighborhood Size

**If too many neighbors**:
- Computation becomes expensive
- Use move restriction (consider best moves only)

**Implementation**:
```python
def generate_neighborhood_limited(routes, max_neighbors=100):
    """Generate top neighbors only"""
    all_neighbors = generate_neighborhood(routes)
    if len(all_neighbors) <= max_neighbors:
        return all_neighbors
    
    # Score and keep top ones
    scored = [(n, calculate_distance(n[0])) for n in all_neighbors]
    top = sorted(scored, key=lambda x: x[1])[:max_neighbors]
    return [n[0] for n in top]
```

---

## Implementation Details

### TabuSearch Class Structure

```python
class TabuSearch:
    def __init__(self, dist, demands, capacity, depot=0):
        self.dist = dist                    # Distance matrix
        self.demands = demands              # Customer demands
        self.capacity = capacity            # Vehicle capacity
        self.depot = depot                  # Depot index
        self.tabu_list = {}                 # Move → tenure
        self.tabu_tenure = 10               # Default tenure
    
    def calculate_routes_distance(self, routes):
        """Total distance of solution"""
        pass
    
    def is_route_feasible(self, route):
        """Check capacity constraint"""
        pass
    
    def generate_neighborhood(self, routes):
        """Create all feasible neighbors"""
        pass
    
    def refine_solution(self, routes, iterations=20, verbose=True):
        """Run full TS"""
        pass
```

### Performance Optimization

**Incremental Distance Updates**:
```python
def distance_after_move(current_distance, move, dist_matrix):
    """Calculate new distance without full recalculation"""
    # Instead of recalculating entire distance
    # Calculate delta: old_edges_removed + new_edges_added
    delta = 0
    # (Remove old edges) - (Add new edges)
    return current_distance + delta
```

**Move Caching**:
```python
class TabuSearchOptimized:
    def __init__(self, ...):
        self.move_cache = {}  # Memoize neighbor evaluations
    
    def generate_neighborhood_cached(self, routes):
        routes_key = tuple(map(tuple, routes))
        if routes_key in self.move_cache:
            return self.move_cache[routes_key]
        
        neighbors = generate_neighborhood(routes)
        self.move_cache[routes_key] = neighbors
        return neighbors
```

---

## Enhancements

### Variable Neighborhood Search (VNS)

**Idea**: Use multiple neighborhood structures

```python
def tabu_search_vns(initial_solution):
    """TS with multiple neighborhoods"""
    
    # Neighborhood 1: Relocation (default)
    # Neighborhood 2: Swap (exchange two customers)
    # Neighborhood 3: 2-opt (reverse segment)
    
    neighborhoods = [
        generate_neighborhood_relocation,
        generate_neighborhood_swap,
        generate_neighborhood_2opt
    ]
    
    current = initial_solution
    k = 0
    
    while not_converged and k < len(neighborhoods):
        # Try neighborhood k
        current, improved = apply_tabu_search(current, neighborhoods[k])
        
        if improved:
            k = 0  # Reset to first neighborhood
        else:
            k += 1  # Try next neighborhood
    
    return current
```

### Reactive Tabu Search

**Adapt tenure based on search quality**:

```python
def reactive_tabu_search(solution):
    """Automatically adjust tenure"""
    tabu_tenure = 10
    recent_improvements = []  # Track recent progress
    
    for iteration in range(max_iterations):
        # ... standard TS iteration ...
        
        if improved:
            recent_improvements.append(1)
        else:
            recent_improvements.append(0)
        
        # Adjust tenure every 50 iterations
        if iteration % 50 == 0:
            improvement_rate = sum(recent_improvements[-50:]) / 50
            
            if improvement_rate < 0.1:
                tabu_tenure += 5  # Increase exploration
            elif improvement_rate > 0.5:
                tabu_tenure -= 2  # Tighten search
            
            tabu_tenure = max(5, min(25, tabu_tenure))
```

### Restart Strategy

**Escape convergence**:
```python
def tabu_search_with_restart(initial_solution, restart_threshold=20):
    """Restart if stuck"""
    no_improve_count = 0
    best_ever = initial_solution
    
    current = initial_solution
    
    while global_iterations < limit:
        current, improved = tabu_search_iteration(current)
        
        if improved:
            no_improve_count = 0
        else:
            no_improve_count += 1
        
        if no_improve_count > restart_threshold:
            # Perturb current solution
            current = perturb_solution(best_ever, intensity=0.3)
            no_improve_count = 0
```

---

## Convergence Analysis

### Convergence Metrics

```python
def analyze_convergence(history):
    """Evaluate TS convergence"""
    improvements = np.diff(history)
    
    # Percentage improvement per iteration
    pct_improvement = -improvements / history[:-1] * 100
    
    # Iterations until no improvement
    stagnation_point = np.where(improvements == 0)[0]
    
    # Average improvement rate
    avg_improvement = np.mean(pct_improvement[pct_improvement > 0])
    
    print(f"Avg improvement: {avg_improvement:.3f}%")
    print(f"Stagnation after: {stagnation_point[0] if len(stagnation_point) > 0 else 'No stagnation'}")
```

### When to Stop

```
Continue TS if:
  ✓ Still finding improvements
  ✓ Iterations < limit
  ✓ Tabu list has diverse moves

Stop TS when:
  ✗ No valid moves (all tabu)
  ✗ Max iterations reached
  ✗ Time limit exceeded
  ✗ Converged (no improvement for N iterations)
```

---

## TS vs GA Comparison

```
Characteristic    | Tabu Search | Genetic Algorithm
Starting point    | Single sol  | Population
Exploration       | Memory-based| Random-based
Movement          | To neighbors| Recombination
Speed             | Fast        | Slower
Local optima      | Can escape  | May trap
Implementation    | Simpler     | More complex
```

---

## References

- Glover, F., & Laguna, M. (1997). Tabu Search
- Glover, F. (1990). Tabu Search: A New Approach to Optimization
- Laguna, M., & Marti, R. (2002). The Tabu Search Metaheuristic: A Survey
- Cordone, R., & Wolfer Calvo, R. (1998). On the effectiveness of Tabu Search for the CVRP

