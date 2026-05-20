#!/bin/bash
# Quick start script for running optimization

echo "🚀 Multi-Cloud Workload Optimization"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import numpy" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Create symlinks to data files
if [ ! -d "data" ]; then
    echo "🔗 Creating data symlinks..."
    ln -s ~/thesis/data data
    echo "✅ Data linked"
fi

# Run optimization
echo ""
echo "🧬 Running NSGA-II optimization..."
echo ""

python main.py \
    --algorithm nsga2 \
    --population 50 \
    --generations 100 \
    --output-dir results

echo ""
echo "✅ Complete! Check results/ directory for outputs"
echo ""
echo "To view results:"
echo "  - Pareto front: open results/pareto_front_nsga2.png"
echo "  - Solutions: cat results/solutions_nsga2.csv"
echo "  - Convergence: open results/convergence_nsga2.png"
