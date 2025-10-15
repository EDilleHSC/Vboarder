#!/bin/bash
# Quick type annotation fix for main.py

echo "🔧 Fixing type annotations in main.py..."

cd /mnt/d/ai/projects/vboarder

# Fix all type annotation issues in one go
sed -i 's/Optional\[str\]/str | None/g' api/main.py
sed -i 's/Optional\[bool\]/bool | None/g' api/main.py
sed -i 's/Optional\[int\]/int | None/g' api/main.py
sed -i 's/Optional\[float\]/float | None/g' api/main.py
sed -i 's/List\[Dict\[str, Any\]\]/list[dict[str, Any]]/g' api/main.py
sed -i 's/List\[str\]/list[str]/g' api/main.py
sed -i 's/Dict\[str, Any\]/dict[str, Any]/g' api/main.py

# Remove unused threading import
sed -i '/import threading/d' api/main.py

# Fix file open mode
sed -i 's/open(registry_path, "r")/open(registry_path)/g' api/main.py

echo "✅ Type annotations fixed!"
