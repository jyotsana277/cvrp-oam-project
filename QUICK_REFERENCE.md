# Quick Reference Guide

Fast lookup for common tasks, troubleshooting, and best practices.

## ⚡ 30-Second Quick Start

```python
# 1. Load data
from oam_project_dataset1 import *
depots, coords, demands = load_mdrp_format("19MDVRP Problem Sets.xlsx", sheet="Problem 7")
dist_matrix = compute_distance_matrix(coords)

# 2. Run optimization
hybrid = HybridGATS(dist=dist_matrix, demands=demands, capacity=1000, num_customers=len(coords))
best_routes, best_distance, history = hybrid.run(ga_pop_size=40, ga_generations=15, ts_iterations=10)

# 3. View results
hybrid.print_solution_summary()
hybrid.plot_convergence()
```

---

## 📋 Command Cheat Sheet

### Setup
```bash
python -m venv venv              # Create environment
source venv/bin/activate         # Activate (Linux/macOS)
venv\Scripts\activate            # Activate (Windows)
pip install -r requirements.txt  # Install dependencies
jupyter notebook                 # Start Jupyter
```

### Python Imports
```python
from oam_project_dataset1 import (
    load_mdrp_format,                 # Load Excel data
    compute_distance_matrix,          # Compute distances
    GeneticAlgorithm,                 # GA component
    TabuSearch,                       # TS component
    HybridGATS,                       # Hybrid algorithm
    check_solution_feasibility        # Verify solution
)
```

---

## 🎯 Common Tasks

### Task 1: Run Full Optimization

```python
# Load data
depots, coords, demands = load_mdrp_format("19MDVRP Problem Sets.xlsx", sheet="Problem 7")
dist_matrix = compute_distance_matrix(coords)

# Configure and run
hybrid = HybridGATS(dist=dist_matrix, demands=demands, capacity=1000, num_customers=len(coords))
routes, distance, history = hybrid.run(
    ga_pop_size=50,
    ga_generations=30,
    ts_iterations=20,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=2
)

# Results
print(f"Best distance: {distance:.2f}")
print(f"Routes: {len(routes)}")
```

### Task 2: Quick Test (< 1 minute)

```python
# Minimal parameters for fast testing
routes, distance, history = hybrid.run(
    ga_pop_size=10,
    ga_generations=2,
    ts_iterations=3
)
```

### Task 3: High Quality (takes longer)

```python
# Better quality, slower
routes, distance, history = hybrid.run(
    ga_pop_size=100,
    ga_generations=50,
    ts_iterations=30
)
```

### Task 4: GA Only (no Tabu Search)

```python
ga = GeneticAlgorithm(dist_matrix, demands, capacity=1000)
best_chrom, history = ga.evolve(
    pop_size=50,
    generations=30,
    crossover_rate=0.8,
    mutation_rate=0.1
)
routes = ga.get_best_routes()
```

### Task 5: Tabu Search Only

```python
ts = TabuSearch(dist_matrix, demands, capacity=1000)
initial_routes = [[0, 1, 2, 0], [0, 3, 4, 0]]  # Example initial solution
refined_routes, refined_distance = ts.refine_solution(initial_routes, iterations=30)
```

### Task 6: Check Solution Feasibility

```python
# Verify all routes respect capacity
feasible = check_solution_feasibility(routes, demands, capacity=1000)
print(f"Solution feasible: {feasible}")

# Manually check each route
for i, route in enumerate(routes):
    customers = [c for c in route if c != 0]
    load = sum(demands[c] for c in customers)
    print(f"Route {i+1}: Load = {load}/1000")
```

### Task 7: Export Results

```python
import pandas as pd
import json

# Export to CSV
routes_df = pd.DataFrame({
    'route': [str(r) for r in routes],
    'distance': [sum(dist_matrix[routes[i][j], routes[i][j+1]] 
                     for j in range(len(routes[i])-1)) 
                for i in range(len(routes))]
})
routes_df.to_csv('routes.csv', index=False)

# Export to JSON
solution = {'routes': routes, 'distance': distance, 'history': history}
with open('solution.json', 'w') as f:
    json.dump(solution, f, indent=2)
```

---

## 🐛 Troubleshooting

| Problem | Solution | Details |
|---------|----------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` | See INSTALLATION.md |
| `FileNotFoundError` (Excel) | Check file exists: `ls 19MDVRP*` | Filename must match exactly |
| Memory error | Reduce `ga_pop_size` to 20-30 | See INSTALLATION.md troubleshooting |
| Jupyter not found | `pip install jupyter` | Or use `jupyter notebook` |
| Slow performance | Reduce generations/pop_size | Expected for large problems |
| Poor solution quality | Increase `ga_generations` to 50+ | More generations = better but slower |
| Routes exceed capacity | Use valid initial setup | Verify `demands` ≤ `capacity` |

---

## ⚙️ Parameter Tuning Quick Guide

### For Small Problems (< 50 customers)
```python
hybrid.run(
    ga_pop_size=30,
    ga_generations=20,
    ts_iterations=15
)
```

### For Medium Problems (50-100 customers)
```python
hybrid.run(
    ga_pop_size=50,
    ga_generations=30,
    ts_iterations=20
)
```

### For Large Problems (> 100 customers)
```python
hybrid.run(
    ga_pop_size=80,
    ga_generations=50,
    ts_iterations=25
)
```

### For Very Fast Testing
```python
hybrid.run(
    ga_pop_size=10,
    ga_generations=2,
    ts_iterations=3
)
```

---

## 📊 Understanding Output

### Convergence History
```python
history = {
    'gen': [1, 2, 3, ...],           # Generation number
    'ga_best': [1500, 1400, ...],    # GA's best fitness
    'ts_best': [1450, 1380, ...],    # After TS refinement
    'overall_best': [1450, 1380, ...]# Best ever found
}

# Plot convergence
import matplotlib.pyplot as plt
plt.plot(history['gen'], history['overall_best'])
plt.xlabel('Generation')
plt.ylabel('Distance')
plt.show()
```

### Solution Format
```python
routes = [
    [0, 1, 3, 5, 0],      # Route 1: depot→1→3→5→depot
    [0, 2, 4, 0],         # Route 2: depot→2→4→depot
    [0, 6, 7, 8, 0]       # Route 3: depot→6→7→8→depot
]

# Route 1 distance: d(0,1) + d(1,3) + d(3,5) + d(5,0)
```

---

## 🔍 Debugging Tips

### Print Details During Run

```python
# Enable verbose output (default is on)
hybrid.run(ga_pop_size=40, ga_generations=5, ts_iterations=10)

# Print after completion
hybrid.print_solution_summary()

# Check history
print(f"Convergence: {history['overall_best']}")
```

### Test on Small Problem First

```python
# Use Problem 5 instead of 7 (smaller dataset)
depots, coords, demands = load_mdrp_format(sheet="Problem 5")
dist_matrix = compute_distance_matrix(coords)

# Run quick test
print(f"Problem size: {len(coords)} customers")
hybrid = HybridGATS(dist_matrix, demands, 1000, num_customers=len(coords))
routes, distance, _ = hybrid.run(ga_pop_size=20, ga_generations=5, ts_iterations=5)
```

### Verify Data Loading

```python
import numpy as np

print(f"Coordinates shape: {coords.shape}")
print(f"Demands shape: {demands.shape}")
print(f"Distance matrix shape: {dist_matrix.shape}")
print(f"Is symmetric: {np.allclose(dist_matrix, dist_matrix.T)}")
print(f"Diagonal zeros: {np.allclose(np.diag(dist_matrix), 0)}")
```

---

## 📈 Performance Metrics

### Typical Results (Problem 7)

| Config | Time | Distance | Routes |
|--------|------|----------|--------|
| pop=10, gen=2 | ~10s | ~2500 | 5 |
| pop=40, gen=15 | ~2min | ~1800 | 4 |
| pop=80, gen=30 | ~5min | ~1500 | 4 |

### Expected Improvement

| Phase | Typical Improvement |
|-------|-------------------|
| GA (first 10 gen) | 15-25% |
| TS refinement | 2-8% per application |
| Hybrid total | 25-40% vs random |

---

## 🎓 Learning Path

1. **Start here**: This file (QUICK_REFERENCE.md)
2. **Setup**: [INSTALLATION.md](INSTALLATION.md)
3. **Understand algorithms**: 
   - [GA_IMPLEMENTATION.md](GA_IMPLEMENTATION.md)
   - [TABU_SEARCH_IMPLEMENTATION.md](TABU_SEARCH_IMPLEMENTATION.md)
4. **Advanced usage**: [HYBRID_GA_TABU_GUIDE.md](HYBRID_GA_TABU_GUIDE.md)
5. **Full reference**: [API.md](API.md)
6. **Detailed examples**: [USAGE.md](USAGE.md)

---

## 🆘 Getting Help

### Documentation Quick Links
```
Setup Issues       → INSTALLATION.md
Algorithm Details  → GA_IMPLEMENTATION.md, TABU_SEARCH_IMPLEMENTATION.md
How To Use         → USAGE.md + QUICK_REFERENCE.md
API Reference      → API.md
Contributing       → CONTRIBUTING.md
```

### Common Issues by File

**INSTALLATION.md covers:**
- Python not found
- pip not working
- Virtual environment issues
- Package installation errors

**USAGE.md covers:**
- How to run optimization
- Parameter tuning
- Multiple runs/sensitivity analysis
- Exporting results

**API.md covers:**
- Method signatures
- Parameter descriptions
- Return value formats
- Example usage

**GA_IMPLEMENTATION.md covers:**
- How GA works
- Genetic operators (crossover, mutation)
- Selection mechanism
- Population evolution

**TABU_SEARCH_IMPLEMENTATION.md covers:**
- Tabu list management
- Neighborhood exploration
- Aspiration criteria
- Local search process

**HYBRID_GA_TABU_GUIDE.md covers:**
- Integration strategy
- When to use GA vs TS
- Parameter interaction
- Advanced configurations

---

## 💡 Pro Tips

1. **Save results**: Always export to CSV/JSON before stopping
   ```python
   import json
   with open('results.json', 'w') as f:
       json.dump({'routes': routes, 'distance': distance}, f)
   ```

2. **Set random seed**: For reproducible results
   ```python
   import random, numpy as np
   random.seed(42)
   np.random.seed(42)
   ```

3. **Monitor convergence**: Watch for plateaus
   ```python
   if history['overall_best'][-1] == history['overall_best'][-10]:
       print("Converged - no improvement in 10 generations")
   ```

4. **Use smaller TS tenure**: For faster convergence
   ```python
   ts = TabuSearch(dist, demands, capacity)
   ts.tabu_tenure = 5  # Default is 10
   ```

5. **Parallel runs**: Test multiple seeds
   ```python
   results = []
   for seed in range(5):
       np.random.seed(seed)
       _, dist, _ = hybrid.run(...)
       results.append(dist)
   print(f"Average: {np.mean(results):.2f}")
   ```

---

## 🚀 Next Steps

- **Run it**: Follow "30-Second Quick Start" above
- **Tune it**: See parameter tuning section
- **Understand it**: Read GA_IMPLEMENTATION.md
- **Optimize it**: Read HYBRID_GA_TABU_GUIDE.md
- **Learn all**: See Learning Path above

---

**Need more info?** Check the specific documentation file for your question!

