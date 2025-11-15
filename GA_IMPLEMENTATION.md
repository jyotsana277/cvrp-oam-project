# Genetic Algorithm Implementation Guide

Deep dive into the Genetic Algorithm component of the hybrid CVRP solver.

## Table of Contents
1. [GA Overview](#ga-overview)
2. [Chromosome Representation](#chromosome-representation)
3. [Population Initialization](#population-initialization)
4. [Genetic Operators](#genetic-operators)
5. [Selection Mechanisms](#selection-mechanisms)
6. [Fitness Evaluation](#fitness-evaluation)
7. [Evolution Process](#evolution-process)
8. [Parameter Effects](#parameter-effects)
9. [Implementation Details](#implementation-details)
10. [Advanced Techniques](#advanced-techniques)

---

## GA Overview

### What is a Genetic Algorithm?

A Genetic Algorithm is a population-based metaheuristic that mimics biological evolution:
- **Population**: Set of candidate solutions (chromosomes)
- **Fitness**: Quality measure for each solution
- **Evolution**: Generations improve population through selection, crossover, mutation
- **Convergence**: Population converges toward good solutions

### Why GA for CVRP?

| Property | GA Advantage |
|----------|-------------|
| Search Space | Handles large combinatorial space |
| Local Optima | Escapes via population diversity |
| Parallelization | Natural parallelism (evaluate pop) |
| Flexibility | Easy to combine with other methods |
| Robustness | Works without problem-specific knowledge |

### GA vs Other Methods

```
Method         | Speed | Quality | Robustness | Code Complexity
GA             | Good  | Good    | High       | Medium
Random Search  | Fast  | Poor    | Medium     | Low
Greedy/Local   | Fast  | Medium  | Low        | Low
GA + Tabu      | Good  | Excellent | High    | High (our approach!)
```

---

## Chromosome Representation

### Giant Tour Encoding

**Definition**: Permutation of customer indices representing visitation order

```
Chromosome: [3, 1, 5, 2, 4, 6]
Meaning: Visit customers in order: 3 → 1 → 5 → 2 → 4 → 6
```

### Decoding Process

Convert permutation into feasible multi-route solution:

```
Algorithm: DecodeGiantTour
Input: chromosome (permutation), demands, capacity
Output: routes (list of vehicle routes)

1. Initialize: current_route = [0], current_load = 0
2. For each customer in chromosome:
   a. If (current_load + demand) > capacity:
      i. Close current_route (add depot)
      ii. Start new route
   b. Add customer to current_route
   c. Update current_load
3. Close final route with depot
4. Return all routes
```

**Example**:
```
Chromosome: [1, 3, 2, 4, 5]
Demands: {1:100, 2:150, 3:200, 4:100, 5:100}
Capacity: 300

Processing:
- Add 1: load = 100 → route = [0, 1]
- Add 3: load = 300 → route = [0, 1, 3]
- Add 2: load = 450 > 300 → close [0, 1, 3, 0], start new
- Add 2: load = 150 → route = [0, 2]
- Add 4: load = 250 → route = [0, 2, 4]
- Add 5: load = 350 > 300 → close [0, 2, 4, 0], start new
- Add 5: load = 100 → route = [0, 5]

Result: 
  Route 1: [0, 1, 3, 0]
  Route 2: [0, 2, 4, 0]
  Route 3: [0, 5, 0]
```

### Advantages of Giant Tour

✓ **Simple**: Linear permutation representation  
✓ **Compact**: One chromosome = entire solution  
✓ **Valid**: Decoding always produces feasible routes  
✓ **Compatible**: Works with standard GA operators  

### Limitations

✗ **Redundancy**: Multiple chromosomes → same routes  
✗ **Non-locality**: Swapping distant cities has similar cost  

---

## Population Initialization

### Random Initialization

**Algorithm**:
```
For i = 1 to population_size:
  1. Create list of customer indices: [1, 2, ..., n]
  2. Randomly shuffle the list
  3. Add to population
```

**Code Example**:
```python
def initialize_population(pop_size, num_customers):
    population = []
    for _ in range(pop_size):
        customers = list(range(1, num_customers + 1))
        random.shuffle(customers)
        population.append(customers)
    return population
```

### Population Diversity

**Measure**: How different are individuals?

```python
def calculate_diversity(population):
    """Measure population diversity (0=identical, high=diverse)"""
    total_distance = 0
    for i in range(len(population)-1):
        for j in range(i+1, len(population)):
            # Hamming distance (number of differing positions)
            dist = sum(1 for a, b in zip(population[i], population[j]) if a != b)
            total_distance += dist
    return total_distance / (len(population) * (len(population)-1) / 2)

# High diversity (good) if > 50% of positions differ
```

### Initial Diversity Effects

| Diversity | Convergence | Quality | Notes |
|-----------|-------------|---------|-------|
| Low | Fast | Poor | May converge prematurely |
| Medium | Balanced | Good | **Recommended** |
| High | Slow | Good | Takes longer to converge |

---

## Genetic Operators

### 1. Crossover: Order-Based (OBX)

**Purpose**: Create offspring combining parent traits

**Algorithm**:
```
OrderBasedCrossover(parent1, parent2):
  1. Select random subset S from parent1 (typically 50%)
  2. Place S at same positions in child
  3. Fill remaining positions with parent2's order
  4. Result: valid permutation inheriting from both parents
```

**Visual Example**:
```
Parent1: [1, 2, 3, 4, 5]
Parent2: [5, 4, 3, 2, 1]

Subset S from parent1 (50%): positions 1,3 → genes {2, 4}

Child construction:
  - Position 1: 2 (from parent1)
  - Position 3: 4 (from parent1)
  - Remaining: fill with parent2 order [5, 3, 1]
  
Child: [2, 5, 4, 3, 1]
```

**Characteristics**:
- ✓ Preserves relative order
- ✓ Creates valid permutations
- ✓ Reduces invalid crossover products
- ✓ Works well for TSP-like problems

**Pseudo-code**:
```python
def crossover_order_based(parent1, parent2):
    n = len(parent1)
    subset_size = n // 2
    subset_indices = sorted(random.sample(range(n), subset_size))
    subset = {parent1[i] for i in subset_indices}
    
    child = [None] * n
    for idx in subset_indices:
        child[idx] = parent1[idx]
    
    fill_pos = 0
    for gene in parent2:
        if gene not in subset:
            while fill_pos < n and child[fill_pos] is not None:
                fill_pos += 1
            if fill_pos < n:
                child[fill_pos] = gene
    
    return child
```

### 2. Mutation: Swap Mutation

**Purpose**: Introduce diversity, escape local optima

**Algorithm**:
```
SwapMutation(chromosome, mutation_rate):
  1. Calculate swaps = max(1, chromosome_length × mutation_rate)
  2. For each swap:
     a. Select two random positions
     b. Swap cities at those positions
  3. Return mutated chromosome
```

**Example**:
```
Original: [1, 2, 3, 4, 5]
Mutation rate: 0.2 → ~1 swap
Swap positions 1 and 4: [1, 5, 3, 4, 2]
```

**Mutation Rate Effects**:

| Rate | Impact | Convergence |
|------|--------|------------|
| 0.02 | Minimal | Fast (risky) |
| 0.05 | Light | Fast-Medium |
| **0.10** | **Balanced** | **Medium (recommended)** |
| 0.15 | Moderate | Medium-Slow |
| 0.30 | Heavy | Very Slow |

**Pseudo-code**:
```python
def mutation_swap(chromosome, mutation_rate=0.1):
    mutated = chromosome.copy()
    n = len(mutated)
    num_swaps = max(1, int(n * mutation_rate))
    
    for _ in range(num_swaps):
        i, j = random.sample(range(n), 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
    
    return mutated
```

---

## Selection Mechanisms

### Roulette Wheel Selection

**Concept**: Selection probability proportional to fitness (inverse for minimization)

**Algorithm**:
```
RouletteWheelSelection(population, fitness_scores):
  1. Find max and min fitness
  2. Invert fitness: inverted[i] = max_fitness - fitness[i] + 1
  3. Normalize: probability[i] = inverted[i] / sum(inverted)
  4. Sample using cumulative distribution
  5. Return selected chromosome
```

**Why Inverse for Minimization?**
- GA typically maximizes fitness
- CVRP minimizes distance
- Invert: worse distance (larger) → lower probability

**Example**:
```
Fitness (distances): [1500, 1300, 1800, 1200]
Max = 1800, Min = 1200

Inverted: [300, 500, 0, 600]
Sum = 1400

Probabilities:
  1500 dist: 300/1400 = 21%
  1300 dist: 500/1400 = 36%
  1800 dist:   0/1400 =  0% (worst, never selected)
  1200 dist: 600/1400 = 43% (best, highest probability)
```

**Pseudo-code**:
```python
def roulette_wheel_selection(population, fitness_scores):
    max_fit = max(fitness_scores)
    min_fit = min(fitness_scores)
    
    if max_fit == min_fit:
        return random.choice(population)
    
    inverted = [max_fit - f + 1 for f in fitness_scores]
    total = sum(inverted)
    probabilities = [f / total for f in inverted]
    
    selected_idx = np.random.choice(len(population), p=probabilities)
    return population[selected_idx].copy()
```

### Alternative: Tournament Selection

```python
def tournament_selection(population, fitness_scores, tournament_size=3):
    """Select best from random subset"""
    indices = random.sample(range(len(population)), tournament_size)
    best_idx = min(indices, key=lambda i: fitness_scores[i])
    return population[best_idx].copy()
```

---

## Fitness Evaluation

### Fitness Function

**Definition**: How good is a solution?

**CVRP Fitness**:
```
Fitness = Total Distance
        = Sum of all route distances
        = Sum of all consecutive city distances + return to depot
        
Minimize Fitness
```

**Calculation**:
```
Algorithm: EvaluateFitness
Input: chromosome
Output: fitness (total distance)

1. Decode chromosome into routes
2. For each route:
   a. Sum distances between consecutive cities
   b. Include return to depot
3. Sum all route distances
4. Return total
```

**Example**:
```
Routes: [[0, 1, 3, 0], [0, 2, 4, 0]]

Distances (from distance matrix):
  Route 1: d(0,1) + d(1,3) + d(3,0) = 10 + 8 + 10 = 28
  Route 2: d(0,2) + d(2,4) + d(4,0) = 12 + 9 + 12 = 33

Total Fitness = 28 + 33 = 61
```

### Fitness Caching (Optimization)

```python
class GAWithCache:
    def __init__(self, ...):
        self.fitness_cache = {}  # chromosome_hash → fitness
    
    def evaluate_fitness(self, chromosome):
        key = tuple(chromosome)
        if key not in self.fitness_cache:
            # Compute fitness
            fitness = calculate_total_distance(chromosome)
            self.fitness_cache[key] = fitness
        return self.fitness_cache[key]
```

---

## Evolution Process

### Complete Generation Loop

```
Algorithm: EvolutiveGA
Input: pop_size, generations, crossover_rate, mutation_rate, elite_size
Output: best_individual, fitness_history

1. Initialize random population
2. Evaluate fitness for all individuals
3. Track best_individual and best_fitness

FOR each generation g = 1 to num_generations:
  4a. Sort population by fitness
  4b. Select elite_size best individuals
  4c. Create new_population with elite
  
  4d. WHILE len(new_population) < pop_size:
      i.   Select parent1 via roulette wheel
      ii.  Select parent2 via roulette wheel
      iii. WITH probability crossover_rate:
           child = OrderBasedCrossover(parent1, parent2)
           ELSE:
           child = parent1.copy()
      iv.  child = SwapMutation(child, mutation_rate)
      v.   Add child to new_population
  
  4e. Replace population with new_population
  4f. Evaluate fitness for new population
  4g. Update best_individual if improvement found
  4h. Record fitness in history

5. Return best_individual, fitness_history
```

### Pseudo-code Implementation

```python
def evolve_ga(pop_size, generations, crossover_rate, mutation_rate, elite_size):
    # Initialize
    population = initialize_population(pop_size)
    fitness_scores = [evaluate_fitness(ind) for ind in population]
    best_ind = population[np.argmin(fitness_scores)]
    best_fit = min(fitness_scores)
    history = [best_fit]
    
    # Evolution loop
    for gen in range(generations):
        # Preserve elite
        sorted_idx = sorted(range(len(fitness_scores)), 
                          key=lambda i: fitness_scores[i])
        elite_idx = sorted_idx[:elite_size]
        new_pop = [population[i].copy() for i in elite_idx]
        
        # Create offspring
        while len(new_pop) < pop_size:
            parent1 = roulette_wheel_select(population, fitness_scores)
            parent2 = roulette_wheel_select(population, fitness_scores)
            
            if random.random() < crossover_rate:
                child = crossover_order_based(parent1, parent2)
            else:
                child = parent1.copy()
            
            child = mutation_swap(child, mutation_rate)
            new_pop.append(child)
        
        # Evaluate new population
        population = new_pop[:pop_size]
        fitness_scores = [evaluate_fitness(ind) for ind in population]
        
        # Update best
        current_best_idx = np.argmin(fitness_scores)
        if fitness_scores[current_best_idx] < best_fit:
            best_ind = population[current_best_idx].copy()
            best_fit = fitness_scores[current_best_idx]
        
        history.append(best_fit)
    
    return best_ind, history
```

---

## Parameter Effects

### Population Size (pop_size)

**Definition**: Number of solutions in each generation

```
Small (10-20):  Fast but risky convergence
Medium (40-60): Balanced (recommended)
Large (100+):   Slow but robust
```

**Effect on Convergence**:
```
                Best Found
                    ↑
Large pop      |     ╱╲
               |    ╱  ╲___
Medium pop     |   ╱╲___
               |  ╱
Small pop      | ╱___________
               └────────────── Generation
```

### Generations (num_generations)

**Definition**: Number of evolution iterations

```
Too Few (< 5):      Incomplete search, poor quality
Adequate (10-30):   Good balance
Many (50+):         Diminishing returns, slow
```

**Convergence Pattern**:
```
Distance
    ↑
   1500 |●
        | ●
   1400 |  ●●
        |    ●  ●
   1300 |      ●  ● ●
        |           ●   ●
   1200 |_________●_●_●_● (plateau)
        └────────────────→ Generation
        0  5  10  15  20
```

### Crossover Rate (crossover_rate)

**Definition**: Probability of crossover vs. copy

```
0.0 (No crossover):   Parents copied, only mutation
0.5 (50%):            Balanced mixing
0.8 (80%):            Heavy mixing (recommended)
1.0 (Always):         Always crossover, never pure copies
```

**Effects**:
```
crossover_rate = 0.8 (recommended):
  - Good genetic mixing
  - Avoids premature convergence
  - Maintains diversity

crossover_rate = 0.5:
  - Less mixing
  - May converge faster
  - Risk of local optima

crossover_rate = 1.0:
  - All children from crossover
  - No pure copies
  - Can lose best solutions
```

### Mutation Rate (mutation_rate)

**Definition**: Intensity of mutation (swaps per chromosome)

```
mutation_rate = 0.1  (recommended)
  → ~10% of cities participate in swaps
  → ~1 swap for 10-city problem

mutation_rate = 0.05 (low):
  - Less disruption
  - Keeps good solutions
  - Risk: premature convergence

mutation_rate = 0.20 (high):
  - More exploration
  - Can escape local optima
  - Risk: disrupts good solutions
```

### Elite Size (elite_size)

**Definition**: Number of best solutions to preserve

```
elite_size = 0:   No preservation (risky)
elite_size = 1-3: Standard (recommended)
elite_size = 5+:  Very conservative
```

**Effect**: Ensures monotonic improvement (best never worsens)

---

## Implementation Details

### GeneticAlgorithm Class Structure

```python
class GeneticAlgorithm:
    def __init__(self, dist, demands, capacity, depot=0, num_customers=None):
        self.dist = dist                    # Distance matrix
        self.demands = demands              # Customer demands
        self.capacity = capacity            # Vehicle capacity
        self.population = []                # Current population
        self.fitness_scores = []            # Fitness of each individual
        self.best_individual = None         # Best found so far
        self.best_fitness = float('inf')    # Best fitness found
    
    def initialize_population(self, pop_size):
        """Generate random population"""
        pass
    
    def decode_chromosome(self, chromosome):
        """Convert permutation to routes"""
        pass
    
    def evaluate_fitness(self, chromosome):
        """Calculate total distance"""
        pass
    
    def evaluate_population(self):
        """Evaluate all individuals"""
        pass
    
    def roulette_wheel_selection(self):
        """Select one parent"""
        pass
    
    def crossover_order_based(self, parent1, parent2):
        """Create offspring"""
        pass
    
    def mutation_swap(self, chromosome, mutation_rate=0.1):
        """Apply mutation"""
        pass
    
    def evolve(self, pop_size, generations, ...):
        """Run full GA"""
        pass
    
    def get_best_routes(self):
        """Return decoded best solution"""
        pass
```

---

## Advanced Techniques

### Adaptive Mutation Rate

Increase mutation as population converges:

```python
def adaptive_mutation_rate(generation, total_generations, base_rate=0.1):
    """Increase mutation rate in later generations"""
    progress = generation / total_generations
    adaptive_rate = base_rate * (1 + progress)  # Up to 2x base rate
    return adaptive_rate
```

### Diversity Maintenance

```python
def maintain_diversity(population, fitness_scores, diversity_threshold=0.3):
    """Replace similar individuals with random ones"""
    diversity = calculate_population_diversity(population)
    
    if diversity < diversity_threshold:
        # Population too similar
        # Replace worst 20% with random individuals
        num_replace = len(population) // 5
        worst_indices = sorted(range(len(fitness_scores)),
                             key=lambda i: fitness_scores[i],
                             reverse=True)[:num_replace]
        
        for idx in worst_indices:
            population[idx] = generate_random_chromosome()
```

### Niching (Maintaining Multiple Species)

```python
def niching_ga(pop_size, generations):
    """Keep diverse subpopulations (species)"""
    population = initialize_population(pop_size)
    
    for gen in range(generations):
        # Cluster population into niches
        niches = cluster_population(population, k=3)
        
        # Evolve within and between niches
        for niche in niches:
            # Evolve within niche
            new_niche = evolve_subpopulation(niche)
            # Migrate between niches
```

### Hybrid with Local Search (Our Approach!)

```python
def hybrid_ga_with_tabu(pop_size, generations, ts_iterations):
    """GA with TS refinement"""
    population = initialize_population(pop_size)
    
    for gen in range(generations):
        # Standard GA evolution
        new_population = evolve_one_generation(population, pop_size)
        
        # Apply local search (Tabu) on best
        best_ind = new_population[np.argmin(fitness_scores)]
        best_routes = decode(best_ind)
        
        # Refine with Tabu Search
        refined_routes = tabu_search(best_routes, ts_iterations)
        
        # Update best if improved
        if fitness(refined_routes) < fitness(best_routes):
            best_ind = refined_routes
            population = updated_with_refined_best(new_population, refined_routes)
```

---

## Performance Optimization

### Vectorization with NumPy

```python
def vectorized_distance_matrix_computation(coords):
    """Faster distance matrix using NumPy"""
    from scipy.spatial.distance import cdist
    return cdist(coords, coords, metric='euclidean')
```

### Parallel Population Evaluation

```python
from multiprocessing import Pool

def parallel_evaluate_population(population, num_workers=4):
    """Evaluate fitness in parallel"""
    with Pool(num_workers) as pool:
        fitness_scores = pool.map(evaluate_fitness, population)
    return fitness_scores
```

---

## When to Use GA

**Good for CVRP because:**
- ✓ Handles large search spaces (n! permutations)
- ✓ Can find near-optimal solutions reasonably fast
- ✓ Works without problem-specific knowledge
- ✓ Combines well with local search (our hybrid!)

**Limitations:**
- ✗ Not guaranteed optimal solution
- ✗ Convergence hard to predict
- ✗ Many parameters to tune
- ✗ Slower than greedy heuristics for small problems

---

## References

- Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning
- Davis, L. (1991). Handbook of Genetic Algorithms
- Back, T. (1996). Evolutionary Algorithms in Theory and Practice
- Michalewicz, Z. (1996). Genetic Algorithms + Data Structures = Evolution Programs

