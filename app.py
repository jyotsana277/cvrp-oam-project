"""
Interactive Streamlit Web App for CVRP Optimization using Hybrid GA + Tabu Search
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
import random
from typing import List, Tuple

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CVRP Optimizer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_mdrp_format(path="19MDVRP Problem Sets.xlsx", sheet="Problem 7"):
    """Load MDRP/CVRP data from Excel file"""
    df = pd.read_excel(path, sheet_name=sheet)
    
    # Extract depot and customer coordinates
    depot_df = df[df['Depot x coordinate'].notna()]
    depots = depot_df[['Depot x coordinate', 'Depot y coordinate']].to_numpy()
    
    cust_df = df[df['Customer Number'].notna()]
    customers = cust_df[['x coordinate', 'y coordinate']].to_numpy()
    
    demands = np.ones(len(customers), dtype=int)
    
    return depots, customers, demands


def compute_distance_matrix(coords):
    """Compute Euclidean distance matrix"""
    n = len(coords)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist[i, j] = sqrt((coords[i][0] - coords[j][0])**2 + 
                            (coords[i][1] - coords[j][1])**2)
    return dist


def check_solution_feasibility(solution, demands, capacity):
    """Check if all routes respect capacity constraints"""
    for route in solution:
        route_customers = [c for c in route if c != 0]
        if sum(demands[c] for c in route_customers) > capacity:
            return False
    return True


# ============================================================================
# GENETIC ALGORITHM
# ============================================================================

class GeneticAlgorithm:
    """Genetic Algorithm for CVRP"""
    
    def __init__(self, dist, demands, capacity, depot=0, num_customers=None):
        self.dist = dist
        self.demands = demands
        self.capacity = capacity
        self.depot = depot
        self.num_customers = num_customers or len(demands)
        
        self.population = []
        self.fitness_scores = []
        self.best_individual = None
        self.best_fitness = float('inf')
        
    def initialize_population(self, pop_size):
        """Initialize random population"""
        self.population = []
        customers = list(range(0, self.num_customers))
        
        for _ in range(pop_size):
            chromosome = customers.copy()
            random.shuffle(chromosome)
            self.population.append(chromosome)
        
        return self.population
    
    def decode_chromosome(self, chromosome):
        """Convert giant tour to feasible routes"""
        routes = []
        current_route = [self.depot]
        current_load = 0
        
        for cust in chromosome:
            demand = self.demands[cust]
            
            if current_load + demand > self.capacity:
                current_route.append(self.depot)
                routes.append(current_route)
                current_route = [self.depot]
                current_load = 0
            
            current_route.append(cust)
            current_load += demand
        
        current_route.append(self.depot)
        routes.append(current_route)
        
        return routes
    
    def evaluate_fitness(self, chromosome):
        """Calculate total distance"""
        routes = self.decode_chromosome(chromosome)
        total_distance = 0
        
        for route in routes:
            for i in range(len(route) - 1):
                a, b = route[i], route[i + 1]
                total_distance += self.dist[a, b]
        
        return total_distance
    
    def evaluate_population(self):
        """Evaluate all individuals"""
        self.fitness_scores = []
        
        for chromosome in self.population:
            fitness = self.evaluate_fitness(chromosome)
            self.fitness_scores.append(fitness)
            
            if fitness < self.best_fitness:
                self.best_fitness = fitness
                self.best_individual = chromosome.copy()
    
    def roulette_wheel_selection(self):
        """Select parent using fitness-proportional selection"""
        max_fitness = max(self.fitness_scores)
        min_fitness = min(self.fitness_scores)
        
        if max_fitness == min_fitness:
            return random.choice(self.population)
        
        inverted_fitness = [max_fitness - f + 1 for f in self.fitness_scores]
        total = sum(inverted_fitness)
        probabilities = [f / total for f in inverted_fitness]
        
        selected_idx = np.random.choice(len(self.population), p=probabilities)
        return self.population[selected_idx].copy()
    
    def crossover_order_based(self, parent1, parent2):
        """Order-Based Crossover"""
        n = len(parent1)
        subset_size = n // 2
        subset_idx = sorted(random.sample(range(n), subset_size))
        subset = {parent1[i]: i for i in subset_idx}
        
        child = [None] * n
        
        for idx in subset_idx:
            child[idx] = parent1[idx]
        
        fill_pos = 0
        for cust in parent2:
            if cust not in subset:
                while fill_pos < n and child[fill_pos] is not None:
                    fill_pos += 1
                if fill_pos < n:
                    child[fill_pos] = cust
        
        return child
    
    def mutation_swap(self, chromosome, mutation_rate=0.1):
        """Swap mutation"""
        mutated = chromosome.copy()
        n = len(mutated)
        
        for _ in range(max(1, int(n * mutation_rate))):
            i, j = random.sample(range(n), 2)
            mutated[i], mutated[j] = mutated[j], mutated[i]
        
        return mutated
    
    def evolve(self, pop_size, generations, crossover_rate=0.8, mutation_rate=0.1, elite_size=2):
        """Run GA evolution"""
        self.initialize_population(pop_size)
        self.evaluate_population()
        
        fitness_history = [self.best_fitness]
        
        for gen in range(generations):
            sorted_idx = sorted(range(len(self.fitness_scores)), 
                              key=lambda i: self.fitness_scores[i])
            elite_idx = sorted_idx[:elite_size]
            
            new_population = [self.population[i].copy() for i in elite_idx]
            
            while len(new_population) < pop_size:
                parent1 = self.roulette_wheel_selection()
                parent2 = self.roulette_wheel_selection()
                
                if random.random() < crossover_rate:
                    child = self.crossover_order_based(parent1, parent2)
                else:
                    child = parent1.copy()
                
                child = self.mutation_swap(child, mutation_rate)
                new_population.append(child)
            
            self.population = new_population[:pop_size]
            self.evaluate_population()
            fitness_history.append(self.best_fitness)
        
        return self.best_individual, fitness_history
    
    def get_best_routes(self):
        """Get best routes"""
        return self.decode_chromosome(self.best_individual)


# ============================================================================
# TABU SEARCH
# ============================================================================

class TabuSearch:
    """Tabu Search for CVRP refinement"""
    
    def __init__(self, dist, demands, capacity, depot=0):
        self.dist = dist
        self.demands = demands
        self.capacity = capacity
        self.depot = depot
        self.tabu_list = {}
        self.tabu_tenure = 10
        
    def calculate_routes_distance(self, routes):
        """Calculate total distance"""
        total = 0
        for route in routes:
            for i in range(len(route) - 1):
                a, b = route[i], route[i + 1]
                total += self.dist[a, b]
        return total
    
    def is_route_feasible(self, route):
        """Check capacity constraint"""
        load = sum(self.demands[c] for c in route if c != self.depot)
        return load <= self.capacity
    
    def generate_neighborhood(self, routes):
        """Generate neighbor solutions"""
        neighbors = []
        
        for from_route_idx in range(len(routes)):
            route = routes[from_route_idx]
            customers_in_route = route[1:-1]
            
            if not customers_in_route:
                continue
            
            for cust_pos, cust in enumerate(customers_in_route):
                for to_route_idx in range(len(routes)):
                    if to_route_idx == from_route_idx:
                        continue
                    
                    to_route = routes[to_route_idx]
                    
                    for insert_pos in range(1, len(to_route)):
                        new_routes = [r.copy() for r in routes]
                        cust_actual_pos = cust_pos + 1
                        new_routes[from_route_idx].pop(cust_actual_pos)
                        
                        if len(new_routes[from_route_idx]) <= 2:
                            continue
                        
                        new_routes[to_route_idx].insert(insert_pos, cust)
                        
                        if self.is_route_feasible(new_routes[to_route_idx]):
                            move = (from_route_idx, cust_pos, to_route_idx, insert_pos)
                            neighbors.append((new_routes, move))
        
        return neighbors
    
    def refine_solution(self, routes, iterations=20):
        """Apply Tabu Search refinement"""
        current_routes = [r.copy() for r in routes]
        current_distance = self.calculate_routes_distance(current_routes)
        
        best_routes = [r.copy() for r in current_routes]
        best_distance = current_distance
        
        self.tabu_list.clear()
        
        for iteration in range(iterations):
            neighbors = self.generate_neighborhood(current_routes)
            
            if not neighbors:
                break
            
            self.tabu_list = {move: tenure - 1 for move, tenure in self.tabu_list.items() if tenure > 1}
            
            best_neighbor_routes = None
            best_neighbor_distance = float('inf')
            best_neighbor_move = None
            
            for neighbor_routes, move in neighbors:
                neighbor_distance = self.calculate_routes_distance(neighbor_routes)
                is_tabu = move in self.tabu_list
                
                if is_tabu and neighbor_distance < best_distance:
                    is_tabu = False
                
                if not is_tabu and neighbor_distance < best_neighbor_distance:
                    best_neighbor_distance = neighbor_distance
                    best_neighbor_routes = neighbor_routes
                    best_neighbor_move = move
            
            if best_neighbor_routes is None:
                break
            
            current_routes = best_neighbor_routes
            current_distance = best_neighbor_distance
            
            if best_neighbor_move:
                self.tabu_list[best_neighbor_move] = self.tabu_tenure
            
            if current_distance < best_distance:
                best_distance = current_distance
                best_routes = [r.copy() for r in current_routes]
        
        return best_routes, best_distance


# ============================================================================
# HYBRID ALGORITHM
# ============================================================================

class HybridGATS:
    """Hybrid GA + TS Pipeline"""
    
    def __init__(self, dist, demands, capacity, depot=0, num_customers=None):
        self.dist = dist
        self.demands = demands
        self.capacity = capacity
        self.depot = depot
        self.num_customers = num_customers or len(demands)
        
        self.ga = GeneticAlgorithm(dist, demands, capacity, depot, num_customers)
        self.ts = TabuSearch(dist, demands, capacity, depot)
        
        self.best_solution = None
        self.best_distance = float('inf')
        self.history = {'gen': [], 'ga_best': [], 'ts_best': [], 'overall_best': []}
        
    def run(self, ga_pop_size=50, ga_generations=30, ts_iterations=15, 
            crossover_rate=0.8, mutation_rate=0.1, elite_size=2, progress_bar=None):
        """Run hybrid algorithm"""
        self.ga.initialize_population(ga_pop_size)
        self.ga.evaluate_population()
        
        self.best_distance = self.ga.best_fitness
        self.best_solution = self.ga.get_best_routes()
        
        for gen in range(ga_generations):
            # GA step
            sorted_idx = sorted(range(len(self.ga.fitness_scores)), 
                              key=lambda i: self.ga.fitness_scores[i])
            elite_idx = sorted_idx[:elite_size]
            
            new_population = [self.ga.population[i].copy() for i in elite_idx]
            
            while len(new_population) < ga_pop_size:
                parent1 = self.ga.roulette_wheel_selection()
                parent2 = self.ga.roulette_wheel_selection()
                
                if np.random.random() < crossover_rate:
                    child = self.ga.crossover_order_based(parent1, parent2)
                else:
                    child = parent1.copy()
                
                child = self.ga.mutation_swap(child, mutation_rate)
                new_population.append(child)
            
            self.ga.population = new_population[:ga_pop_size]
            self.ga.evaluate_population()
            
            # TS step
            ga_best_routes = self.ga.get_best_routes()
            ts_best_routes, ts_best_distance = self.ts.refine_solution(ga_best_routes, ts_iterations)
            
            if ts_best_distance < self.best_distance:
                self.best_distance = ts_best_distance
                self.best_solution = ts_best_routes
            
            self.history['gen'].append(gen + 1)
            self.history['ga_best'].append(self.ga.best_fitness)
            self.history['ts_best'].append(ts_best_distance)
            self.history['overall_best'].append(self.best_distance)
            
            if progress_bar:
                progress_bar.progress((gen + 1) / ga_generations)
        
        return self.best_solution, self.best_distance, self.history


# ============================================================================
# STREAMLIT APP
# ============================================================================

st.markdown("# 🚚 CVRP Optimizer - Hybrid GA + Tabu Search")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        ga_pop_size = st.slider("GA Population Size", 10, 100, 40, step=10)
        ga_generations = st.slider("GA Generations", 5, 50, 15, step=5)
    
    with col2:
        ts_iterations = st.slider("TS Iterations", 5, 50, 15, step=5)
        crossover_rate = st.slider("Crossover Rate", 0.5, 1.0, 0.8, step=0.05)
    
    mutation_rate = st.slider("Mutation Rate", 0.01, 0.3, 0.1, step=0.02)
    vehicle_capacity = st.number_input("Vehicle Capacity", 500, 2000, 1000, step=100)
    
    st.markdown("---")
    st.markdown("### 📊 Problem Instance")
    problem_sheet = st.selectbox("Select Problem", ["Problem 7", "Problem 8", "Problem 9"])

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📋 Problem Summary")
    
    try:
        # Load data
        depots, coords, demands = load_mdrp_format("19MDVRP Problem Sets.xlsx", sheet=problem_sheet)
        dist_matrix = compute_distance_matrix(coords)
        
        # Display stats
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Customers", len(coords))
        with metric_col2:
            st.metric("Depots", len(depots))
        with metric_col3:
            st.metric("Capacity", vehicle_capacity)
        with metric_col4:
            st.metric("Distance Unit", "Euclidean")
        
        # Run optimization
        if st.button("🚀 Run Optimization", use_container_width=True):
            st.info("⏳ Running hybrid GA + TS optimization...")
            progress_bar = st.progress(0)
            
            hybrid = HybridGATS(
                dist=dist_matrix,
                demands=demands,
                capacity=vehicle_capacity,
                num_customers=len(coords)
            )
            
            best_routes, best_distance, history = hybrid.run(
                ga_pop_size=ga_pop_size,
                ga_generations=ga_generations,
                ts_iterations=ts_iterations,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                elite_size=2,
                progress_bar=progress_bar
            )
            
            st.success("✅ Optimization complete!")
            
            # Display results
            st.markdown("### 📈 Results")
            
            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.metric("Best Distance", f"{best_distance:.2f}")
            with result_col2:
                st.metric("Number of Routes", len(best_routes))
            with result_col3:
                improvement = ((history['overall_best'][0] - best_distance) / history['overall_best'][0]) * 100
                st.metric("Improvement", f"{improvement:.1f}%")
            
            # Convergence plot
            st.markdown("### 📊 Convergence Analysis")
            
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(history['gen'], history['ga_best'], marker='o', label='GA Best', linewidth=2)
            ax.plot(history['gen'], history['ts_best'], marker='s', label='TS Refined', linewidth=2)
            ax.plot(history['gen'], history['overall_best'], marker='^', label='Overall Best', 
                   linewidth=2.5, color='red')
            ax.set_xlabel('Generation', fontweight='bold')
            ax.set_ylabel('Distance', fontweight='bold')
            ax.set_title('Hybrid GA + TS Convergence', fontweight='bold', fontsize=14)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Route details
            st.markdown("### 🛣️ Detailed Routes")
            
            total_load = 0
            for i, route in enumerate(best_routes):
                customers = [c for c in route if c != 0]
                route_load = sum(demands[c] for c in customers)
                total_load += route_load
                
                route_distance = 0
                for j in range(len(route) - 1):
                    route_distance += dist_matrix[route[j], route[j+1]]
                
                with st.expander(f"Route {i+1} (Load: {route_load}/{vehicle_capacity}, Distance: {route_distance:.2f})"):
                    st.write(f"**Path:** {' → '.join(map(str, route))}")
                    st.write(f"**Customers:** {customers}")
                    st.write(f"**Load:** {route_load} / {vehicle_capacity}")
                    st.write(f"**Distance:** {route_distance:.2f}")
            
            st.metric("Total Load", f"{total_load}")
            
            # Export results
            st.markdown("### 💾 Export Results")
            
            routes_df = pd.DataFrame({
                'Route_ID': range(1, len(best_routes) + 1),
                'Path': [str(r) for r in best_routes],
                'Distance': [sum(dist_matrix[best_routes[i][j], best_routes[i][j+1]] 
                                for j in range(len(best_routes[i])-1)) 
                            for i in range(len(best_routes))]
            })
            
            csv = routes_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Routes (CSV)",
                data=csv,
                file_name="cvrp_routes.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Make sure '19MDVRP Problem Sets.xlsx' is in the project directory.")

with col2:
    st.markdown("### ℹ️ Information")
    st.info("""
    **Hybrid Algorithm Overview:**
    
    1. **Genetic Algorithm (GA):** Global search using evolutionary operators
    2. **Tabu Search (TS):** Local refinement with memory
    3. **Integration:** GA generates, TS refines each generation
    
    **Key Features:**
    - Fitness-proportional selection
    - Order-Based Crossover (OBX)
    - Swap mutation
    - Customer relocation moves
    - Aspiration criteria
    """)

# Footer
st.markdown("---")
st.markdown("#### 📚 References")
st.markdown("""
- Cordeau, J. F., et al. (2007). Recent Advances in the Vehicle Routing Problem
- Blum, C., & Roli, A. (2003). Metaheuristics in combinatorial optimization
- Built with [Streamlit](https://streamlit.io/)
""")
