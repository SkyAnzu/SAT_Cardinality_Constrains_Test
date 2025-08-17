#!/bin/bash
# Auto Test Script for CBP - Linux/Mac Shell
# Run automatic test for Cyclic Bandwidth Problem

echo "========================================"
echo "  CBP Auto Test Script (Linux/Mac)"  
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo " Python not found! Please install Python."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo " Python is ready ($PYTHON_CMD)"

# Check required files
required_files=("auto_test.py" "dataset_loader.py" "ver_2.py")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo " $file not found"
        exit 1
    fi
done

echo " All required files are ready"

# Check Dataset directory
if [ ! -d "Dataset" ]; then
    echo " Dataset directory not found"
    echo " Please create Dataset directory and place .mtx files there"
    exit 1
fi

# Check .mtx files in Dataset
mtx_count=$(find Dataset -maxdepth 1 \( -name "*.mtx" -o -name "*.mtx.gz" \) | wc -l)

if [ "$mtx_count" -eq 0 ]; then
    echo " No .mtx or .mtx.gz files found in Dataset directory"
    echo " Please place data files in Dataset directory"
    exit 1
fi

echo " Found $mtx_count data files"

# Create results directory if it doesn't exist
mkdir -p results

# Run test
echo ""
echo " Starting auto test..."
echo " This process may take several minutes..."
echo ""

$PYTHON_CMD auto_test.py

# Check results
if [ $? -eq 0 ]; then
    echo ""
    echo " Test completed successfully!"
    echo " Check CSV result file in current directory"
    
    # Move CSV files to results directory (optional)
    find . -maxdepth 1 -name "cbp_test_results_*.csv" -exec mv {} results/ \;
    
    echo " Result files have been moved to 'results/' directory"
else
    echo ""
    echo " Test encountered an error!"
    exit 1
fi

echo ""
echo "  Completed!"
