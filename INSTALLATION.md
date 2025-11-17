# Installation & Setup Guide

Complete step-by-step guide to install and set up the CVRP Hybrid GA+TS project.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Verification](#verification)
4. [Jupyter Setup](#jupyter-setup)
5. [Troubleshooting](#troubleshooting)
6. [Configuration](#configuration)

---

## Prerequisites

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.7 or higher
- **RAM**: 2GB minimum (4GB+ recommended)
- **Disk Space**: 500MB for project + dependencies

### Check Python Installation

```bash
# Check Python version
python --version

# Should output: Python 3.7.x or higher
```

If Python is not installed, download from [python.org](https://www.python.org/downloads/)

---

## Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/jyotsana277/cvrp-oam-project.git

# Navigate to project directory
cd cvrp-oam-project

# Verify you're in correct directory
ls  # On Linux/macOS or dir on Windows
# Should see: README.md, INSTALLATION.md, oam_project_dataset1.ipynb, etc.
```

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies:

#### Windows (PowerShell/CMD)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal
```

#### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list

# Should see: numpy, pandas, matplotlib, openpyxl, jupyter
```

### Individual Package Installation

If you prefer installing packages individually:

```bash
# Core scientific computing
pip install numpy>=1.19.0
pip install pandas>=1.1.0

# Data and file handling
pip install openpyxl>=3.0.0

# Visualization
pip install matplotlib>=3.3.0

# Jupyter for interactive notebooks
pip install jupyter>=1.0.0
```

### Step 4: Verify Installation

```bash
# Test Python imports
python -c "import numpy, pandas, matplotlib, openpyxl; print('✓ All packages installed!')"

# Should output: ✓ All packages installed!
```

---

## Jupyter Setup

### Option 1: Jupyter Notebook (Classic)

```bash
# Start Jupyter Notebook
jupyter notebook

# Browser will open at http://localhost:8888
# Navigate to oam_project_dataset1.ipynb and open it
```

### Option 2: Jupyter Lab (Modern Interface)

```bash
# Install Jupyter Lab (optional)
pip install jupyterlab

# Start Jupyter Lab
jupyter lab

# Browser will open at http://localhost:8888/lab
# Navigate to oam_project_dataset1.ipynb
```

### Option 3: VS Code Integration

**If using VS Code:**

1. Install Python extension (ms-python.python)
2. Install Jupyter extension (ms-toolsai.jupyter)
3. Open notebook file
4. VS Code will suggest installing Jupyter components
5. Click "Install" and wait for completion

---

## Verification

### Test 1: Import All Components

```python
# Run this in a Python shell or Jupyter cell
from oam_project_dataset1 import (
    load_mdrp_format,
    compute_distance_matrix,
    GeneticAlgorithm,
    TabuSearch,
    HybridGATS,
    check_solution_feasibility
)

print("✓ All components imported successfully!")
```

### Test 2: Load Sample Data

```python
# Load dataset
depots, coords, demands = load_mdrp_format(
    "19MDVRP Problem Sets.xlsx", 
    sheet="Problem 7"
)

print(f"✓ Loaded {len(coords)} customers")
print(f"✓ Depots: {depots.shape}")
print(f"✓ Demands shape: {demands.shape}")
```

### Test 3: Run Mini Optimization

```python
# Quick test run
dist_matrix = compute_distance_matrix(coords)

hybrid = HybridGATS(
    dist=dist_matrix,
    demands=demands,
    capacity=1000,
    num_customers=len(coords)
)

# Run with minimal parameters for quick test
best_routes, best_dist, history = hybrid.run(
    ga_pop_size=10,
    ga_generations=2,
    ts_iterations=5
)

print(f"✓ Quick test passed!")
print(f"✓ Best distance: {best_dist:.2f}")
```

---

## Configuration

### Environment Variables (Optional)

Create a `.env` file in project root for custom settings:

```env
# Dataset path (optional)
DATASET_PATH=19MDVRP Problem Sets.xlsx

# Default sheet name
DATASET_SHEET=Problem 7

# Default vehicle capacity
VEHICLE_CAPACITY=1000

# Logging level (DEBUG, INFO, WARNING)
LOG_LEVEL=INFO
```

### Python Path Configuration

If importing from different directory:

```python
import sys
sys.path.insert(0, '/path/to/cvrp-oam-project')

# Now can import
from oam_project_dataset1 import HybridGATS
```

---

## Platform-Specific Notes

### Windows

```powershell
# In PowerShell, if activation fails, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate venv again:
venv\Scripts\activate
```

### macOS

```bash
# If using Homebrew Python, ensure it's set as default:
brew install python3

# Verify:
which python3
```

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies first
sudo apt-get install python3-dev python3-venv

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

### Linux (Fedora/RHEL)

```bash
# Install system dependencies
sudo dnf install python3-devel

# Create and activate venv
python3 -m venv venv
source venv/bin/activate
```

---

## Docker Setup (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Run Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--allow-root"]
```

### Build and Run

```bash
# Build image
docker build -t cvrp-optimizer .

# Run container
docker run -p 8888:8888 -v $(pwd):/app cvrp-optimizer

# Access at http://localhost:8888
```

---

## Troubleshooting

### Issue: Python not found

**Solution:**
```bash
# Windows: Use python or py
python --version

# macOS/Linux: Use python3
python3 --version

# Or set alias
alias python=python3
```

### Issue: pip not found

**Solution:**
```bash
# Try with python module
python -m pip install -r requirements.txt

# Or use pip3
pip3 install -r requirements.txt
```

### Issue: Permission denied (macOS/Linux)

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: ModuleNotFoundError when importing

**Solution:**
```bash
# Ensure you're in project directory
cd cvrp-oam-project

# Verify packages installed
pip list | grep numpy

# Reinstall if needed
pip install --upgrade -r requirements.txt
```

### Issue: Jupyter kernel not found

**Solution:**
```bash
# Install ipykernel
pip install ipykernel

# Install kernel for virtual environment
python -m ipykernel install --user --name=cvrp-env

# Restart Jupyter and select kernel from dropdown
```

### Issue: Excel file not found

**Solution:**
```bash
# Verify file exists in project directory
ls 19MDVRP*

# Or check full path
import os
print(os.path.abspath("19MDVRP Problem Sets.xlsx"))

# Ensure filename matches exactly (case-sensitive on Linux)
```

### Issue: Memory error on large problems

**Solution:**
```python
# Reduce population size
hybrid.run(ga_pop_size=20, ga_generations=10)

# Or use smaller dataset
depots, coords, demands = load_mdrp_format(sheet="Problem 5")
```

---

## Verification Checklist

- [ ] Python 3.7+ installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] requirements.txt installed
- [ ] All imports working
- [ ] Sample data loaded
- [ ] Mini optimization test passed
- [ ] Jupyter notebook opens successfully
- [ ] Dataset file accessible

---

## Next Steps

1. **Quick Start**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. **Usage Guide**: See [USAGE.md](USAGE.md)
3. **Run Example**: Open `oam_project_dataset1.ipynb` in Jupyter
4. **Learn Algorithm**: See [ALGORITHM.md](ALGORITHM.md)

---

## Getting Help

| Issue | Resource |
|-------|----------|
| Installation | This file |
| Quick help | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Usage examples | [USAGE.md](USAGE.md) |
| API details | [API.md](API.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install/upgrade packages
pip install --upgrade -r requirements.txt

# Run tests
python -m pytest tests/

# Start Jupyter
jupyter notebook

# Deactivate virtual environment
deactivate
```

---

**Installation complete!** Ready to run the optimization? Start with the [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or open the Jupyter notebook.

