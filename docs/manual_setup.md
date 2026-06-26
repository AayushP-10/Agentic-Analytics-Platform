# Manual Setup

Complete these steps before running the project locally.

## 1. Clone the Repository

```bash
git clone <repository-url>
cd agentic-analytics-platform
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```bash
python -m pip install --upgrade pip
make install
```

## 4. Create a Local Environment File

```bash
cp .env.example .env
```

Do not commit `.env` or any real secrets.

## 5. Generate Sample Data

```bash
make sample-data
```

This creates deterministic demo files under `data/sample/` and `data/sqlite/`.

## 6. Run Tests

```bash
make test
```

## 7. Run Linting

```bash
make lint
```

## 8. Start the Backend

```bash
make backend
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

## 9. Start the Frontend

```bash
make frontend
```

Streamlit will print a local URL in the terminal.
