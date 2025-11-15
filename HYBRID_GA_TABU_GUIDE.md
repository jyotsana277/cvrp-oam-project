# Hybrid GA + Tabu Search Integration Guide

Comprehensive guide to the hybrid approach combining Genetic Algorithm and Tabu Search.

## Table of Contents
1. [Integration Strategy](#integration-strategy)
2. [Why Hybrid?](#why-hybrid)
3. [Architecture](#architecture)
4. [Execution Flow](#execution-flow)
5. [Parameter Interaction](#parameter-interaction)
6. [Tuning Guide](#tuning-guide)
7. [Advanced Configurations](#advanced-configurations)
8. [Convergence Analysis](#convergence-analysis)
9. [Best Practices](#best-practices)
10. [Case Studies](#case-studies)

---

## Integration Strategy

### Core Philosophy

**GA explores globally, TS exploits locally**

```
Genetic Algorithm (Exploration)
  ↓
  Generates diverse solutions
  Population-based search
  Genetic operators (crossover, mutation)
  ↓
Hybrid Integration
  ↓ ← Best GA individual each generation
  ↓
Tabu Search (Exploitation)
  ↓
  Refines solution locally
  Memory-based search
  Escapes local optima
  ↓
  Improved solution (feedback to GA)
  ↓
Back to GA Evolution
```

### Synergy Benefits

**GA + TS Together:**
```
GA alone:    Finds 1500 distance (may have slack)
TS alone:    Needs good starting point (depends on init)
GA + TS:     1500 → 1350 (GA) → 1280 (TS) = 15% total improvement
```

**Key Synergies:**
1. **GA provides diverse starting points** for TS
2. **TS refines GA solutions** to local optima
3. **Refined solutions** guide GA population improvement
4. **Population diversity** maintained (TS doesn't narrow)
5. **Iterative refinement** across generations

---

## Why Hybrid?

### Problem with GA Alone

```
GA convergence curve:
Distance
    ↑
 1500 |●  (random start)
      | ╲
 1400 |  ●╲
      |   │ ●
 1350 |   │  ●
      |   │  │●
 1300 |   │  │ ● ← Converges here (local optimum)
      |   │  │
 1250 |___|__|__●_●_●_● ← Could do better
      └─────────────────→ Generation

GA stops improving but solution still has slack
```

### Problem with TS Alone

```
TS refinement curve (starting from random):
Distance
    ↑
 1800 | (random start, poor quality)
      | ╲
 1600 |  ╲●
      |    ╲
 1400 |     ●
      |      ╲
 1300 |       ●━━━● ← Quick improvement, then plateau
      |        \
 1200 |_________●_●_●
      └──────────────→ Iteration

TS works well once it has decent solution,
but starting point greatly affects final quality
```

### Combined Effect

```
Combined curve:
Distance
    ↑
 1500 |●  GA (random)
      | │╲
 1400 |G│A●╲
      |A│  │ ●╲
 1350 |E│  │ T│●╲
      |N│  │S│  ●╲
 1300 |C│  │ │   ●╲ ← TS refinement applied per generation
      | │  │ │      ●
 1250 |─┼──┼─┼───●─●─●  ← Better final result!
      └─┴──┴─┴──────────→ Generation
      
Each generation: GA evolves, then TS refines
Result: Better quality than either alone
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│           HybridGATS Controller                  │
│  Orchestrates GA-TS integration                  │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ↓                         ↓
┌─────────────┐         ┌──────────────┐
│   GA Loop   │         │ GA Population│
│  - Select   │         │   Storage    │
│  - Crossover│────────→├──────────────┤
│  - Mutate   │         │Population[]  │
│  - Evaluate │         │Fitness[]     │
└──────┬──────┘         │BestInd[]     │
       │                └──────────────┘
       │ Best Individual Each Gen
       ↓
    ┌─────────────────┐
    │  Decoder        │
    │ (chromosome→    │
    │  routes)        │
    └────────┬────────┘
             │ Routes
             ↓
    ┌─────────────────┐
    │  Tabu Search    │
    │  - Neighborhood │
    │  - Tabu List    │
    │  - Aspiration   │
    └────────┬────────┘
             │ Refined Routes
             ↓
    ┌─────────────────┐
    │ Best Tracker    │
    │- Track best     │
    │- Update history │
    │- Print progress │
    └─────────────────┘
```

### Class Hierarchy

```python
HybridGATS (Main Controller)
  ├── GeneticAlgorithm
  │   ├── population[]
  │   ├── fitness_scores[]
  │   ├── best_individual
  │   └── best_fitness
  │
  ├── TabuSearch
  │   ├── tabu_list{}
  │   ├── tabu_tenure
  │   └── best_distance
  │
  └── History Tracker
      ├── gen[]
      ├── ga_best[]
      ├── ts_best[]
      └── overall_best[]
```

---

## Execution Flow

### Main Loop

```
Algorithm: HybridGATS
Input: ga_pop_size, ga_generations, ts_iterations
       crossover_rate, mutation_rate, elite_size

1. Initialize GA population
2. Evaluate initial population
3. Set best_distance = min(population fitness)

FOR gen = 1 to ga_generations:
  4a. ===== GA PHASE =====
      - Sort population by fitness
      - Preserve elite individuals
      - Create offspring via crossover/mutation
      - Evaluate new population
      - Update best_individual from GA
  
  4b. ===== TS PHASE =====
      - Decode best GA individual → routes
      - Apply TS refinement (ts_iterations)
      - Get refined_routes and refined_distance
  
  4c. ===== TRACKING =====
      - Record GA_best[gen] = best GA fitness
      - Record TS_best[gen] = TS refined fitness
      - If TS_best < overall_best:
        Update overall_best[gen]
        Print "✓ NEW BEST"
      - Else:
        overall_best[gen] = overall_best[gen-1]
  
  4d. ===== LOGGING =====
      Print generation summary

5. Return best_solution, best_distance, history
```

### Pseudo-code

```python
def hybrid_ga_ts_run(pop_size, generations, ts_iters, 
                     crossover_rate, mutation_rate, elite_size):
    # Initialize
    ga = GeneticAlgorithm(dist, demands, capacity)
    ts = TabuSearch(dist, demands, capacity)
    
    ga.initialize_population(pop_size)
    ga.evaluate_population()
    
    overall_best = ga.best_fitness
    best_solution = ga.get_best_routes()
    
    history = {'gen': [], 'ga_best': [], 'ts_best': [], 'overall_best': []}
    
    # Main loop
    for gen in range(generations):
        print(f"\nGeneration {gen+1}/{generations}")
        
        # GA phase
        ga_population = evolve_one_generation(ga, pop_size, crossover_rate, 
                                             mutation_rate, elite_size)
        ga_best_fitness = ga.best_fitness
        
        # TS phase
        ga_routes = ga.get_best_routes()
        ts_routes, ts_distance = ts.refine_solution(ga_routes, ts_iters)
        
        # Update best
        if ts_distance < overall_best:
            overall_best = ts_distance
            best_solution = ts_routes
            print(f"✓ NEW BEST: {overall_best:.2f}")
        
        # Track
        history['gen'].append(gen + 1)
        history['ga_best'].append(ga_best_fitness)
        history['ts_best'].append(ts_distance)
        history['overall_best'].append(overall_best)
    
    return best_solution, overall_best, history
```

### Visualization of Flow

```
Gen 1:
  GA Phase:     1500 distance
  ↓ decode
  TS Phase:     1450 distance (refinement)
  Record:       GA=1500, TS=1450, Overall=1450 ✓
  
Gen 2:
  GA Phase:     1400 distance (population improved)
  ↓ decode
  TS Phase:     1380 distance
  Record:       GA=1400, TS=1380, Overall=1380 ✓
  
Gen 3:
  GA Phase:     1420 distance (worse, GA explores)
  ↓ decode
  TS Phase:     1395 distance (still helps)
  Record:       GA=1420, TS=1395, Overall=1380 (unchanged)
  
Gen 4:
  GA Phase:     1350 distance (improvement)
  ↓ decode
  TS Phase:     1320 distance
  Record:       GA=1350, TS=1320, Overall=1320 ✓
```

---

## Parameter Interaction

### GA-TS Parameter Relationships

```
GA Parameters → Solution Quality → TS Effectiveness

Larger GA pop_size:
  ✓ Better diversity
  ✓ More solutions to refine
  ✗ Slower GA per generation
  → TS has better starting points

More GA generations:
  ✓ Population converges better
  ✓ TS refines high-quality solutions
  ✗ More total runtime
  → Each TS run on better solution

More TS iterations:
  ✓ Better local refinement
  ✓ Larger objective improvement
  ✗ Slower per generation
  → But improves overall best

Higher mutation_rate:
  ✓ More diversity in GA
  ✓ TS has more varied starting points
  ✗ Less convergence in GA
  → May need more generations
```

### Typical Configurations

**Small Problem (n < 30)**:
```python
hybrid.run(
    ga_pop_size=20,      # Small pop, fine-grained search
    ga_generations=15,   # Fewer generations needed
    ts_iterations=10,    # Good ratio (2:3)
    crossover_rate=0.85, # High mixing
    mutation_rate=0.15,  # More mutation needed
    elite_size=1
)
Runtime: ~30 seconds
```

**Medium Problem (30 ≤ n ≤ 100)**:
```python
hybrid.run(
    ga_pop_size=50,      # Balanced population
    ga_generations=30,   # Standard evolution
    ts_iterations=15,    # Good ratio (1:2)
    crossover_rate=0.8,  # Standard
    mutation_rate=0.1,   # Standard
    elite_size=2
)
Runtime: ~2-3 minutes
```

**Large Problem (n > 100)**:
```python
hybrid.run(
    ga_pop_size=80,      # Larger pop for diversity
    ga_generations=50,   # More evolution
    ts_iterations=20,    # More refinement
    crossover_rate=0.75, # Balance
    mutation_rate=0.08,  # Protect good solutions
    elite_size=3
)
Runtime: ~5-10 minutes
```

---

## Tuning Guide

### Step 1: Set Problem Size Parameters

```python
# Determine based on n (number of customers)
if n < 30:
    base_pop = 20
    base_gen = 15
elif n < 100:
    base_pop = 50
    base_gen = 30
else:
    base_pop = 80
    base_gen = 50
```

### Step 2: Quick Test

```python
# Run quick validation
hybrid.run(
    ga_pop_size=base_pop // 2,
    ga_generations=2,
    ts_iterations=3,
    ...
)
# Should complete in < 30 seconds
# Should show improvement trend
```

### Step 3: Tune for Quality

```python
# Run longer with base parameters
best_routes, best_dist, history = hybrid.run(
    ga_pop_size=base_pop,
    ga_generations=base_gen,
    ts_iterations=base_gen // 2,  # 1:2 ratio
    ...
)

# Check convergence
import numpy as np
last_10 = history['overall_best'][-10:]
improvement = (max(last_10) - min(last_10)) / max(last_10)

if improvement > 0.05:
    print("Converging well - could reduce iterations")
elif improvement < 0.01:
    print("Converged - could stop earlier or increase generations")
```

### Step 4: Hyperparameter Optimization

```python
# Test different combinations
configs = [
    {'gen': 10, 'ts': 5},
    {'gen': 20, 'ts': 10},
    {'gen': 30, 'ts': 15},
    {'gen': 50, 'ts': 10},  # Different ratio
]

results = []
for config in configs:
    routes, dist, _ = hybrid.run(
        ga_generations=config['gen'],
        ts_iterations=config['ts']
    )
    results.append({'config': config, 'distance': dist})

best_config = min(results, key=lambda x: x['distance'])
print(f"Best config: {best_config}")
```

---

## Advanced Configurations

### 1. Adaptive Integration

**Adjust TS intensity based on GA progress**:

```python
def adaptive_hybrid(ga_gens, initial_ts_iters):
    """Increase TS refinement as GA converges"""
    hybrid = HybridGATS(dist, demands, capacity)
    
    for gen in range(ga_gens):
        # More TS in later generations when GA better
        ts_iters = initial_ts_iters + (gen // 5)
        
        best_routes, _, _ = hybrid.run(
            ga_pop_size=50,
            ga_generations=1,  # One gen per iteration
            ts_iterations=ts_iters
        )
```

### 2. Multiple Restarts

**Run multiple complete hybrid cycles**:

```python
import random
import numpy as np

def multi_start_hybrid(num_runs=3):
    """Run hybrid multiple times, return best"""
    best_overall = float('inf')
    best_solution = None
    
    for run in range(num_runs):
        # Different random seed each run
        seed = 42 + run
        random.seed(seed)
        np.random.seed(seed)
        
        routes, distance, _ = hybrid.run(...)
        
        if distance < best_overall:
            best_overall = distance
            best_solution = routes
    
    return best_solution, best_overall
```

### 3. Sensitivity Analysis

**Understand parameter impact**:

```python
def sensitivity_analysis():
    """Test each parameter's effect"""
    base_config = {
        'ga_pop_size': 50,
        'ga_generations': 30,
        'ts_iterations': 15,
        'crossover_rate': 0.8,
        'mutation_rate': 0.1
    }
    
    results = {}
    
    # Test each parameter
    for param in ['ga_pop_size', 'ga_generations', 'ts_iterations']:
        results[param] = {}
        for value in [base_config[param] // 2, 
                     base_config[param],
                     base_config[param] * 2]:
            config = base_config.copy()
            config[param] = value
            
            _, distance, _ = hybrid.run(**config)
            results[param][value] = distance
    
    # Plot or print results
    for param, values in results.items():
        print(f"\n{param}:")
        for v, d in sorted(values.items()):
            print(f"  {v}: {d:.2f}")
```

### 4. Population Diversity Tracking

**Monitor GA population health**:

```python
def track_diversity():
    """Monitor population diversity over time"""
    diversity_history = []
    
    for gen in range(num_generations):
        # Calculate diversity (% positions different)
        diversity = calculate_population_diversity(ga.population)
        diversity_history.append(diversity)
        
        # If diversity drops too low, increase mutation
        if diversity < 0.3:  # Less than 30% unique positions
            mutation_rate *= 1.2  # Increase mutation
            print(f"Low diversity ({diversity:.1%}), increasing mutation")
    
    # Plot diversity
    plt.plot(diversity_history)
    plt.ylabel('Population Diversity (%)')
    plt.xlabel('Generation')
    plt.show()
```

---

## Convergence Analysis

### Analyzing Results

```python
def analyze_results(history):
    """Comprehensive convergence analysis"""
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Extract arrays
    ga_best = np.array(history['ga_best'])
    ts_best = np.array(history['ts_best'])
    overall = np.array(history['overall_best'])
    
    # Metrics
    ga_improvement = (ga_best[0] - ga_best[-1]) / ga_best[0] * 100
    ts_improvement = (ts_best[0] - ts_best[-1]) / ts_best[0] * 100
    hybrid_improvement = (overall[0] - overall[-1]) / overall[0] * 100
    
    print(f"GA Improvement: {ga_improvement:.1f}%")
    print(f"TS Improvement: {ts_improvement:.1f}%")
    print(f"Hybrid Total: {hybrid_improvement:.1f}%")
    
    # Convergence rate
    convergence_gen = np.where(overall[:-1] != overall[1:])[0]
    if len(convergence_gen) > 0:
        print(f"Converged at generation: {convergence_gen[-1]}")
    
    # Plot 
    plt.figure(figsize=(12, 5))
    
    plt.plot(history['gen'], ga_best, 'o-', label='GA')
    plt.plot(history['gen'], ts_best, 's-', label='TS')
    plt.plot(history['gen'], overall, '^-', label='Overall', linewidth=2.5)
    
    plt.xlabel('Generation')
    plt.ylabel('Distance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
```

### Performance Metrics

```
Metric              | Good | Excellent
─────────────────────────────────────
GA improvement      | >10% | >20%
TS refinement       | 2-5% | 5-10%
Total improvement   | >15% | >30%
Convergence gen     | <15  | <10
Final plateau       | <5   | <3
```

---

## Best Practices

### 1. Reproducibility

```python
import random
import numpy as np

# Always set seeds for reproducible results
seed = 42
random.seed(seed)
np.random.seed(seed)

# Document seed in results
results = {
    'seed': seed,
    'distance': best_distance,
    'routes': best_routes
}
```

### 2. Monitoring

```python
# Print progress every generation
print(f"Gen {gen+1}: GA={ga_best:.0f}, TS={ts_best:.0f}, "
      f"Overall={overall_best:.0f}")

# Alert on improvements
if ts_best < previous_best:
    print(f"✓ NEW BEST!")

# Detect stagnation
stagnation_counter += 1 if not improved else 0
if stagnation_counter > 5:
    print("No improvement for 5 generations")
```

### 3. Validation

```python
# Always verify feasibility
feasible = check_solution_feasibility(best_routes, demands, capacity)
assert feasible, "Solution violates constraints!"

# Check all customers served
all_customers = set()
for route in best_routes:
    all_customers.update(c for c in route if c != 0)
assert len(all_customers) == num_customers, "Missing customers!"

# Verify distance calculation
total_dist = sum(calculate_route_distance(r) for r in best_routes)
assert abs(total_dist - best_distance) < 0.01, "Distance mismatch!"
```

### 4. Export Results

```python
import json
import pandas as pd

# Save complete results
results_dict = {
    'config': {
        'ga_pop_size': pop_size,
        'ga_generations': generations,
        'ts_iterations': ts_iterations
    },
    'solution': {
        'distance': best_distance,
        'routes': best_routes,
        'num_routes': len(best_routes)
    },
    'history': history
}

with open('hybrid_results.json', 'w') as f:
    json.dump(results_dict, f, indent=2)

# Save routes
routes_df = pd.DataFrame({
    'route_id': range(len(best_routes)),
    'route': [str(r) for r in best_routes]
})
routes_df.to_csv('routes.csv', index=False)
```

---

## Case Studies

### Case 1: Small Problem (Problem 5)

```
Input:  20 customers
Config: pop=30, gen=15, ts=10

Results:
  GA Best:    1450
  TS Refined: 1380
  Improvement: 4.8%
  Runtime: 45 seconds
```

### Case 2: Medium Problem (Problem 7)

```
Input:  50 customers
Config: pop=50, gen=30, ts=15

Results:
  GA Best:    1800
  TS Refined: 1620
  Improvement: 10%
  Runtime: 2 min
```

### Case 3: Large Problem (Problem 8)

```
Input:  150 customers
Config: pop=80, gen=50, ts=20

Results:
  GA Best:    2500
  TS Refined: 2100
  Improvement: 16%
  Runtime: 8 min
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Poor quality | Low GA_gens | Increase ga_generations |
| Slow TS | Large neighborhoods | Reduce ts_iterations |
| No convergence | High mutation | Lower mutation_rate |
| Stagnating GA | Low diversity | Increase mutation |
| Slow overall | Large pop | Reduce ga_pop_size |

---

## References

- Cordeau, J. F., et al. (2007). Recent Advances in the Vehicle Routing Problem
- Blum, C., & Roli, A. (2003). Metaheuristics in combinatorial optimization
- Burke, E. K., & Kendall, G. (2005). Search Methodologies

