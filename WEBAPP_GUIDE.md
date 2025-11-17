# 🚚 CVRP Optimizer - Web App Guide

## Quick Start

### 1. Install Streamlit
```powershell
pip install streamlit
```

Or install all dependencies:
```powershell
pip install -r requirements.txt
```

### 2. Run the Web App
```powershell
streamlit run app.py
```

This will:
- Open a browser at `http://localhost:8501`
- Display the interactive dashboard
- Allow you to configure and run the optimization in real-time

### 3. Using the App

**Left Sidebar - Configuration:**
- Adjust GA population size (10-100)
- Set number of generations (5-50)
- Configure Tabu Search iterations (5-50)
- Tune genetic operators (crossover, mutation rates)
- Set vehicle capacity
- Select problem instance

**Main Panel - Optimization:**
- View problem summary statistics
- Click "Run Optimization" button
- Watch progress bar
- See real-time convergence plot
- View detailed routes
- Download results as CSV

### Features

✅ **Interactive Controls**
- Real-time parameter adjustment
- Live progress tracking
- Instant result visualization

📊 **Comprehensive Analysis**
- Convergence curves (GA, TS, Overall)
- Detailed route breakdown
- Performance metrics
- Improvement percentage

💾 **Export Options**
- Download routes as CSV
- Easy integration with other tools

### Example Workflow

1. **Load Problem:** Select Problem 7 from sidebar
2. **Configure:** Adjust population size to 50, generations to 20
3. **Run:** Click "Run Optimization"
4. **Analyze:** View convergence plot and routes
5. **Export:** Download results

### Troubleshooting

**"File not found" error:**
- Make sure `19MDVRP Problem Sets.xlsx` is in the project directory

**Streamlit not found:**
```powershell
pip install streamlit>=1.28.0
```

**Port already in use:**
```powershell
streamlit run app.py --server.port 8502
```

**Clear Streamlit cache:**
```powershell
streamlit cache clear
```

### Performance Tips

- **Faster results:** Reduce GA generations (e.g., 10 instead of 20)
- **Better quality:** Increase population size and generations
- **Fine-tuning:** Adjust crossover/mutation rates

### System Requirements

- Python 3.7+
- 4GB RAM minimum
- 100MB disk space

### Browser Compatibility

- Chrome ✅
- Firefox ✅
- Safari ✅
- Edge ✅

---

For detailed algorithm documentation, see:
- `GA_IMPLEMENTATION.md` - Genetic Algorithm details
- `TABU_SEARCH_IMPLEMENTATION.md` - Tabu Search details
- `HYBRID_GA_TABU_GUIDE.md` - Integration strategy
