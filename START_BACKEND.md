# How to Start the Backend Server

## Option 1: Using Python directly
```bash
cd farm_security_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Option 2: Using the main module
```bash
cd farm_security_backend
python -m app
```

## Option 3: Direct run
```bash
cd farm_security_backend
python app/__main__.py
```

## What you should see:
```
📁 Database location: D:\farm security\farm_security_backend\farm_security.db
✅ YOLOv8 Model Loaded from ...
INFO:     Started server process
INFO:     Waiting for application startup.
Camera processing thread started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Then test the API:
Open browser: http://localhost:8000/alerts

You should see JSON with your detection logs.

## Common Issues:

### Port already in use
If port 8000 is busy, change it:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
Then update frontend settings to use port 8001.

### Module not found
Make sure you're in the `farm_security_backend` directory when running.
