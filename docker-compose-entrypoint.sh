#!/bin/bash
# Wrapper script for docker-compose - Runs FRESH authentication before pipeline
# Forces re-login on every execution to ensure session validity
set -e
cd /app

echo "============================================================"
echo "🔐 AUTHENTICATION CHECK (FRESH LOGIN)"
echo "============================================================"

# Always force a fresh login - never reuse saved cookies
python3 -c "
import sys
sys.path.insert(0, '/app')
exec(open('/app/src/auth_check.py').read())
" || {
    echo "❌ FRESH authentication failed - stopping pipeline"
    exit 1
}

echo ""
echo "✅ Fresh auth verified! Running full pipeline..."
echo "============================================================"

# Now run the main scraping and building pipeline
exec python3 main.py