# CVRP Optimization with Genetic Algorithm & Tabu Search (OAM)

A hybrid metaheuristic approach for solving the **Capacitated Vehicle Routing Problem (CVRP)** using **Genetic Algorithm (GA)** combined with **Tabu Search (TS)** refinement.

## 📋 Overview

This project implements a state-of-the-art hybrid optimization algorithm that combines:
- **Genetic Algorithm**: Population-based global search for exploring the solution space
- **Tabu Search**: Local search refinement to improve solution quality and escape local optima

The algorithm is designed specifically for the CVRP, where multiple vehicles must deliver goods to customers while respecting vehicle capacity constraints and minimizing total travel distance.

## 🎯 Problem Definition

**Capacitated Vehicle Routing Problem (CVRP)**:
- Given: Set of customers with demands, vehicle capacity, distance matrix
- Objective: Find routes for vehicles starting/ending at depot that:
  1. Serve all customers exactly once
  2. Respect vehicle capacity constraints
  3. Minimize total travel distance

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────┐
│          Data Loading & Preparation             │
│  (MDRP Dataset Format, Distance Matrix)         │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────────┐          ┌──────────────┐
   │ Genetic     │          │ Tabu Search  │
   │ Algorithm   │◄────────►│ Refinement   │
   │             │          │              │
   │ • Population│          │ • Neighborhood
   │ • Selection │          │ • Tabu List  
   │ • Crossover │          │ • Aspiration 
   │ • Mutation  │          │ • Iteration  
   └─────────────┘          └──────────────┘
        │                         │
        └────────────┬────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Best Solution Found   │
        │  Convergence Analysis  │
        │  Visualization         │
        └────────────────────────┘
```

## 📁 Project Structure

```
cvrp-oam-project/
├── README.md                          # Main documentation
├── ALGORITHM.md                       # Detailed algorithm explanation
├── USAGE.md                           # Usage guide & examples
├── API.md                             # API documentation
├── oam_project_dataset1.ipynb         # Main Jupyter notebook
├── 19MDVRP Problem Sets.xlsx          # MDRP dataset (Problem 7)
└── .git/                              # Git repository
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Required packages: `numpy`, `pandas`, `openpyxl`, `matplotlib`

### Installation

```bash
# Clone repository
git clone https://github.com/jyotsana277/cvrp-oam-project.git
cd cvrp-oam-project

# Install dependencies
pip install numpy pandas openpyxl matplotlib
```

### Basic Usage

```python
from oam_project_dataset1 import HybridGATS, load_mdrp_format, compute_distance_matrix

# Load CVRP data
depots, coords, demands = load_mdrp_format("19MDVRP Problem Sets.xlsx", sheet="Problem 7")
dist_matrix = compute_distance_matrix(coords)

# Initialize hybrid algorithm
hybrid = HybridGATS(
    dist=dist_matrix,
    demands=demands,
    capacity=1000,  # Vehicle capacity
    num_customers=len(coords)
)

# Run optimization
best_routes, best_distance, history = hybrid.run(
    ga_pop_size=40,
    ga_generations=15,
    ts_iterations=10,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=2
)

# Visualize results
hybrid.print_solution_summary()
hybrid.plot_convergence()
```

## 🧬 Genetic Algorithm Component

### Population Representation
- **Chromosome**: Giant tour (permutation of customer indices 1 to n)
- **Interpretation**: Sequence of customers to visit in order

### Key Operations

#### 1. Population Initialization
```
- Initialize pop_size random permutations
- Each permutation represents a potential giant tour
```

#### 2. Fitness Evaluation
```
- Decode chromosome to feasible routes (respecting capacity)
- Calculate total route distance
- Lower distance = higher fitness (better solution)
```

#### 3. Selection: Roulette Wheel
```
- Fitness-proportional selection
- Better solutions have higher selection probability
- Inverse fitness mapping: worse solutions have lower chance
```

#### 4. Crossover: Order-Based Crossover (OBX)
```
1. Select random subset S from Parent 1
2. Place S at same positions in Child
3. Fill remaining with Parent 2's order
4. Preserves relative order information
```

#### 5. Mutation: Swap Mutation
```
- Randomly select two cities
- Swap their positions in chromosome
- Exploration mechanism for new regions
```

### Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `pop_size` | 40 | Population size |
| `generations` | 15 | Number of generations |
| `crossover_rate` | 0.8 | Probability of crossover |
| `mutation_rate` | 0.1 | Mutation probability per city |
| `elite_size` | 2 | Elite individuals preserved |

## 🔍 Tabu Search Component

### Neighborhood Generation
- **Move**: Relocate customer from one route to another
- **Move Format**: (from_route_idx, cust_idx, to_route_idx, insert_pos)
- **Feasibility Check**: Ensures capacity constraints after relocation

### Tabu List Management
- **Tabu Status**: Moves in tabu list are forbidden (prevents cycling)
- **Tabu Tenure**: Time steps a move remains in tabu list (default: 10)
- **Decay**: Tabu tenure decreases each iteration

### Aspiration Criteria
- **Override Tabu**: Accept tabu moves if they improve best-ever solution
- **Mechanism**: Prevents getting stuck in local optima
- **Balance**: Exploration vs. Exploitation

### Search Process
```
For each TS iteration:
1. Generate neighborhood (all feasible relocations)
2. Update tabu tenure counters
3. Find best non-tabu neighbor
4. Check aspiration criteria
5. Move to selected neighbor
6. Update tabu list
7. Track best solution found
```

### Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `iterations` | 20 | TS iterations per GA generation |
| `tabu_tenure` | 10 | Iterations a move stays tabu |

## 🔄 Hybrid Pipeline

### Execution Flow

```
1. Initialize GA population (random permutations)
2. Evaluate fitness for all individuals

FOR each GA generation:
   a) Perform GA operations:
      - Preserve elite individuals
      - Create offspring via selection, crossover, mutation
      - Evaluate new population
   
   b) Apply Tabu Search:
      - Get best GA individual
      - Decode to routes
      - Run TS refinement (ts_iterations)
      - Track best TS-refined solution
   
   c) Update tracking:
      - Record GA best, TS best, overall best
      - Check for improvements

3. Return best solution found
4. Visualize convergence
```

### Key Features
- **Early Stopping**: Can terminate if no improvement
- **Elite Preservation**: Best solutions never lost
- **Hybrid Synergy**: GA explores, TS exploits and refines
- **Convergence Tracking**: Monitor all three best fitness values

## 📊 Results & Analysis

### Output Format
```python
{
    'best_routes': [[0, 1, 4, 7, 0], [0, 2, 5, 0], ...],
    'best_distance': 1234.56,
    'history': {
        'gen': [1, 2, 3, ...],
        'ga_best': [1500, 1400, 1350, ...],
        'ts_best': [1450, 1380, 1340, ...],
        'overall_best': [1450, 1380, 1340, ...]
    }
}
```

### Convergence Metrics
- **GA Best**: Solution quality from genetic algorithm alone
- **TS Best**: Quality after tabu search refinement
- **Overall Best**: Best solution found in any iteration
- **Improvement Rate**: Measures algorithm effectiveness

### Visualization
- Convergence curve showing GA, TS, and overall best progression
- Route visualization (can be extended)
- Solution quality analysis

## 🔧 Configuration

### For Small Problems (< 50 customers)
```python
hybrid.run(
    ga_pop_size=30,
    ga_generations=20,
    ts_iterations=15,
    crossover_rate=0.85,
    mutation_rate=0.15
)
```

### For Medium Problems (50-100 customers)
```python
hybrid.run(
    ga_pop_size=50,
    ga_generations=30,
    ts_iterations=20,
    crossover_rate=0.8,
    mutation_rate=0.1
)
```

### For Large Problems (> 100 customers)
```python
hybrid.run(
    ga_pop_size=80,
    ga_generations=50,
    ts_iterations=25,
    crossover_rate=0.75,
    mutation_rate=0.08
)
```

## 📈 Performance Characteristics

### Time Complexity
- **GA Evaluation**: O(n) per individual (decoding + distance calculation)
- **TS Neighborhood**: O(n²) per iteration
- **Overall**: O(g × (p × n + ts × n²)) where g=generations, p=population, ts=TS iterations

### Space Complexity
- O(n²) for distance matrix
- O(p × n) for population
- O(n) for best solution tracking

## 🎓 Algorithm Details

See [ALGORITHM.md](ALGORITHM.md) for:
- Detailed mathematical formulation
- Pseudocode for each component
- Complexity analysis
- Convergence properties

## 💡 Usage Examples

See [USAGE.md](USAGE.md) for:
- Step-by-step tutorials
- Different problem sizes
- Custom configurations
- Result interpretation

## 🔌 API Reference

See [API.md](API.md) for:
- Complete method documentation
- Parameter descriptions
- Return value specifications
- Example code snippets

## 🧪 Testing

Run the notebook cells in order:
1. Data loading cells (verify dataset loads correctly)
2. GA implementation cells (test population, crossover, mutation)
3. TS implementation cells (test neighborhood generation)
4. Hybrid pipeline cell (full algorithm execution)

## 📝 Dataset

### MDRP Format (19MDVRP Problem Sets.xlsx)
- **Sheet**: "Problem 7"
- **Columns**: 
  - `Depot x coordinate`, `Depot y coordinate`: Depot location
  - `Customer Number`: Customer ID
  - `x coordinate`, `y coordinate`: Customer location
- **Data**: Automatically loaded with generated unit demands

### Dataset Statistics
- Total locations (depots + customers)
- Customer coordinates (x, y)
- Distance matrix (Euclidean)
- Uniform demand (default: 1 unit/customer)

## 🚀 Future Enhancements

- [ ] Multiple depots support
- [ ] Time window constraints
- [ ] Vehicle heterogeneity (different capacities)
- [ ] Real-time rerouting
- [ ] Advanced visualization (map display)
- [ ] Parallel population evaluation
- [ ] Adaptive parameter tuning
- [ ] Solution export (CSV, JSON formats)

## 📚 References

- Classic CVRP literature and benchmarks
- Genetic Algorithm foundations (Holland, Goldberg)
- Tabu Search methodology (Glover, Laguna)
- Hybrid metaheuristic approaches

## 👥 Contributors

- **Person A**: Data loading and preprocessing
- **Person B**: Route feasibility and distance calculation
- **Person C**: Tabu Search implementation
- **Current**: Genetic Algorithm + Hybrid pipeline integration

## 📄 License

This project is part of academic coursework for Optimization algorithms.

## 📧 Contact

For questions or issues, please refer to the repository maintainers.

## 🔗 Links

- **GitHub**: https://github.com/jyotsana277/cvrp-oam-project
- **Dataset**: 19MDVRP Problem Sets
- **Notebook**: `oam_project_dataset1.ipynb`

---

**Last Updated**: November 2025  
**Status**: Active Development
