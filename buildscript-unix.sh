
#!/bin/bash
echo "================================"
echo "    DEADLOCK GAME BUILDER"
echo "================================"
echo

echo "[1/5] Cleaning previous builds..."
rm -rf build dist __pycache__

echo "[2/5] Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo "[3/5] Building executable..."
pyinstaller main.spec --clean --noconfirm

echo "[4/5] Copying additional files..."
if [ -d "dist/Deadlock" ]; then
    cp README.md dist/Deadlock/
    cp high_scores.json dist/Deadlock/ 2>/dev/null || true
    echo "Game version info" > dist/Deadlock/version.txt
    echo "Built on $(date)" >> dist/Deadlock/version.txt
fi

echo "[5/5] Build complete!"
echo
echo "================================"
echo "   BUILD SUCCESSFUL!"
echo "================================"
echo "Executable location: dist/Deadlock/Deadlock"
echo

chmod +x build_exe.sh