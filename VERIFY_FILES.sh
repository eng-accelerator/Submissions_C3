#!/bin/bash
# Script to verify all files including hidden .streamlit directory

echo "🔍 Checking deploy_hf directory for all files..."
echo ""

cd "$(dirname "$0")"

echo "📁 All files (including hidden):"
ls -la

echo ""
echo "📁 .streamlit directory:"
if [ -d ".streamlit" ]; then
    echo "✅ .streamlit directory EXISTS"
    ls -la .streamlit/
    echo ""
    echo "📄 Contents of .streamlit/config.toml:"
    cat .streamlit/config.toml
else
    echo "❌ .streamlit directory NOT FOUND"
fi

echo ""
echo "📊 File count:"
echo "Total files: $(find . -type f | wc -l | tr -d ' ')"
echo "Python files: $(find . -type f -name "*.py" | wc -l | tr -d ' ')"
echo "Config files: $(find . -type f \( -name "*.toml" -o -name "*.json" -o -name "Dockerfile" -o -name "requirements.txt" \) | wc -l | tr -d ' ')"
