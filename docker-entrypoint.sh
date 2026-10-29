#!/usr/bin/env bash
set -e

echo "================================================"
echo "  Drishti DocVision AI  ·  Trendline Titans"
echo "================================================"
echo "Starting Streamlit on port ${STREAMLIT_SERVER_PORT:-8501}..."

# Pre-create directories that the app may write to
mkdir -p /app/data/tmp /app/data/samples

exec "$@"
