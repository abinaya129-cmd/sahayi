# SAHAYI — VS Code + GitHub Guide

## 1. Open in VS Code

1. **Open VS Code** → `File > Open Folder...`
2. Select: `E:\abi\all iteams\PERSONAL\college sri ram\hackathon\mgr`
3. Install the **Python extension** (Microsoft, `ms-python.python`) — VS Code will suggest it.
4. Press `Ctrl+Shift+P` → type **"Python: Select Interpreter"** → pick your installed Python 3.12.
5. Open the terminal inside VS Code: ``Ctrl+` `` (backtick key, left of 1).
6. Install + run:

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

7. Open **http://localhost:8001** in the browser (Ctrl+Click the link VS Code prints).
8. Optional — one-click debug: create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "SAHAYI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--host", "0.0.0.0", "--port", "8001"],
      "justMyCode": false
    }
  ]
}
```

Then press **F5** to run with breakpoints.

## 2. Push to GitHub (first time)

```bash
# 1. Initialise git in the project folder
git init

# 2. Stage everything (.gitignore already excludes *.db, logs, .freebuff)
git add .

# 3. First commit
git commit -m "SAHAYI: voice-first govtech assistant - 13 languages, 7 schemes, ask-anything KB"

# 4. Create the repo on github.com (New repository, NO README/gitignore),
#    then connect and push:
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/sahayi.git
git push -u origin main
```

If GitHub asks for a password: it wants a **Personal Access Token**, not your login
(GitHub → Settings → Developer settings → Personal access tokens → Generate, tick `repo`).
Or press "Sign in with browser" if Git offers it.

## 3. Every later change

```bash
git add .
git commit -m "describe what you changed"
git push
```

## 4. Handy extras

- **See what changed before committing:** `git status` and `git diff`
- **Never commit:** `*.db`, `uvicorn.log`, `.env` (already in .gitignore)
- **Clone on another machine:** `git clone https://github.com/<YOU>/sahayi.git`
- **Free hosting:** the repo includes a Dockerfile — Cloud Run deploy is in README.md
