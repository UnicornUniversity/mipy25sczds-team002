@echo off
echo ================================
echo    DEADLOCK GAME BUILDER
echo ================================
echo.

echo [1/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo [2/5] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo [3/5] Building executable...
pyinstaller main.spec --clean --noconfirm

echo [4/5] Copying additional files...
if exist "dist\Deadlock" (
    copy "README.md" "dist\Deadlock\"
    copy "high_scores.json" "dist\Deadlock\" 2>nul
    echo Game version info > "dist\Deadlock\version.txt"
    echo Built on %date% %time% >> "dist\Deadlock\version.txt"
)

echo [5/5] Build complete!
echo.
echo ================================
echo   BUILD SUCCESSFUL!
echo ================================
echo Executable location: dist\Deadlock\Deadlock.exe
echo.
pause