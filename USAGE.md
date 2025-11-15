# Usage Guide & Examples

Complete guide to using the CVRP Hybrid GA+TS optimization system with practical examples.

## Table of Contents
1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Dataset Loading](#dataset-loading)
4. [Configuring Parameters](#configuring-parameters)
5. [Running Optimization](#running-optimization)
6. [Analyzing Results](#analyzing-results)
7. [Advanced Scenarios](#advanced-scenarios)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements
```
Python 3.7+
numpy
pandas
openpyxl
matplotlib
```

### Setup

```bash
# Clone repository
git clone https://github.com/jyotsana277/cvrp-oam-project.git
cd cvrp-oam-project

# Install dependencies
pip install numpy pandas openpyxl matplotlib

# Verify installation
python -c "import numpy, pandas; print('Ready!')"
```

### Jupyter Notebook

```bash
# Install Jupyter
pip install jupyter

# Launch notebook
jupyter notebook oam_project_dataset1.ipynb
```

---

## Basic Usage

### Minimal Example

The simplest way to run optimization:

```python
# 1. Import required modules
from oam_project_dataset1 import HybridGATS, load_mdrp_format, compute_distance_matrix

# 2. Load data
depots, coords, demands = load_mdrp_format(
    "19MDVRP Problem Sets.xlsx", 
    sheet="Problem 7"
)
dist_matrix = compute_distance_matrix(coords)

# 3. Initialize and run
hybrid = HybridGATS(
    dist=dist_matrix,
    demands=demands,
    capacity=1000,
    num_customers=len(coords)
)

best_routes, best_distance, history = hybrid.run(
    ga_pop_size=40,
    ga_generations=15,
    ts_iterations=10
)

# 4. Print results
print(f"Best distance: {best_distance:.2f}")
print(f"Number of routes: {len(best_routes)}")
```

**Output:**
```
==== HYBRID GA + TS PIPELINE ====
Running optimization...

--- Generation 1/15 ---
GA Best: 1500.45
TS Best: 1490.23
✓ NEW OVERALL BEST: 1490.23

[...more generations...]

FINAL SOLUTION SUMMARY
Total Distance: 1245.67
Number of Routes: 5
Routes: [[0, 1, 4, 7, 0], ...]
```

---

## Dataset Loading

### Load from Excel (MDRP Format)

```python
from oam_project_dataset1 import load_mdrp_format, compute_distance_matrix

# Load Problem 7
depots, customers, demands = load_mdrp_format(
    "19MDVRP Problem Sets.xlsx",
    sheet="Problem 7"
)

print(f"Loaded {len(customers)} customers")
print(f"Loaded {len(depots)} depot(s)")
print(f"Sample customer: {customers[0]}")  # [x, y]
print(f"Sample demand: {demands[0]}")      # 1.0
```

### Create Custom Dataset

```python
import numpy as np

# Define custom problem
num_customers = 30
num_depots = 1

# Random coordinates (0-100)
depot_coords = np.array([[50, 50]])  # Single depot at center
customer_coords = np.random.rand(num_customers, 2) * 100

# Stack coordinates (depot first)
all_coords = np.vstack([depot_coords, customer_coords])

# Create demands (random 1-10)
demands = np.random.randint(1, 11, num_customers)

# Compute distance matrix
from oam_project_dataset1 import compute_distance_matrix
dist_matrix = compute_distance_matrix(all_coords)

print(f"Custom problem created:")
print(f"  Locations: {all_coords.shape[0]}")
print(f"  Customers: {num_customers}")
print(f"  Distance matrix: {dist_matrix.shape}")
```

### Load from CSV

```python
import numpy as np
import pandas as pd

# Load customer data
df = pd.read_csv("customers.csv")  # Columns: x, y, demand
customers = df[['x', 'y']].values
demands = df['demand'].values

# Load or define depot
depot = np.array([[0, 0]])  # Depot at origin

# Combine all coordinates
all_coords = np.vstack([depot, customers])

# Compute distance matrix
dist_matrix = compute_distance_matrix(all_coords)
```

---

## Configuring Parameters

### Understanding Parameters

Each algorithm component has tuning parameters:

```python
hybrid.run(
    # GA Parameters
    ga_pop_size=50,        # Population size
    ga_generations=30,     # Evolution iterations
    
    # TS Parameters
    ts_iterations=15,      # TS refinement iterations
    
    # GA Operators
    crossover_rate=0.8,    # Crossover probability
    mutation_rate=0.1,     # Mutation intensity
    
    # Selection
    elite_size=2           # Elite preservation
)
```

### Quick Size Classification

Choose configuration based on problem size:

#### Small Problems (n < 50 customers)

```python
hybrid.run(
    ga_pop_size=30,
    ga_generations=20,
    ts_iterations=15,
    crossover_rate=0.85,
    mutation_rate=0.15,
    elite_size=1
)
# Typical runtime: < 1 minute
# Memory usage: Low
```

**Good for:**
- Quick testing
- Parameter exploration
- Proof of concept

#### Medium Problems (50-100 customers)

```python
hybrid.run(
    ga_pop_size=50,
    ga_generations=30,
    ts_iterations=20,
    crossover_rate=0.80,
    mutation_rate=0.10,
    elite_size=2
)
# Typical runtime: 5-15 minutes
# Memory usage: Moderate
```

**Good for:**
- Standard CVRP benchmarks
- Production deployments
- Balance of quality and speed

#### Large Problems (n > 100 customers)

```python
hybrid.run(
    ga_pop_size=80,
    ga_generations=50,
    ts_iterations=25,
    crossover_rate=0.75,
    mutation_rate=0.08,
    elite_size=3
)
# Typical runtime: 30-60 minutes
# Memory usage: High
```

**Good for:**
- Real-world instances
- High-quality solutions needed
- Research/optimization focus

### Parameter Tuning Guidelines

**Population Size (ga_pop_size)**
```
Larger:  ✓ More diversity, ✗ Slower per generation
Smaller: ✓ Faster, ✗ Risk of premature convergence

Sweet spot: 20-80 individuals
```

**Generations (ga_generations)**
```
More:    ✓ Better convergence, ✗ More runtime
Fewer:   ✓ Faster, ✗ Incomplete search

Rule of thumb: Start with 20, increase if not converged
```

**TS Iterations (ts_iterations)**
```
Higher:  ✓ Better local search, ✗ More cost per generation
Lower:   ✓ Faster, ✗ Less refinement

Typical ratio: 1/3 to 1/2 of GA generations
```

**Mutation Rate (mutation_rate)**
```
High:    ✓ More exploration, ✗ Disrupts good solutions
Low:     ✓ Exploitation, ✗ Premature convergence

Optimal: 0.05-0.15 for most problems
```

**Crossover Rate (crossover_rate)**
```
High:    ✓ Mix parent genes more, ✗ More variation
Low:     ✓ Preserve good solutions, ✗ Less mixing

Typical: 0.7-0.9
```

---

## Running Optimization

### Step-by-Step Execution

```python
# Step 1: Load data
print("Step 1: Loading data...")
from oam_project_dataset1 import HybridGATS, load_mdrp_format, compute_distance_matrix

depots, coords, demands = load_mdrp_format("19MDVRP Problem Sets.xlsx", sheet="Problem 7")
dist_matrix = compute_distance_matrix(coords)

print(f"✓ Loaded {len(coords)} customers")
print(f"✓ Distance matrix: {dist_matrix.shape}")

# Step 2: Initialize hybrid algorithm
print("\nStep 2: Initializing hybrid algorithm...")
hybrid = HybridGATS(
    dist=dist_matrix,
    demands=demands,
    capacity=1000,
    depot=0,
    num_customers=len(coords)
)

# Step 3: Configure parameters
print("\nStep 3: Configuring parameters...")
config = {
    'ga_pop_size': 40,
    'ga_generations': 20,
    'ts_iterations': 15,
    'crossover_rate': 0.8,
    'mutation_rate': 0.1,
    'elite_size': 2
}
print(f"✓ Config: {config}")

# Step 4: Run optimization
print("\nStep 4: Running optimization...")
print("(This may take a few minutes...)\n")
best_routes, best_distance, history = hybrid.run(**config)

# Step 5: Analyze results
print("\nStep 5: Results:")
print(f"✓ Best distance: {best_distance:.2f}")
print(f"✓ Number of routes: {len(best_routes)}")
print(f"✓ Convergence achieved in {len(history['gen'])} generations")
```

### Using Different GA Algorithms

You can also run components separately:

#### GA Only

```python
from oam_project_dataset1 import GeneticAlgorithm

ga = GeneticAlgorithm(dist_matrix, demands, capacity=1000)
best_chrom, ga_history = ga.evolve(
    pop_size=50,
    generations=30,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=2
)

ga_routes = ga.get_best_routes()
ga_distance = ga.evaluate_fitness(best_chrom)

print(f"GA Best: {ga_distance:.2f}")
```

#### TS Only (Refinement of Initial Solution)

```python
from oam_project_dataset1 import TabuSearch

# Create initial solution (e.g., nearest neighbor)
initial_routes = [[0, 1, 2, 3, 0], [0, 4, 5, 0]]  # Example

ts = TabuSearch(dist_matrix, demands, capacity=1000)
refined_routes, ts_distance = ts.refine_solution(
    initial_routes,
    iterations=30,
    verbose=True
)

print(f"TS Refined: {ts_distance:.2f}")
```

---

## Analyzing Results

### Basic Result Analysis

```python
# Get results from hybrid.run()
best_routes, best_distance, history = hybrid.run(...)

# 1. Print detailed summary
hybrid.print_solution_summary()

# 2. Check feasibility
from oam_project_dataset1 import check_solution_feasibility
feasible = check_solution_feasibility(best_routes, demands, 1000)
print(f"Solution feasible: {feasible}")

# 3. Analyze convergence
print("\nConvergence Analysis:")
print(f"  Initial distance: {history['ga_best'][0]:.2f}")
print(f"  Final distance: {history['overall_best'][-1]:.2f}")
print(f"  Improvement: {(history['ga_best'][0] - history['overall_best'][-1]) / history['ga_best'][0] * 100:.1f}%")

# 4. Compare GA vs TS vs Overall
import numpy as np
ga_avg = np.mean(history['ga_best'])
ts_avg = np.mean(history['ts_best'])
overall_avg = np.mean(history['overall_best'])

print(f"\nAverage Distance by Component:")
print(f"  GA: {ga_avg:.2f}")
print(f"  TS: {ts_avg:.2f}")
print(f"  Overall: {overall_avg:.2f}")
```

### Visualizing Convergence

```python
import matplotlib.pyplot as plt
import numpy as np

# Plot 1: Three convergence curves
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(history['gen'], history['ga_best'], 'o-', label='GA', linewidth=2)
plt.plot(history['gen'], history['ts_best'], 's-', label='TS Refined', linewidth=2)
plt.plot(history['gen'], history['overall_best'], '^-', label='Overall Best', linewidth=2.5)
plt.xlabel('Generation')
plt.ylabel('Distance')
plt.title('Convergence Comparison')
plt.legend()
plt.grid(True, alpha=0.3)

# Plot 2: Improvement rate
plt.subplot(1, 2, 2)
ga_improvements = np.array(history['ga_best'][:-1]) - np.array(history['ga_best'][1:])
ts_improvements = np.array(history['ts_best'][:-1]) - np.array(history['ts_best'][1:])
generations = history['gen'][1:]

plt.plot(generations, ga_improvements, 'o-', label='GA Improvement', linewidth=2)
plt.plot(generations, ts_improvements, 's-', label='TS Improvement', linewidth=2)
plt.xlabel('Generation')
plt.ylabel('Distance Improvement')
plt.title('Improvement Rate per Generation')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Or use built-in method
hybrid.plot_convergence()
```

### Exporting Results

```python
import json
import pandas as pd

# Export routes to CSV
routes_df = pd.DataFrame({
    'route_id': list(range(len(best_routes))),
    'route': [str(r) for r in best_routes],
    'num_customers': [len(r) - 2 for r in best_routes],
    'total_load': [sum(demands[c] for c in r if c != 0) for r in best_routes]
})
routes_df.to_csv('routes.csv', index=False)

# Export convergence history to CSV
history_df = pd.DataFrame(history)
history_df.to_csv('convergence.csv', index=False)

# Export solution summary to JSON
solution_summary = {
    'best_distance': float(best_distance),
    'num_routes': len(best_routes),
    'num_customers': len(coords),
    'routes': best_routes,
    'feasible': check_solution_feasibility(best_routes, demands, 1000)
}
with open('solution.json', 'w') as f:
    json.dump(solution_summary, f, indent=2)

print("Results exported!")
```

---

## Advanced Scenarios

### Multiple Runs with Different Seeds

```python
import random
import numpy as np

results = []

for run in range(5):
    # Set random seed for reproducibility
    seed = 42 + run
    random.seed(seed)
    np.random.seed(seed)
    
    print(f"\nRun {run + 1}/5 (seed={seed})...")
    
    hybrid = HybridGATS(dist_matrix, demands, capacity=1000)
    routes, distance, history = hybrid.run(
        ga_pop_size=40,
        ga_generations=20,
        ts_iterations=15
    )
    
    results.append({
        'run': run + 1,
        'seed': seed,
        'distance': distance,
        'num_routes': len(routes),
        'convergence_gen': np.argmin(history['overall_best'])
    })

# Analyze results
results_df = pd.DataFrame(results)
print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)
print(results_df.to_string(index=False))
print(f"\nBest: {results_df['distance'].min():.2f}")
print(f"Worst: {results_df['distance'].max():.2f}")
print(f"Average: {results_df['distance'].mean():.2f}")
print(f"Std Dev: {results_df['distance'].std():.2f}")
```

### Parameter Sensitivity Analysis

```python
import itertools

# Test different parameter combinations
param_grid = {
    'mutation_rate': [0.05, 0.10, 0.15],
    'crossover_rate': [0.75, 0.80, 0.85],
    'elite_size': [1, 2, 3]
}

results = []

# Generate all combinations
param_combinations = list(itertools.product(*param_grid.values()))
param_names = list(param_grid.keys())

for i, param_values in enumerate(param_combinations):
    params = dict(zip(param_names, param_values))
    
    print(f"Testing {i+1}/{len(param_combinations)}: {params}")
    
    hybrid = HybridGATS(dist_matrix, demands, capacity=1000)
    routes, distance, _ = hybrid.run(
        ga_pop_size=40,
        ga_generations=15,
        ts_iterations=10,
        **params
    )
    
    results.append({**params, 'distance': distance, 'routes': len(routes)})

# Find best parameters
results_df = pd.DataFrame(results)
best_idx = results_df['distance'].idxmin()
print(f"\nBest parameters: {results_df.iloc[best_idx].to_dict()}")

# Plot sensitivity
import matplotlib.pyplot as plt
for param in param_names:
    plt.figure()
    for value in param_grid[param]:
        mask = results_df[param] == value
        plt.plot(range(len(mask)), results_df[mask]['distance'].values, 
                label=f'{param}={value}')
    plt.xlabel('Configuration')
    plt.ylabel('Distance')
    plt.title(f'Sensitivity to {param}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

### Comparing with Baseline

```python
# Random solution (baseline)
def create_random_solution(num_customers, capacity, demands, dist):
    """Create random solution for comparison"""
    customers = list(range(1, num_customers + 1))
    random.shuffle(customers)
    
    # Decode to feasible routes
    from oam_project_dataset1 import GeneticAlgorithm
    ga = GeneticAlgorithm(dist, demands, capacity)
    routes = ga.decode_chromosome(customers)
    
    total_dist = 0
    for route in routes:
        for i in range(len(route) - 1):
            total_dist += dist[route[i], route[i+1]]
    
    return routes, total_dist

# Nearest neighbor heuristic (baseline)
def nearest_neighbor_solution(dist_matrix, demands, capacity, depot=0):
    """Create nearest neighbor solution"""
    num_customers = len(demands)
    unvisited = set(range(1, num_customers + 1))
    routes = []
    
    while unvisited:
        route = [depot]
        current_load = 0
        current_pos = depot
        
        while unvisited:
            # Find nearest unvisited customer
            nearest = min(unvisited, 
                         key=lambda c: dist_matrix[current_pos, c])
            
            if current_load + demands[nearest - 1] <= capacity:
                route.append(nearest)
                current_load += demands[nearest - 1]
                current_pos = nearest
                unvisited.remove(nearest)
            else:
                break
        
        route.append(depot)
        routes.append(route)
    
    # Calculate distance
    total = sum(sum(dist_matrix[route[i], route[i+1]] 
                   for i in range(len(route)-1)) 
               for route in routes)
    
    return routes, total

# Run benchmarks
print("Creating baseline solutions...")
random_routes, random_dist = create_random_solution(
    len(coords), 1000, demands, dist_matrix
)
nn_routes, nn_dist = nearest_neighbor_solution(
    dist_matrix, demands, 1000
)

# Run hybrid
print("Running hybrid algorithm...")
hybrid = HybridGATS(dist_matrix, demands, capacity=1000)
hybrid_routes, hybrid_dist, _ = hybrid.run(
    ga_pop_size=40, ga_generations=20, ts_iterations=15
)

# Compare
print("\n" + "="*60)
print("COMPARISON")
print("="*60)
print(f"Random Solution:      {random_dist:.2f}")
print(f"Nearest Neighbor:     {nn_dist:.2f}")
print(f"Hybrid GA+TS:         {hybrid_dist:.2f}")
print(f"\nImprovement vs NN:    {(nn_dist - hybrid_dist) / nn_dist * 100:.1f}%")
print(f"Improvement vs Rand:  {(random_dist - hybrid_dist) / random_dist * 100:.1f}%")
```

---

## Troubleshooting

### Issue: Algorithm runs slowly

**Solutions:**
```python
# 1. Reduce population or generations
hybrid.run(ga_pop_size=30, ga_generations=10, ts_iterations=5)

# 2. For large problems, use coarser TS
hybrid.run(ga_pop_size=40, ga_generations=15, ts_iterations=5)

# 3. Check your distance matrix computation
# Make sure it's not too large (n > 1000)
print(f"Problem size: {dist_matrix.shape}")
```

### Issue: Solution quality poor

**Solutions:**
```python
# 1. Increase population and generations
hybrid.run(ga_pop_size=80, ga_generations=50, ts_iterations=30)

# 2. Increase mutation rate for more exploration
hybrid.run(mutation_rate=0.15, crossover_rate=0.75)

# 3. Run multiple times and take best
best_distance = float('inf')
for i in range(5):
    _, dist, _ = hybrid.run(...)
    if dist < best_distance:
        best_distance = dist
        best_solution = _
```

### Issue: Memory error on large problems

**Solutions:**
```python
# 1. Reduce population size
hybrid.run(ga_pop_size=20, ga_generations=15)

# 2. Reduce TS neighborhood (less intensive)
hybrid.run(ts_iterations=5)

# 3. Process in batches or use smaller dataset
```

### Issue: Getting different results each run

**Solutions:**
```python
# Set random seed for reproducibility
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# Now run will be deterministic
hybrid.run(...)
```

### Issue: Routes violate capacity constraints

**Check data:**
```python
# Verify demands aren't accidentally doubled
print(f"Max demand: {demands.max()}")
print(f"Capacity: {capacity}")
print(f"Feasible: {demands.max() <= capacity}")

# If demand > capacity for single customer, adjust capacity
if demands.max() > capacity:
    print(f"Increasing capacity to {demands.max()}")
    capacity = demands.max() + 100
```

---

## Best Practices

### 1. Preprocessing
```python
# Always validate input data
assert dist_matrix.shape == (len(coords), len(coords))
assert len(demands) == len(coords) - 1  # Exclude depot
assert all(d > 0 for d in demands)
assert dist_matrix.min() >= 0
```

### 2. Parameter Setting
```python
# Start conservative, adjust if needed
config = {
    'ga_pop_size': 40,
    'ga_generations': 20,
    'ts_iterations': 15,
    'crossover_rate': 0.8,
    'mutation_rate': 0.1,
    'elite_size': 2
}

# Monitor convergence
best_routes, best_dist, history = hybrid.run(**config)
if history['overall_best'][-1] == history['overall_best'][-5]:
    print("Converged early - could increase generations")
```

### 3. Result Validation
```python
# Always verify solution quality
feasible = check_solution_feasibility(best_routes, demands, capacity)
assert feasible, "Solution is infeasible!"

# Check for edge cases
assert len(best_routes) > 0, "No routes generated!"
assert sum(len(r)-2 for r in best_routes) == len(coords), "Not all customers visited!"
```

---

## Performance Tips

| Task | Optimization |
|------|-------------|
| **Speed up** | Reduce pop_size, generations, ts_iterations |
| **Better quality** | Increase all three parameters |
| **Memory efficient** | Use smaller populations, less TS |
| **Stability** | Run multiple times, increase elite_size |
| **Reproducibility** | Set random seeds |

