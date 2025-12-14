@echo off
REM Install PyTorch CPU-only version for Windows compatibility
REM This avoids DLL loading issues with CUDA-enabled PyTorch

echo Installing PyTorch CPU-only version...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo PyTorch CPU installation complete!
echo You can now install the remaining requirements:
echo pip install -r requirements.txt


