# Contributing Guidelines

Thank you for your interest in contributing to the CVRP Optimization project! This document provides guidelines for contributions.

## Project Structure

```
cvrp-oam-project/
├── README.md                    # Main documentation
├── ALGORITHM.md                 # Algorithm details & pseudocode
├── API.md                       # API reference
├── USAGE.md                     # Usage examples & tutorials
├── CONTRIBUTING.md              # This file
├── oam_project_dataset1.ipynb   # Main implementation notebook
├── 19MDVRP Problem Sets.xlsx    # Dataset
└── .git/                        # Repository
```

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/jyotsana277/cvrp-oam-project.git
cd cvrp-oam-project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Jupyter for development
pip install jupyter jupyterlab
```

### Code Organization

**Notebook Cells Organization:**

1. **Data Loading** (Cells 1-5)
   - Load CVRP data from Excel
   - Compute distance matrix
   - Feasibility checking utilities

2. **Genetic Algorithm** (Cells 6-10)
   - GeneticAlgorithm class
   - Population initialization
   - Selection, crossover, mutation

3. **Tabu Search** (Cells 11-13)
   - TabuSearch class
   - Neighborhood generation
   - Tabu list management

4. **Hybrid Pipeline** (Cells 14-16)
   - HybridGATS class
   - Integration logic
   - Results analysis

5. **Examples** (Cells 17+)
   - Usage examples
   - Benchmark runs
   - Visualization

## Contribution Types

### 1. Bug Fixes

If you find a bug:

1. Create an issue describing the bug
2. Fork the repository
3. Create a branch: `git checkout -b fix/bug-description`
4. Fix the bug with clear commit messages
5. Add test cases if applicable
6. Submit pull request with description

**Example PR:**
```
Title: Fix capacity constraint bug in TabuSearch
Description:
- Issue: Routes sometimes exceed capacity after TS refinement
- Cause: Missing feasibility check in move evaluation
- Solution: Added IsRouteFeasible check before accepting moves
- Testing: Verified on 10 test cases
```

### 2. Feature Enhancements

Proposed features should:

1. Solve a real problem or add significant value
2. Not break existing functionality
3. Include documentation updates
4. Have clear examples

**Example features:**
- Multiple depot support
- Time window constraints
- Real-time rerouting
- Advanced visualization

### 3. Performance Improvements

Optimizations should:

1. Maintain algorithm correctness
2. Be benchmarked (before/after)
3. Not significantly increase complexity
4. Include documentation of improvements

**Example optimizations:**
- Vectorized distance calculations with numpy
- Parallel fitness evaluation
- Incremental distance updates in TS

### 4. Documentation

Documentation improvements are always welcome:

- **README.md**: High-level overview and quick start
- **ALGORITHM.md**: Mathematical formulation and pseudocode
- **API.md**: Detailed method documentation
- **USAGE.md**: Examples and tutorials
- **Code comments**: Inline documentation in notebook

### 5. Testing & Validation

Help improve code quality:

1. Create comprehensive test cases
2. Validate on different problem sizes
3. Test edge cases
4. Performance profiling

## Coding Standards

### Python Style

Follow PEP 8 with these preferences:

```python
# Good: Clear naming, type hints in comments
def evaluate_fitness(self, chromosome):
    """
    Calculate fitness score for a chromosome.
    
    Args:
        chromosome: List of customer indices
        
    Returns:
        float: Total distance (fitness value)
    """
    routes = self.decode_chromosome(chromosome)
    return self.calculate_routes_distance(routes)

# Avoid: Unclear names, missing docs
def eval_fit(c):
    r = self.dec_chr(c)
    return self.calc_dist(r)
```

### Documentation Standards

Every class and method should include:

```python
"""
Brief one-line description.

Detailed explanation of what this does, why it matters,
and any important notes about usage or assumptions.

Args:
    param1 (type): Description of param1
    param2 (type): Description of param2
    
Returns:
    type: Description of return value
    
Raises:
    ExceptionType: When this exception is raised
    
Example:
    >>> instance.method(param1, param2)
    expected_output
    
Time Complexity: O(...)
Space Complexity: O(...)
"""
```

### Comment Guidelines

Use comments to explain **why**, not **what**:

```python
# Good: Explains reasoning
if current_load + demand > self.capacity:
    # Capacity exceeded; must close current route and start new one
    # to maintain feasibility constraint
    current_route.append(self.depot)
    routes.append(current_route)
    current_route = [self.depot]

# Avoid: Repeats code
if current_load + demand > self.capacity:
    # Add depot to current route
    current_route.append(self.depot)
    # Append route to routes
    routes.append(current_route)
    # Start new route with depot
    current_route = [self.depot]
```

## Git Workflow

### Branch Naming

```
feature/description       # New feature
fix/description          # Bug fix
docs/description         # Documentation
test/description         # Tests
refactor/description     # Code refactoring
perf/description         # Performance improvement
```

### Commit Messages

```
# Good: Clear, descriptive, reference issues
Fix capacity feasibility check in TabuSearch
- Add IsRouteFeasible validation before accepting TS moves
- Prevents infeasible routes in final solution
- Fixes #15

# Avoid: Vague or unclear
fixed stuff
update
work in progress
```

### Pull Request Process

1. **Before starting**: Check existing PRs/issues
2. **Fork & branch**: Create feature branch
3. **Implement**: Add feature with tests
4. **Document**: Update relevant .md files
5. **Test**: Run on multiple problem sizes
6. **Submit**: Create PR with clear description

**PR Template:**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update

## Testing
- [ ] Tested on small problems (n < 50)
- [ ] Tested on medium problems (50 ≤ n < 100)
- [ ] Tested on large problems (n ≥ 100)
- [ ] Added test cases

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Performance impact analyzed
```

## Algorithm Development

### Adding New Operators

**Genetic Algorithm - New Crossover:**

```python
def crossover_position_based(self, parent1, parent2):
    """
    Position-Based Crossover (PBX):
    Inherits positions from parent1, order from parent2.
    
    Args:
        parent1, parent2: Chromosomes
        
    Returns:
        child: Offspring chromosome
    """
    n = len(parent1)
    child = [None] * n
    
    # Inherit positions from parent1
    positions_from_parent1 = set(random.sample(range(n), n // 2))
    for pos in positions_from_parent1:
        child[pos] = parent1[pos]
    
    # Fill with parent2's order
    fill_pos = 0
    for gene in parent2:
        if gene not in child:
            while fill_pos < n and child[fill_pos] is not None:
                fill_pos += 1
            if fill_pos < n:
                child[fill_pos] = gene
    
    return child
```

**Tabu Search - New Neighborhood:**

```python
def generate_neighborhood_2opt(self, routes):
    """
    2-opt neighborhood: swap edges within and between routes.
    More intensive but potentially better quality.
    
    Args:
        routes: Current solution
        
    Returns:
        neighbors: List of valid neighbor solutions
    """
    neighbors = []
    
    for r_idx, route in enumerate(routes):
        for i in range(1, len(route) - 2):
            for j in range(i + 2, len(route) - 1):
                # Reverse segment between i and j
                new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                new_routes = [rt.copy() for rt in routes]
                new_routes[r_idx] = new_route
                
                if self.is_solution_feasible(new_routes):
                    move = ('2opt', r_idx, i, j)
                    neighbors.append((new_routes, move))
    
    return neighbors
```

### Algorithm Validation

When implementing new algorithms:

1. **Verify correctness**: Test on known problem instances
2. **Compare baselines**: Compare against existing operators
3. **Convergence analysis**: Plot fitness over iterations
4. **Parameter sensitivity**: Test with different settings

## Testing

### Test Cases

Create test cases for:

1. **Functionality**: Does it work as designed?
2. **Edge cases**: Empty routes, single customer, capacity = 0
3. **Performance**: Is it efficient enough?
4. **Correctness**: Are constraints satisfied?

**Example test:**

```python
def test_capacity_feasibility():
    """Verify all routes respect capacity constraints"""
    dist = np.eye(6)  # Simple 5-customer problem
    demands = [100, 200, 150, 100, 50]
    capacity = 300
    
    hybrid = HybridGATS(dist, demands, capacity, num_customers=5)
    routes, _, _ = hybrid.run(ga_pop_size=10, ga_generations=5, ts_iterations=3)
    
    # Check each route
    for route in routes:
        customers = [c for c in route if c != 0]
        load = sum(demands[c-1] for c in customers)
        assert load <= capacity, f"Route {route} exceeds capacity"
```

## Documentation Requirements

For each contribution, update relevant files:

| Change Type | Update |
|------------|--------|
| New class/method | API.md + docstrings |
| New algorithm | ALGORITHM.md + API.md |
| New features | USAGE.md example + README.md |
| Bug fix | Update relevant .md section |
| Performance | ALGORITHM.md complexity |

## Review Process

**Reviewers will check:**

1. ✓ Code quality and style consistency
2. ✓ Algorithm correctness and validation
3. ✓ Documentation completeness
4. ✓ Test coverage adequacy
5. ✓ Performance impact
6. ✓ Breaking changes assessment

## Questions or Issues?

- Create GitHub Issue for bugs or questions
- Check existing Issues first
- Include: problem description, data size, expected vs actual behavior
- Provide: minimal reproducible example if possible

## License

By contributing, you agree that your contributions are licensed under the project's license (academic use).

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Welcome diverse perspectives and approaches
- Help maintain welcoming community

---

## Quick Start for Contributors

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/cvrp-oam-project.git
cd cvrp-oam-project

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes
# Edit oam_project_dataset1.ipynb in Jupyter

# 4. Test locally
jupyter notebook oam_project_dataset1.ipynb
# Run all cells to verify

# 5. Update documentation
# Edit relevant .md files

# 6. Commit and push
git add .
git commit -m "Clear description of changes"
git push origin feature/your-feature

# 7. Create Pull Request on GitHub
# Include: description, testing done, related issues
```

Thank you for contributing to improve CVRP optimization!

