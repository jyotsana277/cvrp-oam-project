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
├── API.md                             # API documentation
├── USAGE.md                           # Usage guide & examples
├── INSTALLATION.md                    # Setup instructions
├── QUICK_REFERENCE.md                 # Cheat sheet
├── GA_IMPLEMENTATION.md               # GA deep dive
├── TABU_SEARCH_IMPLEMENTATION.md      # TS deep dive
├── HYBRID_GA_TABU_GUIDE.md            # Integration guide
├── WEBAPP_GUIDE.md                    # Web app documentation
├── oam_project_dataset1.ipynb         # Main Jupyter notebook
├── app.py                             # Streamlit web app (interactive)
├── 19MDVRP Problem Sets.xlsx          # MDRP dataset (Problem 7)
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
└── .git/                              # Git repository
```

## 🚀 Quick Start

### Fastest Way: Web App (No Coding!)

```bash
# 1. Install Streamlit
pip install streamlit

# 2. Run the app
streamlit run app.py

# 3. Open browser at http://localhost:8501
# 4. Adjust parameters and click "Run Optimization"
```

**Web app includes:**
- Interactive parameter controls
- Real-time optimization progress
- Visual convergence plots
- Detailed route breakdown
- CSV export

See [WEBAPP_GUIDE.md](WEBAPP_GUIDE.md) for full web app documentation.

### Alternative: Jupyter Notebook

```bash
# Open interactive notebook
jupyter notebook oam_project_dataset1.ipynb
```

### Alternative: Python Script

See "Usage Examples" section below for code examples.

### Installation

```bash
# Clone repository
git clone https://github.com/jyotsana277/cvrp-oam-project.git
cd cvrp-oam-project

# Install dependencies (all packages)
pip install -r requirements.txt

# Or install only core packages
pip install numpy pandas openpyxl matplotlib

# For web app support, also install:
pip install streamlit
```

### Required Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | ≥1.19.0 | Numerical computations |
| `pandas` | ≥1.1.0 | Data manipulation |
| `openpyxl` | ≥3.0.0 | Excel file reading |
| `matplotlib` | ≥3.3.0 | Visualization |
| `streamlit` | ≥1.28.0 | Web app framework (optional) |
| `jupyter` | ≥1.0.0 | Notebook environment (optional) |

### Two Ways to Use

#### Option 1: Interactive Web App (Recommended for Users)

```bash
# Install Streamlit
pip install streamlit

# Run the web app
streamlit run app.py
```

The app opens at `http://localhost:8501` with:
- 🎛️ **Live Configuration Panel**: Adjust parameters in real-time
- 📊 **Interactive Dashboard**: View results instantly
- 🛣️ **Route Visualization**: Expandable route details
- 💾 **CSV Export**: Download optimized routes

**Features:**
- No coding required
- Visual parameter controls
- Real-time progress tracking
- One-click result export

See [WEBAPP_GUIDE.md](WEBAPP_GUIDE.md) for detailed instructions.

#### Option 2: Jupyter Notebook (For Development/Analysis)

```bash
# Install Jupyter
pip install jupyter

# Run notebook
jupyter notebook oam_project_dataset1.ipynb
```

Execute cells in order to:
- Load and explore data
- Run individual algorithm components
- Analyze convergence step-by-step
- Customize advanced parameters

#### Option 3: Python Script (For Batch Processing)

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

### Interactive Web Dashboard

The **Streamlit web app** (`app.py`) provides an interactive interface:

```
Main Features:
├── 🎛️ Configuration Panel (Sidebar)
│   ├── GA parameters (population, generations)
│   ├── TS parameters (iterations, tenure)
│   ├── Operator tuning (crossover, mutation)
│   └── Problem selection
│
├── 📈 Real-time Visualization
│   ├── Convergence plot (GA, TS, Overall)
│   ├── Performance metrics (distance, routes, improvement %)
│   └── Live progress bar
│
├── 🛣️ Route Details
│   ├── Expandable route cards
│   ├── Load information
│   └── Distance breakdown
│
└── 💾 Export Options
    └── Download routes as CSV
```

**Example Dashboard Output:**
- Problem: 100 customers
- Best Distance: 2,980.45
- Routes: 8
- Improvement: 3.2%

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

## 📚 Documentation

### Getting Started
- **[WEBAPP_GUIDE.md](WEBAPP_GUIDE.md)** - Interactive web app guide (recommended for new users)
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup instructions
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick help & command cheat sheet

### Algorithm Details
- **[ALGORITHM.md](ALGORITHM.md)** - Complete algorithm formulation and pseudocode
- **[GA_IMPLEMENTATION.md](GA_IMPLEMENTATION.md)** - Genetic Algorithm deep dive
- **[TABU_SEARCH_IMPLEMENTATION.md](TABU_SEARCH_IMPLEMENTATION.md)** - Tabu Search deep dive
- **[HYBRID_GA_TABU_GUIDE.md](HYBRID_GA_TABU_GUIDE.md)** - Integration strategy & tuning

### API & Usage
- **[API.md](API.md)** - Complete API reference with code examples
- **[USAGE.md](USAGE.md)** - Usage tutorials and examples

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
