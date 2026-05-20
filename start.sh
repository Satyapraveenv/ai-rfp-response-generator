#!/bin/bash
# AI RFP Response Generator — Quick Start
cd "$(dirname "$0")"
echo "🚀 Starting AI RFP Response Generator..."
echo "   Open http://localhost:8501 in your browser"
echo "   Press Ctrl+C to stop"
echo ""
streamlit run app.py --server.port 8501
