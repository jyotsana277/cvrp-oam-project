# API Reference

Complete documentation of all classes and methods in the CVRP optimization system.

## Table of Contents
- [GeneticAlgorithm](#geneticalgorithm)
- [TabuSearch](#tabusearch)
- [HybridGATS](#hybridgats)
- [Utility Functions](#utility-functions)

---

## GeneticAlgorithm

Population-based metaheuristic for global search of CVRP solutions.

### Constructor

```python
GeneticAlgorithm(dist, demands, capacity, depot=0, num_customers=None)
```

**Parameters:**
- `dist` (ndarray): Distance matrix of shape (n, n)
  - Element [i,j] is distance between locations i and j
  - Should be symmetric (optional)
  - Used for fitness evaluation
  
- `demands` (list/array): Customer demand values
  - Length n (number of customers)
  - Integer values representing units per customer
  - Used in capacity feasibility checking
  
- `capacity` (int): Vehicle capacity constraint
  - Maximum load per vehicle
  - Used to split giant tour into feasible routes
  - Positive integer
  
- `depot` (int, default=0): Depot node index
  - Starting and ending point for all routes
  - Integer index into distance matrix
  
- `num_customers` (int, optional): Number of customers
  - If None, inferred as len(demands)
  - Excludes depot

**Returns:**
- GeneticAlgorithm instance (ready for population initialization)

**Example:**
```python
import numpy as np
from oam_project_dataset1 import GeneticAlgorithm

dist = np.random.rand(20, 20)  # 20 customers
demands = np.ones(20)
ga = GeneticAlgorithm(dist, demands, capacity=100, depot=0, num_customers=20)
```

### Methods

#### initialize_population

```python
initialize_population(pop_size) -> List[List[int]]
```

Initialize population with random permutations (giant tours).

**Parameters:**
- `pop_size` (int): Number of chromosomes to generate
  - Recommended: 30-100 depending on problem size
  - Typical: 40-50

**Returns:**
- `population` (list of lists): Each element is a chromosome (permutation of customers 1..n)
  - Shape: (pop_size, num_customers)
  - Type: List[List[int]]

**Side Effects:**
- Updates internal `self.population`
- Prints progress information

**Time Complexity:** $O(\text{pop\_size} \times n \log n)$

**Example:**
```python
population = ga.initialize_population(pop_size=50)
# population = [[3, 1, 5, 2, 4], [2, 4, 1, 3, 5], ...]  (50 permutations)
```

#### decode_chromosome

```python
decode_chromosome(chromosome) -> List[List[int]]
```

Convert giant tour into feasible routes respecting capacity.

**Parameters:**
- `chromosome` (list): Customer sequence [c1, c2, ..., cn]
  - Integer indices from 1 to num_customers
  - Order determines giant tour sequence

**Returns:**
- `routes` (list of lists): Each route contains [depot, cust1, cust2, ..., depot]
  - Format: [[0, c1, c2, 0], [0, c3, c4, 0], ...]
  - Always starts/ends with depot
  - Respects vehicle capacity

**Raises:**
- ValueError: If demand exceeds capacity (should not occur with valid chromosome)

**Time Complexity:** $O(n)$

**Example:**
```python
chromosome = [3, 1, 5, 2, 4]
routes = ga.decode_chromosome(chromosome)
# Output: [[0, 3, 1, 0], [0, 5, 2, 4, 0]]  (depending on capacity)
```

#### evaluate_fitness

```python
evaluate_fitness(chromosome) -> float
```

Calculate total distance for a chromosome (fitness score).

**Parameters:**
- `chromosome` (list): Customer sequence

**Returns:**
- `fitness` (float): Total travel distance (lower is better)
  - Sum of all distances in decoded routes
  - Includes return to depot

**Side Effects:** None (read-only)

**Time Complexity:** $O(n)$ for decoding + $O(n)$ for distance calculation = $O(n)$

**Example:**
```python
fitness = ga.evaluate_fitness([3, 1, 5, 2, 4])
# fitness = 1234.56
```

#### evaluate_population

```python
evaluate_population() -> None
```

Evaluate fitness for all individuals in current population.

**Parameters:** None

**Returns:** None

**Side Effects:**
- Updates `self.fitness_scores` with fitness value per individual
- Updates `self.best_individual` and `self.best_fitness` if improvement found
- Prints best fitness found

**Time Complexity:** $O(\text{pop\_size} \times n)$

**Example:**
```python
ga.evaluate_population()
# Prints: "Evaluating population fitness..."
# Prints: "Population evaluation complete. Best fitness: 1234.56"
```

#### roulette_wheel_selection

```python
roulette_wheel_selection() -> List[int]
```

Select parent chromosome using fitness-proportional selection.

**Parameters:** None (uses current population and fitness scores)

**Returns:**
- `selected` (list): A copy of the selected chromosome
  - Higher quality solutions have higher selection probability
  - All solutions have non-zero probability (diversity)

**Algorithm:**
1. Invert fitness values (convert minimization to maximization)
2. Normalize to probability distribution
3. Sample from distribution

**Time Complexity:** $O(\text{pop\_size})$

**Example:**
```python
parent = ga.roulette_wheel_selection()
# parent = [1, 3, 2, 5, 4]  (likely better solution)
parent2 = ga.roulette_wheel_selection()
# parent2 = [4, 2, 1, 3, 5]  (for crossover)
```

#### crossover_order_based

```python
crossover_order_based(parent1, parent2) -> List[int]
```

Create offspring using Order-Based Crossover (OBX).

**Parameters:**
- `parent1` (list): First parent chromosome
- `parent2` (list): Second parent chromosome

**Returns:**
- `child` (list): Offspring chromosome
  - Subset from parent1 at same positions
  - Remaining filled with parent2's order
  - Valid permutation (no duplicates)

**Algorithm:**
1. Select random half of parent1 positions
2. Place these genes at same positions in child
3. Fill remaining with parent2's ordering

**Time Complexity:** $O(n)$

**Example:**
```python
parent1 = [1, 2, 3, 4, 5]
parent2 = [5, 4, 3, 2, 1]
child = ga.crossover_order_based(parent1, parent2)
# child might be = [1, 2, 5, 4, 3]  (preserves parent1's structure)
```

#### mutation_swap

```python
mutation_swap(chromosome, mutation_rate=0.1) -> List[int]
```

Apply swap mutation to chromosome.

**Parameters:**
- `chromosome` (list): Chromosome to mutate
- `mutation_rate` (float, default=0.1): Mutation intensity
  - Range: [0, 1]
  - 0.1 means ~10% of cities involved in swaps
  - Typical: 0.05-0.15

**Returns:**
- `mutated` (list): Mutated copy of chromosome
  - Original unchanged

**Algorithm:**
1. Calculate number of swaps: $\text{max}(1, \lfloor n \times \text{mutation\_rate} \rfloor)$
2. Randomly select pairs of positions
3. Swap cities at selected positions

**Time Complexity:** $O(n \times \text{mutation\_rate})$

**Example:**
```python
original = [1, 2, 3, 4, 5]
mutated = ga.mutation_swap(original, mutation_rate=0.2)
# mutated might be = [3, 2, 1, 4, 5]  (cities 1 and 3 swapped)
```

#### evolve

```python
evolve(pop_size, generations, crossover_rate=0.8, mutation_rate=0.1, 
       elite_size=2) -> Tuple[List[int], List[float]]
```

Run genetic algorithm for specified generations.

**Parameters:**
- `pop_size` (int): Population size
- `generations` (int): Number of generations to evolve
- `crossover_rate` (float, default=0.8): Probability of crossover operation
  - Range: [0, 1]
  - 1.0 = always crossover
  
- `mutation_rate` (float, default=0.1): Mutation probability per city
  - Range: [0, 1]
  
- `elite_size` (int, default=2): Number of best individuals to preserve
  - Recommended: 1-5
  - Ensures monotonic improvement

**Returns:**
- `best_individual` (list): Best chromosome found
  - Represents best giant tour discovered
  
- `fitness_history` (list of floats): Best fitness per generation
  - Length = generations + 1 (includes initial evaluation)
  - Useful for convergence analysis

**Side Effects:**
- Updates `self.population`
- Updates `self.fitness_scores`
- Updates `self.best_individual` and `self.best_fitness`
- Prints generation-by-generation progress

**Time Complexity:** $O(\text{generations} \times (\text{pop\_size} \times n + k))$
- Where k is crossover/mutation operations

**Example:**
```python
best_chrom, history = ga.evolve(
    pop_size=40,
    generations=20,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=2
)

import matplotlib.pyplot as plt
plt.plot(history)
plt.xlabel('Generation')
plt.ylabel('Distance')
plt.title('GA Convergence')
plt.show()
```

#### get_best_routes

```python
get_best_routes() -> List[List[int]]
```

Get decoded routes of best individual found so far.

**Parameters:** None

**Returns:**
- `routes` (list of lists): Routes in format [[0, c1, c2, 0], [0, c3, 0], ...]
  - Each route: [depot, customer1, customer2, ..., depot]
  - Compatible with Tabu Search input

**Example:**
```python
routes = ga.get_best_routes()
for i, route in enumerate(routes):
    print(f"Route {i+1}: {route}")
```

---

## TabuSearch

Local search refinement using tabu memory and aspiration criteria.

### Constructor

```python
TabuSearch(dist, demands, capacity, depot=0)
```

**Parameters:**
- `dist` (ndarray): Distance matrix
- `demands` (list/array): Customer demands
- `capacity` (int): Vehicle capacity
- `depot` (int, default=0): Depot index

**Example:**
```python
ts = TabuSearch(dist_matrix, demands, capacity=1000, depot=0)
```

### Methods

#### generate_neighborhood

```python
generate_neighborhood(routes) -> List[Tuple[List[List[int]], Tuple]]
```

Generate all feasible relocations of customers between routes.

**Parameters:**
- `routes` (list of lists): Current routes
  - Format: [[0, c1, c2, 0], ...]

**Returns:**
- `neighbors` (list of tuples): Each element is (new_routes, move)
  - `new_routes`: Resulting routes after move
  - `move`: (from_route_idx, cust_idx, to_route_idx, insert_pos)
  - Only includes feasible moves (respecting capacity)

**Neighborhood Size:** Up to $O(r^2 \times n)$ neighbors
- r = number of routes
- n = customers per route

**Time Complexity:** $O(r^2 \times n^2)$ for full generation and validation

**Example:**
```python
neighbors = ts.generate_neighborhood(routes)
print(f"Generated {len(neighbors)} neighbors")
# neighbors = [(newRoutes1, move1), (newRoutes2, move2), ...]
```

#### calculate_routes_distance

```python
calculate_routes_distance(routes) -> float
```

Compute total distance of solution.

**Parameters:**
- `routes` (list of lists): Routes to evaluate

**Returns:**
- `total_distance` (float): Sum of all route distances
  - Includes return to depot
  - Read-only operation

**Time Complexity:** $O(r \times c)$ where r=routes, c=customers per route

**Example:**
```python
distance = ts.calculate_routes_distance(routes)
print(f"Total distance: {distance:.2f}")
```

#### is_route_feasible

```python
is_route_feasible(route) -> bool
```

Check if route respects vehicle capacity constraint.

**Parameters:**
- `route` (list): Single route [0, c1, c2, ..., 0]

**Returns:**
- `feasible` (bool): True if load ≤ capacity

**Time Complexity:** $O(n)$ where n = customers in route

**Example:**
```python
feasible = ts.is_route_feasible([0, 1, 2, 3, 0])
if not feasible:
    print("Route exceeds capacity!")
```

#### refine_solution

```python
refine_solution(routes, iterations=20, verbose=True) -> Tuple[List[List[int]], float]
```

Apply Tabu Search refinement to improve solution.

**Parameters:**
- `routes` (list of lists): Initial routes to refine
  - Format: [[0, c1, c2, 0], ...]
  
- `iterations` (int, default=20): Maximum TS iterations
  - Stops early if no valid moves available
  - Typical: 10-30 iterations
  
- `verbose` (bool, default=True): Print iteration progress
  - False for silent operation

**Returns:**
- `best_routes` (list of lists): Best routes found
  - Same format as input
  
- `best_distance` (float): Best distance achieved
  - May be better than initial

**Side Effects:**
- Clears internal `self.tabu_list`
- Prints progress if verbose=True

**Time Complexity:** $O(\text{iterations} \times \text{neighborhood\_size})$

**Example:**
```python
refined_routes, refined_distance = ts.refine_solution(
    routes, 
    iterations=15,
    verbose=False
)

print(f"Improved distance: {refined_distance:.2f}")
```

---

## HybridGATS

Complete hybrid pipeline integrating GA with TS refinement.

### Constructor

```python
HybridGATS(dist, demands, capacity, depot=0, num_customers=None)
```

**Parameters:** Same as GeneticAlgorithm

**Example:**
```python
hybrid = HybridGATS(
    dist=dist_matrix,
    demands=demands,
    capacity=1000,
    depot=0,
    num_customers=20
)
```

### Methods

#### run

```python
run(ga_pop_size=50, ga_generations=30, ts_iterations=15,
    crossover_rate=0.8, mutation_rate=0.1, elite_size=2) 
    -> Tuple[List[List[int]], float, Dict]
```

Execute hybrid GA + TS optimization.

**Parameters:**
- `ga_pop_size` (int, default=50): GA population size
  - Recommended: 30-100
  
- `ga_generations` (int, default=30): Number of GA generations
  - Recommended: 10-100
  
- `ts_iterations` (int, default=15): TS iterations per GA generation
  - Applied to best GA individual each generation
  - Recommended: 10-30
  
- `crossover_rate` (float, default=0.8): GA crossover probability
  - Recommended: 0.7-0.9
  
- `mutation_rate` (float, default=0.1): GA mutation rate
  - Recommended: 0.05-0.15
  
- `elite_size` (int, default=2): Elite individuals preserved
  - Recommended: 1-5

**Returns:**
- `best_solution` (list of lists): Best routes found
  - Format: [[0, c1, c2, 0], ...]
  
- `best_distance` (float): Best distance achieved
  
- `history` (dict): Convergence tracking
  - Keys: 'gen', 'ga_best', 'ts_best', 'overall_best'
  - Useful for analysis and visualization

**Side Effects:**
- Prints detailed progress for each generation
- Updates internal tracking structures

**Time Complexity:** $O(\text{ga\_generations} \times (\text{ga\_pop\_size} \times n + \text{ts\_iterations} \times r^2 \times n))$

**Example:**
```python
best_routes, best_dist, hist = hybrid.run(
    ga_pop_size=50,
    ga_generations=20,
    ts_iterations=15,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=2
)

print(f"Best distance: {best_dist:.2f}")
print(f"Routes found: {len(best_routes)}")
```

#### plot_convergence

```python
plot_convergence() -> None
```

Visualize convergence curves (GA, TS, overall best).

**Parameters:** None

**Returns:** None (displays matplotlib figure)

**Side Effects:**
- Creates matplotlib figure
- Displays plot (blocks execution until closed)

**Example:**
```python
hybrid.plot_convergence()
# Shows graph with three curves:
# - GA Best (blue with circles)
# - TS Refined (green with squares)
# - Overall Best (red with triangles)
```

#### print_solution_summary

```python
print_solution_summary() -> None
```

Print detailed summary of best solution found.

**Parameters:** None

**Returns:** None (prints to stdout)

**Output Format:**
```
=== FINAL SOLUTION SUMMARY ===
Total Distance: 1234.56
Number of Routes: 5
Number of Customers: 20

Route 1:
  Path: [0, 3, 5, 2, 0]
  Customers: [3, 5, 2]
  Load: 150/1000
  Distance: 234.56

...

Total Load: 950
==============================
```

**Example:**
```python
hybrid.print_solution_summary()
```

---

## Utility Functions

### load_mdrp_format

```python
load_mdrp_format(path="19MDVRP Problem Sets.xlsx", sheet="Problem 7") 
    -> Tuple[ndarray, ndarray, ndarray]
```

Load CVRP data from MDRP format Excel file.

**Parameters:**
- `path` (str): Path to Excel file
- `sheet` (str): Sheet name containing problem data

**Returns:**
- `depots` (ndarray): Depot coordinates shape (d, 2)
  - Columns: [x, y]
  
- `coords` (ndarray): Customer coordinates shape (n, 2)
  - Columns: [x, y]
  
- `demands` (ndarray): Customer demands shape (n,)
  - Generated as ones (unit demand)

**Raises:**
- FileNotFoundError: If file doesn't exist
- KeyError: If sheet not found
- ValueError: If required columns missing

**Example:**
```python
depots, customers, demands = load_mdrp_format(
    "19MDVRP Problem Sets.xlsx", 
    sheet="Problem 7"
)

print(f"Depots: {depots.shape}")
print(f"Customers: {customers.shape}")
print(f"Demands: {demands.shape}")
```

### compute_distance_matrix

```python
compute_distance_matrix(coords) -> ndarray
```

Compute Euclidean distance matrix from coordinates.

**Parameters:**
- `coords` (ndarray): Coordinates shape (n, 2)
  - Rows: locations
  - Columns: [x, y]

**Returns:**
- `dist` (ndarray): Distance matrix shape (n, n)
  - Element [i,j] = Euclidean distance between i and j
  - Symmetric: dist[i,j] = dist[j,i]
  - Diagonal zeros: dist[i,i] = 0

**Time Complexity:** $O(n^2)$

**Example:**
```python
dist_matrix = compute_distance_matrix(customer_coords)
print(f"Distance matrix shape: {dist_matrix.shape}")
print(f"Distance 0→1: {dist_matrix[0, 1]:.2f}")
```

### check_solution_feasibility

```python
check_solution_feasibility(solution, demands, capacity) -> bool
```

Verify all routes respect vehicle capacity.

**Parameters:**
- `solution` (list of lists): Routes to check
- `demands` (list): Customer demands
- `capacity` (int): Vehicle capacity

**Returns:**
- `feasible` (bool): True if all routes valid

**Example:**
```python
if check_solution_feasibility(routes, demands, 1000):
    print("Solution is feasible!")
else:
    print("Solution violates capacity constraints!")
```

### total_solution_distance

```python
total_solution_distance(solution, dist) -> float
```

Calculate total distance of complete solution.

**Parameters:**
- `solution` (list of lists): Routes
- `dist` (ndarray): Distance matrix

**Returns:**
- `total` (float): Sum of all distances

**Example:**
```python
total_dist = total_solution_distance(routes, dist_matrix)
```

---

## Complete Example

```python
import numpy as np
import pandas as pd
from math import sqrt

# ============================================
# LOAD DATA
# ============================================
depots, coords, demands = load_mdrp_format(
    "19MDVRP Problem Sets.xlsx", 
    sheet="Problem 7"
)

# Compute distance matrix
dist_matrix = compute_distance_matrix(coords)

# ============================================
# RUN HYBRID ALGORITHM
# ============================================
hybrid = HybridGATS(
    dist=dist_matrix,
    demands=demands,
    capacity=1000,
    depot=0,
    num_customers=len(coords)
)

best_routes, best_distance, history = hybrid.run(
    ga_pop_size=50,
    ga_generations=20,
    ts_iterations=15,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=2
)

# ============================================
# ANALYZE RESULTS
# ============================================
hybrid.print_solution_summary()
hybrid.plot_convergence()

# Check feasibility
feasible = check_solution_feasibility(best_routes, demands, 1000)
print(f"Solution feasible: {feasible}")

# Get convergence metrics
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(history['gen'], history['overall_best'], 'ro-', label='Hybrid Best')
plt.xlabel('Generation')
plt.ylabel('Distance')
plt.title('Hybrid GA+TS Convergence')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

