# VBoarder Development Scripts

.PHONY: help dev test lint format clean install start backend frontend devdash smoke-test validate repair

help:
	@echo "VBoarder - Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make start      - Start full stack (backend + devdash)"
	@echo "  make dev        - Start backend with hot reload"
	@echo "  make backend    - Start backend server"
	@echo "  make frontend   - Start frontend (Next.js)"
	@echo "  make devdash    - Start developer dashboard"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test       - Run all tests (quiet mode)"
	@echo "  make test-v     - Run tests with verbose output"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make smoke-test - Run smoke tests (beta validation)"
	@echo "  make validate   - Run all system validations"
	@echo ""
	@echo "🔧 Code Quality:"
	@echo "  make lint       - Run linter (ruff)"
	@echo "  make lint-fix   - Run linter with auto-fix"
	@echo "  make format     - Format code (black + ruff)"
	@echo "  make pre-commit - Run pre-commit hooks"
	@echo ""
	@echo "🔧 Agent Tools:"
	@echo "  make repair     - Run agent repair (dry-run)"
	@echo "  make repair-fix - Execute agent repair"
	@echo "  make test-agents - Test all 9 agents"
	@echo ""
	@echo "📦 Dependencies:"
	@echo "  make install    - Install dependencies"
	@echo "  make freeze     - Create requirements.lock"
	@echo "  make setup-hooks - Install pre-commit hooks"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean      - Remove cache files and artifacts"
	@echo "  make clean-all  - Deep clean (including logs, data)"

# ===========================================
# Quick Start
# ===========================================

start: backend devdash

backend:
	@echo "🚀 Starting Backend API on port 3738..."
	uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload

frontend:
	@echo "🎨 Starting Frontend on port 3000..."
	cd vboarder_frontend/nextjs_space && npm run dev

devdash:
	@echo "📊 Starting DevDash on port 4545..."
	python tools/dev/devdash.py

# ===========================================
# Development server (alias for backend)
# ===========================================

dev: backend

# ===========================================
# Testing
# ===========================================

test:
	@echo "🧪 Running tests..."
	pytest -q

test-v:
	@echo "🧪 Running tests (verbose)..."
	pytest -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=api --cov-report=html --cov-report=term

smoke-test:
	@echo "🧪 Running smoke tests..."
	bash tools/tests/run_smoke_beta.sh

validate:
	@echo "🔍 Running system validations..."
	bash tools/ops/validate-all.sh

test-agents:
	@echo "🧪 Testing all agents..."
	bash tools/ops/test-all-agents.sh

# ===========================================
# Code quality
# ===========================================

lint:
	@echo "🔍 Running linter..."
	ruff check api tests_flat

lint-fix:
	@echo "🔧 Running linter with auto-fix..."
	ruff check api tests_flat --fix

format:
	@echo "🎨 Formatting code..."
	black api tests_flat agents
	ruff check api tests_flat --fix

pre-commit:
	@echo "🔍 Running pre-commit hooks..."
	pre-commit run --all-files

# ===========================================
# Agent Tools
# ===========================================

repair:
	@echo "🔧 Running agent repair (dry-run)..."
	DRY_RUN=true bash tools/ops/repair-agents.sh

repair-fix:
	@echo "🔧 Executing agent repair..."
	bash tools/ops/repair-agents.sh

repair-validate:
	@echo "✅ Validating hardening improvements..."
	bash tools/tests/validate_hardening.sh

# ===========================================
# Dependency management
# ===========================================

install:
	@echo "📦 Installing dependencies..."
	pip install -U pip wheel
	pip install -r requirements.txt

install-dev:
	@echo "📦 Installing dev dependencies..."
	pip install -U pip wheel
	pip install -r requirements.txt
	pip install pre-commit pytest-cov black ruff

freeze:
	@echo "📦 Freezing dependencies..."
	pip list --format=freeze > requirements.lock

setup-hooks:
	@echo "🔧 Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"

# ===========================================
# Cleanup
# ===========================================

clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	@echo "✅ Cleanup complete!"

clean-all: clean
	@echo "🧹 Deep cleaning (logs, data, uploads)..."
	rm -rf logs/*.log 2>/dev/null || true
	rm -rf test_data/ test_logs/ test_uploads/ 2>/dev/null || true
	@echo "✅ Deep cleanup complete!"

# ===========================================
# Environment Setup
# ===========================================

setup-dev:
	@echo "🔧 Setting up development environment..."
	cp .env.example .env.development || true
	@echo "✅ .env.development created (customize as needed)"

setup-test:
	@echo "🔧 Setting up test environment..."
	cp .env.example .env.testing || true
	@echo "✅ .env.testing created (customize as needed)"

# ===========================================
# Documentation
# ===========================================

docs:
	@echo "📚 Opening documentation..."
	@echo "Quick Reference: .vscode/QUICK_REFERENCE.md"
	@echo "Setup Guide: docs/VSCODE_SETUP_GUIDE.md"
	@echo "Agent Repair: docs/AGENT_REPAIR_HARDENING.md"

# ===========================================
# Git & Versioning
# ===========================================

tag-beta:
	@echo "🏷️  Tagging v0.9.0-beta.1..."
	git tag -a v0.9.0-beta.1 -m "Stable build with VS Code hardening"
	git push origin v0.9.0-beta.1 --tags
	@echo "✅ Beta tagged and pushed!"

# ===========================================
# CI/CD Helpers
# ===========================================

ci-test:
	@echo "🚀 Running CI tests..."
	pytest -v --cov=api --cov-report=xml --cov-report=term

ci-lint:
	@echo "🔍 Running CI linter..."
	ruff check api tests_flat --output-format=github

ci-validate:
	@echo "🔍 Running CI validation..."
	bash tools/ops/validate-all.sh
	bash tools/tests/run_smoke_beta.sh
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/

# Health checks
health:
	@curl -s http://127.0.0.1:3738/health | python -m json.tool

ready:
	@curl -s http://127.0.0.1:3738/ready | python -m json.tool

agents:
	@curl -s http://127.0.0.1:3738/agents | python -m json.tool

# Quick chat test
chat-test:
	@curl -s -X POST http://127.0.0.1:3738/chat/CEO \
		-H 'Content-Type: application/json' \
		-d '{"message":"Quick health check","session_id":"test","concise":true}' \
		| python -m json.tool | head -n 20

# Development dashboard
dashboard:
	@echo "Starting Dev Dashboard..."
	@echo "Open http://127.0.0.1:4545 in your browser"
	python tools/dev/devdash.py

# Repository inventory
inventory:
	@echo "Generating repository inventory..."
	python tools/inventory/inventory.py

# Update doc links after reorganization
update-docs:
	@echo "Updating documentation links..."
	python tools/ops/update-doc-links.py
