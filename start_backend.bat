@echo off
echo Starting Farm Security Backend...
cd farm_security_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
