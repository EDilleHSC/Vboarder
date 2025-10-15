@echo off
setlocal ENABLEDELAYEDEXPANSION

REM 1) Paths
set ROOT=%cd%
echo Working in %ROOT%

REM 2) Ensure Python venv (optional)
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate

REM 3) Python deps
echo Installing Python requirements...
pip install --upgrade pip
pip install asyncpg qdrant-client aiohttp python-dotenv

REM 4) Create .env if missing
if not exist .env (
  echo Creating .env
  (
    echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vboarder
    echo QDRANT_URL=http://localhost:6333
    echo OLLAMA_URL=http://localhost:11434
    echo EMBEDDING_MODEL=nomic-embed-text
    echo RAG_TOP_K=5
  ) > .env
) else (
  echo .env already exists - skipping creation
)

REM 5) Start Docker services (Postgres + Qdrant)
echo Starting Docker containers...
docker ps >nul 2>&1
if errorlevel 1 (
  echo Docker is not running. Please start Docker Desktop and rerun this script.
  exit /b 1
)

REM Postgres
docker inspect vboarder-pg >nul 2>&1
if errorlevel 1 (
  docker run -d --name vboarder-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=vboarder -p 5432:5432 -v pg_data:/var/lib/postgresql/data postgres:16
) else (
  echo Postgres container exists - ensuring it is running...
  docker start vboarder-pg >nul
)

REM Qdrant
docker inspect vboarder-qdrant >nul 2>&1
if errorlevel 1 (
  docker run -d --name vboarder-qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
) else (
  echo Qdrant container exists - ensuring it is running...
  docker start vboarder-qdrant >nul
)

echo Waiting 8s for services to warm up...
timeout /t 8 >nul

REM 6) Bootstrap Qdrant collections for all agents
echo Bootstrapping Qdrant collections...
py scripts\bootstrap_qdrant.py
if errorlevel 1 (
  echo Failed to bootstrap Qdrant collections.
  exit /b 1
)

echo DONE. Local environment is ready.
echo Next: Use scripts\ingest_doc.py to add a document to an agent, then scripts\test_retrieval.py to verify.
endlocal