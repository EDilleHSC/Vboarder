#!/bin/bash
# Clean up remaining issues

cd /mnt/d/ai/projects/vboarder

echo "🔧 Final cleanup of api/main.py..."

# Fix the remaining Optional instances one by one
python3 << 'EOF'
import re

# Read the file
with open('api/main.py', 'r') as f:
    content = f.read()

# Fix all remaining Optional patterns
content = re.sub(r'Optional\[str\]', 'str | None', content)
content = re.sub(r'Optional\[int\]', 'int | None', content)
content = re.sub(r'Optional\[float\]', 'float | None', content)
content = re.sub(r'Optional\[bool\]', 'bool | None', content)

# Remove any threading import if still there
content = re.sub(r'\s+import threading\n', '\n', content)

# Fix exception chaining
content = re.sub(
    r'raise HTTPException\(status_code=400, detail=str\(exc\)\)',
    'raise HTTPException(status_code=400, detail=str(exc)) from exc',
    content
)
content = re.sub(
    r'raise HTTPException\(status_code=404, detail=str\(exc\)\)',
    'raise HTTPException(status_code=404, detail=str(exc)) from exc',
    content
)
content = re.sub(
    r'raise HTTPException\(\s+status_code=500, detail="An unexpected error occurred during processing."\s+\)',
    'raise HTTPException(status_code=500, detail="An unexpected error occurred during processing.") from None',
    content
)

# Write back
with open('api/main.py', 'w') as f:
    f.write(content)

print("✅ Fixed remaining type annotations and exception handling")
EOF

echo "🧹 Cleanup complete!"
