# Quick Start Guide

## Automatic Start (Easiest)

```bash
cd /Users/markgentry/candidate-verification-app
./start-simple.sh
```

Then open: **http://localhost:8000**

---

## Manual Start

### Terminal 1 - Backend

```bash
cd /Users/markgentry/candidate-verification-app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Should see:** `Running on http://127.0.0.1:5001`

### Terminal 2 - Frontend

```bash
cd /Users/markgentry/candidate-verification-app/frontend
python3 -m http.server 8000
```

**Should see:** `Serving HTTP on 0.0.0.0 port 8000`

### Open Browser

Navigate to: **http://localhost:8000**

---

## Ports Used

- **Backend API:** http://localhost:5001
- **Frontend UI:** http://localhost:8000

---

## To Stop

Press **Ctrl+C** in each terminal window

Or if using start-simple.sh, just press **Ctrl+C** once

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Python Module Not Found
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Can't Activate Virtual Environment
Make sure you're using bash/zsh, not fish shell:
```bash
bash
source venv/bin/activate
```
