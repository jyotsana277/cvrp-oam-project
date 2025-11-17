# Algorithm Documentation

## Table of Contents
1. [Problem Formulation](#problem-formulation)
2. [Genetic Algorithm](#genetic-algorithm)
3. [Tabu Search](#tabu-search)
4. [Hybrid Pipeline](#hybrid-pipeline)
5. [Complexity Analysis](#complexity-analysis)
6. [Convergence Properties](#convergence-properties)

## Problem Formulation

### CVRP Definition

**Given:**
- Graph $G = (V, E)$ where $V = \{0, 1, 2, ..., n\}$ (depot + customers)
- Distance matrix $d_{ij}$ for all pairs $(i,j) \in V$
- Vehicle capacity $Q$
- Customer demands $q_i$ for $i \in \{1, ..., n\}$

**Decision Variables:**
- Binary variables $x_{ij}^k = 1$ if vehicle $k$ uses edge $(i,j)$, else 0
- Route assignment for each vehicle

**Objective:**
$$\text{Minimize} \quad Z = \sum_{k=1}^{m} \sum_{i=0}^{n} \sum_{j=0}^{n} d_{ij} \cdot x_{ij}^k$$

**Constraints:**
1. Each customer visited exactly once:
   $$\sum_{k=1}^{m} \sum_{i=0}^{n} x_{ij}^k = 1 \quad \forall j \in \{1,...,n\}$$

2. Capacity constraint for each route:
   $$\sum_{i=1}^{n} q_i \cdot \left(\sum_{j=0}^{n} x_{ij}^k\right) \leq Q \quad \forall k$$

3. Flow continuity at each node:
   $$\sum_{i=0}^{n} x_{ij}^k = \sum_{i=0}^{n} x_{ji}^k \quad \forall j, k$$

4. Routes start/end at depot:
   $$\sum_{j=1}^{n} x_{0j}^k = 1 \quad \forall k$$

---

## Genetic Algorithm

### Chromosome Representation

**Giant Tour (Permutation) Encoding:**
- Chromosome = ordered list of customer indices $[c_1, c_2, ..., c_n]$
- Each position contains a unique customer ID from 1 to $n$
- Depot (0) implicit at start/end of routes

**Decoding Process:**

```
ALGORITHM: DecodedRoutes ← DecodeChromosome(chromosome, demands, capacity)
  routes ← []
  currentRoute ← [0]                      // Start with depot
  currentLoad ← 0
  
  FOR each customer c IN chromosome DO
    demand ← demands[c]
    IF currentLoad + demand > capacity THEN
      currentRoute.append(0)              // Close current route
      routes.append(currentRoute)
      currentRoute ← [0]                  // Start new route
      currentLoad ← 0
    END IF
    
    currentRoute.append(c)
    currentLoad ← currentLoad + demand
  END FOR
  
  currentRoute.append(0)                  // Close final route
  routes.append(currentRoute)
  RETURN routes
```

**Time Complexity**: $O(n)$ where $n$ is number of customers

### Population Initialization

```
ALGORITHM: InitializePopulation(popSize, numCustomers)
  population ← []
  customers ← [1, 2, ..., numCustomers]
  
  FOR i = 1 TO popSize DO
    chromosome ← Random permutation of customers
    population.append(chromosome)
  END FOR
  
  RETURN population
```

**Complexity**: $O(\text{popSize} \times n \log n)$ for random permutation generation

### Fitness Evaluation

```
ALGORITHM: EvaluateFitness(chromosome, distMatrix, demands, capacity)
  routes ← DecodeChromosome(chromosome, demands, capacity)
  totalDistance ← 0
  
  FOR each route IN routes DO
    routeDistance ← 0
    FOR i = 0 TO length(route)-2 DO
      routeDistance ← routeDistance + distMatrix[route[i]][route[i+1]]
    END FOR
    totalDistance ← totalDistance + routeDistance
  END FOR
  
  RETURN totalDistance
```

**Fitness Strategy**: Lower distance = better fitness (minimization problem)

### Selection: Roulette Wheel

**Principle**: Fitness-proportional selection with inverse mapping

```
ALGORITHM: RouletteWheelSelection(population, fitnessScores)
  maxFitness ← MAX(fitnessScores)
  minFitness ← MIN(fitnessScores)
  
  // Invert fitness (worse = lower probability)
  invertedFitness ← []
  FOR each f IN fitnessScores DO
    invertedFitness.append(maxFitness - f + 1)
  END FOR
  
  totalFitness ← SUM(invertedFitness)
  probabilities ← invertedFitness / totalFitness
  
  selectedIndex ← SelectByProbability(probabilities)
  RETURN population[selectedIndex]
```

**Complexity**: $O(\text{popSize})$ for probability calculation

### Crossover: Order-Based Crossover (OBX)

**Purpose**: Combine genetic material from two parents preserving valid permutations

**Algorithm:**
```
ALGORITHM: OrderBasedCrossover(parent1, parent2)
  n ← length(parent1)
  subsetSize ← n / 2
  
  // Select random subset from parent1
  subsetIndices ← RandomSample(0..n-1, subsetSize)
  subset ← {parent1[i] : i IN subsetIndices}
  
  child ← [NULL] * n
  
  // Place subset at same positions in child
  FOR each i IN subsetIndices DO
    child[i] ← parent1[i]
  END FOR
  
  // Fill remaining positions with parent2's order
  fillPos ← 0
  FOR each customer IN parent2 DO
    IF customer NOT IN subset THEN
      WHILE fillPos < n AND child[fillPos] ≠ NULL DO
        fillPos ← fillPos + 1
      END WHILE
      IF fillPos < n THEN
        child[fillPos] ← customer
      END IF
    END IF
  END FOR
  
  RETURN child
```

**Advantages**:
- Maintains relative order information
- Reduces invalid permutations
- Better convergence for TSP-like problems

### Mutation: Swap Mutation

**Purpose**: Introduce randomness and prevent premature convergence

**Algorithm:**
```
ALGORITHM: SwapMutation(chromosome, mutationRate)
  mutated ← chromosome.copy()
  n ← length(mutated)
  
  numSwaps ← MAX(1, floor(n * mutationRate))
  
  FOR i = 1 TO numSwaps DO
    pos1 ← RandomInt(0, n-1)
    pos2 ← RandomInt(0, n-1), pos2 ≠ pos1
    Swap(mutated[pos1], mutated[pos2])
  END FOR
  
  RETURN mutated
```

**Mutation Rate Effects:**
- Low rate (< 0.05): Slower exploration, premature convergence risk
- Medium rate (0.05-0.15): Balanced exploration and exploitation
- High rate (> 0.15): Excessive disruption, loses good solutions

### GA Evolution Loop

```
ALGORITHM: EvolvationGA(popSize, numGenerations, crossoverRate, mutationRate, eliteSize)
  population ← InitializePopulation(popSize, numCustomers)
  EvaluatePopulation(population)
  
  bestIndividual ← population[BestFitness(population)]
  bestFitness ← Fitness(bestIndividual)
  
  FOR gen = 1 TO numGenerations DO
    // Preserve elite
    sortedIndices ← SortByFitness(population)
    eliteIndices ← sortedIndices[1..eliteSize]
    newPopulation ← [population[i] for i IN eliteIndices]
    
    // Create offspring
    WHILE length(newPopulation) < popSize DO
      parent1 ← RouletteWheelSelection(population)
      parent2 ← RouletteWheelSelection(population)
      
      IF Random() < crossoverRate THEN
        child ← OrderBasedCrossover(parent1, parent2)
      ELSE
        child ← parent1.copy()
      END IF
      
      child ← SwapMutation(child, mutationRate)
      newPopulation.append(child)
    END WHILE
    
    population ← newPopulation[1..popSize]
    EvaluatePopulation(population)
    
    // Update best
    currentBest ← population[BestFitness(population)]
    IF Fitness(currentBest) < bestFitness THEN
      bestIndividual ← currentBest
      bestFitness ← Fitness(currentBest)
    END IF
  END FOR
  
  RETURN bestIndividual, bestFitness
```

**Time Complexity**: $O(\text{numGenerations} \times (\text{popSize} \times n + p \times k))$
- $n$: chromosome length (number of customers)
- $p$: average number of offspring
- $k$: operations per offspring (crossover + mutation)

---

## Tabu Search

### Neighborhood Structure

**Move Definition**: Relocate customer from one route to another

**Move Representation**:
$$\text{Move} = (\text{route}_{\text{from}}, \text{cust\_idx}, \text{route}_{\text{to}}, \text{insert\_pos})$$

**Neighborhood Size**: $O(r^2 \times n)$ where $r$ is number of routes

### Feasibility Checking

```
ALGORITHM: IsRouteFeasible(route, demands, capacity)
  load ← 0
  FOR each customer IN route DO
    IF customer ≠ depot THEN
      load ← load + demands[customer]
    END IF
  END FOR
  
  RETURN load ≤ capacity
```

### Neighborhood Generation

```
ALGORITHM: GenerateNeighborhood(routes, demands, capacity)
  neighbors ← []
  
  FOR fromRouteIdx = 1 TO length(routes) DO
    route ← routes[fromRouteIdx]
    customers ← [c FOR c IN route IF c ≠ depot]
    
    IF length(customers) = 0 THEN CONTINUE END IF
    
    FOR custIdx = 1 TO length(customers) DO
      customer ← customers[custIdx]
      
      FOR toRouteIdx = 1 TO length(routes) DO
        IF toRouteIdx = fromRouteIdx THEN CONTINUE END IF
        
        FOR insertPos = 1 TO length(routes[toRouteIdx]) DO
          newRoutes ← CopyRoutes(routes)
          
          // Remove from source
          newRoutes[fromRouteIdx].remove(customer)
          
          // Check if source route still valid
          IF length(newRoutes[fromRouteIdx]) ≤ 2 THEN CONTINUE END IF
          
          // Insert into target
          newRoutes[toRouteIdx].insert(insertPos, customer)
          
          // Check feasibility
          IF IsRouteFeasible(newRoutes[toRouteIdx], demands, capacity) THEN
            move ← (fromRouteIdx, custIdx, toRouteIdx, insertPos)
            neighbors.append((newRoutes, move))
          END IF
        END FOR
      END FOR
    END FOR
  END FOR
  
  RETURN neighbors
```

**Time Complexity**: $O(r^2 \times n^2 \times m)$ for full evaluation
- $r$: number of routes
- $n$: customers per route (average)
- $m$: distance matrix lookup

### Tabu List Management

**Data Structure**: Dictionary mapping Move → Tenure

```
ALGORITHM: UpdateTabuList(tabuList, newMove, tabuTenure)
  // Decrease all tenures
  FOR move, tenure IN tabuList DO
    tabuList[move] ← tenure - 1
    IF tabuList[move] ≤ 0 THEN
      tabuList.remove(move)
    END IF
  END FOR
  
  // Add new tabu move
  tabuList[newMove] ← tabuTenure
  
  RETURN tabuList
```

**Tabu Tenure**:
- Static: Fixed duration (e.g., 10 iterations)
- Dynamic: Varies based on search progress or random ($\text{tenure} = a + b \times \text{random}$)
- Default: Static tenure of 10 iterations

### Aspiration Criteria

**Mechanism**: Override tabu restriction if move improves best-ever solution

```
ALGORITHM: ShouldAcceptMove(move, neighborDistance, bestDistance, isTabu)
  IF NOT isTabu THEN
    RETURN TRUE
  END IF
  
  // Aspiration: Accept if better than best-ever
  IF neighborDistance < bestDistance THEN
    RETURN TRUE        // Accept despite being tabu
  END IF
  
  RETURN FALSE
```

**Effectiveness**: Allows escaping local optima while preventing cycling

### Tabu Search Iteration

```
ALGORITHM: TabuSearchIteration(currentSolution, tabuList, distMatrix, demands, capacity)
  neighbors ← GenerateNeighborhood(currentSolution, demands, capacity)
  
  // Update tabu tenure
  UpdateTabuList(tabuList)
  
  bestNeighbor ← NULL
  bestNeighborDistance ← INFINITY
  bestNeighborMove ← NULL
  
  FOR (neighbor, move) IN neighbors DO
    neighborDistance ← CalculateDistance(neighbor)
    isTabu ← move IN tabuList
    
    // Check aspiration criteria
    IF isTabu AND neighborDistance < bestDistance THEN
      isTabu ← FALSE
    END IF
    
    // Select best non-tabu neighbor
    IF NOT isTabu AND neighborDistance < bestNeighborDistance THEN
      bestNeighbor ← neighbor
      bestNeighborDistance ← neighborDistance
      bestNeighborMove ← move
    END IF
  END FOR
  
  IF bestNeighbor = NULL THEN
    RETURN currentSolution, currentDistance, "NO_MOVE"
  END IF
  
  // Move to best neighbor
  tabuList[bestNeighborMove] ← tabuTenure
  
  RETURN bestNeighbor, bestNeighborDistance, "MOVED"
```

### Full Tabu Search Algorithm

```
ALGORITHM: TabuSearch(initialSolution, iterations, tabuTenure)
  currentSolution ← initialSolution
  currentDistance ← CalculateDistance(currentSolution)
  
  bestSolution ← currentSolution.copy()
  bestDistance ← currentDistance
  
  tabuList ← {}
  
  FOR iter = 1 TO iterations DO
    currentSolution, currentDistance, status ← TabuSearchIteration(
      currentSolution, tabuList, distMatrix, demands, capacity
    )
    
    IF status = "NO_MOVE" THEN
      BREAK
    END IF
    
    // Update best
    IF currentDistance < bestDistance THEN
      bestSolution ← currentSolution.copy()
      bestDistance ← currentDistance
    END IF
  END FOR
  
  RETURN bestSolution, bestDistance
```

**Time Complexity**: $O(\text{iterations} \times (\text{neighborhood\_generation} + \text{evaluation}))$
- Typically: $O(\text{iterations} \times r^2 \times n)$ for dense neighborhoods

---

## Hybrid Pipeline

### Integration Strategy

**Philosophy**: GA explores solution space globally, TS exploits locally

```
ALGORITHM: HybridGATS(distMatrix, demands, capacity, numCustomers,
                      gaPopSize, gaGenerations, tsIterations,
                      crossoverRate, mutationRate, eliteSize)
  
  // Initialize GA
  gaPopulation ← InitializePopulation(gaPopSize, numCustomers)
  EvaluatePopulation(gaPopulation)
  
  bestSolution ← GetBestIndividual(gaPopulation)
  bestDistance ← CalculateDistance(DecodedRoutes(bestSolution))
  
  history ← {gen: [], ga_best: [], ts_best: [], overall_best: []}
  
  FOR gen = 1 TO gaGenerations DO
    // Step 1: GA Evolution
    gaPopulation ← EvolutionStep(gaPopulation, gaPopSize, crossoverRate,
                                 mutationRate, eliteSize)
    
    gaBestIndividual ← GetBestIndividual(gaPopulation)
    gaBestDistance ← Fitness(gaBestIndividual)
    
    // Step 2: TS Refinement
    gaBestRoutes ← DecodeChromosome(gaBestIndividual)
    tsBestRoutes, tsBestDistance ← TabuSearch(gaBestRoutes, tsIterations)
    
    // Step 3: Track Progress
    history.gen.append(gen)
    history.ga_best.append(gaBestDistance)
    history.ts_best.append(tsBestDistance)
    
    // Step 4: Update Overall Best
    IF tsBestDistance < bestDistance THEN
      bestSolution ← tsBestRoutes
      bestDistance ← tsBestDistance
    END IF
    
    history.overall_best.append(bestDistance)
    
  END FOR
  
  RETURN bestSolution, bestDistance, history
```

### Synergy Effects

1. **GA→TS**: GA provides diverse starting solutions for TS
2. **TS→GA**: Improved solutions guide GA population quality
3. **Mutual Benefit**: Together achieve better results than individually

---

## Complexity Analysis

### Time Complexity Summary

| Component | Complexity | Notes |
|-----------|-----------|-------|
| GA Evaluation | $O(\text{popSize} \times n)$ | Per generation |
| Selection | $O(\text{popSize})$ | Roulette wheel |
| Crossover | $O(n)$ | Order-based |
| Mutation | $O(\text{numSwaps})$ | Typically $O(n)$ |
| TS Neighborhood | $O(r^2 \times n^2)$ | Worst case all routes |
| TS Iteration | $O(r^2 \times n^2 + m)$ | Neighborhood + evaluation |
| **Full GA** | $O(g \times (p \times n))$ | g=gen, p=pop |
| **Full TS** | $O(t \times r^2 \times n^2)$ | t=iterations, r=routes |
| **Hybrid** | $O(g \times (p \times n + t \times r^2 \times n^2))$ | Both combined |

Where:
- $n$ = number of customers
- $p$ = population size
- $g$ = GA generations
- $t$ = TS iterations
- $r$ = number of routes (typically $O(n/\text{capacity})$)
- $m$ = distance matrix operations $O(1)$ lookup

### Space Complexity

| Component | Complexity | Purpose |
|-----------|-----------|---------|
| Distance Matrix | $O(n^2)$ | Random access lookup |
| GA Population | $O(p \times n)$ | Store all chromosomes |
| TS Tabu List | $O(\text{tabuTenure})$ | Store recent moves |
| **Total** | $O(n^2 + p \times n)$ | Dominated by distance matrix |

---

## Convergence Properties

### Theoretical Guarantees

**GA Convergence:**
- Elite preservation ensures monotonic improvement
- Diversity maintained through crossover/mutation
- Not guaranteed to find global optimum (NP-hard problem)

**TS Convergence:**
- Tabu mechanism prevents cycling
- Aspiration criteria allow infinite search (non-convergence by design)
- Can escape local optima through forced moves

### Empirical Convergence

**Expected Behavior:**
1. **Early Phase** (Gen 1-5): Rapid improvement as GA explores
2. **Middle Phase** (Gen 5-12): TS refinement improves plateau solutions
3. **Late Phase** (Gen 12+): Diminishing returns, convergence slowing

**Convergence Indicators:**
- $\Delta \text{fitness} < 0.01\%$ over 5 generations → Near convergence
- All GA individuals similar → Population convergence
- TS cannot improve GA best → Local optimum likely

### Factors Affecting Convergence

| Factor | Impact | Mitigation |
|--------|--------|-----------|
| Population Size | Larger = better diversity | Balance with computation |
| Mutation Rate | Higher = slower convergence | Use medium rate (0.05-0.15) |
| Tabu Tenure | Longer = less cycling | Tune to problem size |
| GA Generations | More = better solutions | Balance with TS iterations |
| TS Iterations | More per gen = higher cost | Typically 10-20 iterations |

---

## Performance Tuning

### For Small Problems (n < 50)
```
- GA Pop: 30-40
- GA Gen: 20-30
- TS Iter: 15-20
- Mutation: 0.1-0.15
- Tabu Tenure: 8-12
```

### For Medium Problems (50 ≤ n < 100)
```
- GA Pop: 40-60
- GA Gen: 30-50
- TS Iter: 20-30
- Mutation: 0.08-0.12
- Tabu Tenure: 10-15
```

### For Large Problems (n ≥ 100)
```
- GA Pop: 60-100
- GA Gen: 50-100
- TS Iter: 30-50
- Mutation: 0.05-0.1
- Tabu Tenure: 15-20
```

---

## References

1. Reeves, C. R. (Ed.). (1993). *Modern heuristic techniques for combinatorial problems*. John Wiley & Sons.
2. Glover, F., & Laguna, M. (1997). *Tabu search*. Kluwer Academic Publishers.
3. Goldberg, D. E. (1989). *Genetic algorithms in search, optimization, and machine learning*. Addison-Wesley.
4. Cordeau, J. F., Gendreau, M., Hertz, A., Laporte, G., & Sormany, J. S. (2005). New heuristics for the vehicle routing problem. Handbook of metaheuristics, 220-250.

