#!/bin/bash
# Run all three algorithms for comparison

echo "🚀 Multi-Cloud Workload Optimization - Algorithm Comparison"
echo "================================================================"
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
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Create data symlink if needed
if [ ! -d "data" ]; then
    echo "🔗 Creating data symlinks..."
    ln -s ~/thesis/data data
    echo "✅ Data linked"
fi

# Run all three algorithms
echo ""
echo "🧬 Running ALL three algorithms (NSGA-II, MOEA/D, SPEA2)..."
echo "This will take approximately 5-10 minutes..."
echo ""

python main.py \
    --algorithm all \
    --population 50 \
    --generations 100 \
    --output-dir results

echo ""
echo "✅ Complete! Check results/ directory:"
echo "  - results/nsga2/     (NSGA-II outputs)"
echo "  - results/moead/     (MOEA/D outputs)"
echo "  - results/spea2/     (SPEA2 outputs)"
echo ""
echo "To view comparisons:"
echo "  - cat results/nsga2/solutions.csv"
echo "  - cat results/moead/solutions.csv"
echo "  - cat results/spea2/solutions.csv"
