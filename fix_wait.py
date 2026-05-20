import re

def update_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    wait_loop = """          for i in $(seq 1 30); do
            PYPI_JSON=$(curl -sf "https://pypi.org/pypi/gemstack/$VERSION/json" || echo "")
            if [ -n "$PYPI_JSON" ]; then
              # Check if sdist is present (and bdist_wheel for release)
              if echo "$PYPI_JSON" | python3 -c "import sys,json; data=json.load(sys.stdin); sys.exit(0 if any(u['packagetype']=='sdist' for u in data.get('urls', [])) else 1)" 2>/dev/null; then
                echo "✅ Package and sdist available on PyPI"
                exit 0
              fi
            fi
            echo "  Attempt $i/30 — waiting 10s..."
            sleep 10
          done"""
          
    # Replace the old loop
    # In release.yml
    if "release.yml" in filepath:
        old_loop = """          for i in $(seq 1 30); do
            if curl -sf "https://pypi.org/pypi/gemstack/$VERSION/json" > /dev/null 2>&1; then
              echo "✅ Package available on PyPI"
              exit 0
            fi
            echo "  Attempt $i/30 — waiting 10s..."
            sleep 10
          done"""
    else:
        old_loop = """          for i in $(seq 1 30); do
            if curl -sf "https://pypi.org/pypi/gemstack/$VERSION/json" > /dev/null 2>&1; then
              echo "Package available on PyPI"
              exit 0
            fi
            echo "Attempt $i/30 — waiting 10s..."
            sleep 10
          done"""

    if old_loop in content:
        content = content.replace(old_loop, wait_loop)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"Loop not found in {filepath}")

update_file(".github/workflows/release.yml")
update_file(".github/workflows/update-formula.yml")
