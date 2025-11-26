.PHONY: help install dev backend frontend test test-backend test-frontend clean

# Default target
help:
	@echo "Hyperliquid Trading Bot - Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make dev              Start both backend and frontend"
	@echo "  make backend          Start only backend (port 8000)"
	@echo "  make frontend         Start only frontend (port 3000)"
	@echo "  make install          Install all dependencies"
	@echo "  make test             Run all tests"
	@echo "  make test-backend     Run backend tests only"
	@echo "  make test-frontend    Run frontend tests only"
	@echo "  make clean            Clean build artifacts"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && python3 -m venv venv && venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo ""
	@echo "✅ All dependencies installed!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Configure backend/.env (copy from backend/.env.example)"
	@echo "  2. Run 'make dev' to start the application"

# Start both services in parallel
dev:
	@echo "� Stopping any existing services..."
	@-lsof -ti:8000 | xargs kill -9 > /dev/null 2>&1 || true
	@-lsof -ti:3000 | xargs kill -9 > /dev/null 2>&1 || true
	@echo "�🚀 Starting Hyperliquid Trading Bot..."
	@echo ""
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop both services"
	@echo ""
	@trap 'kill 0' SIGINT; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait

# Start backend only
backend:
	@echo "🔧 Starting backend on port 8000..."
	cd backend && venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend only
frontend:
	@echo "🎨 Starting frontend on port 3000..."
	cd frontend && npm run dev

# Run all tests
test:
	@echo "🧪 Running all tests..."
	@echo ""
	@echo "=== Backend Tests ==="
	cd backend && venv/bin/python -m pytest tests -v
	@echo ""
	@echo "=== Frontend Tests ==="
	cd frontend && npm test
	@echo ""
	@echo "✅ All tests completed!"

# Run backend tests only
test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && venv/bin/python -m pytest tests -v

# Run frontend tests only
test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf backend/*.db
	rm -rf frontend/.next
	rm -rf frontend/out
	rm -rf frontend/node_modules/.cache
	@echo "✅ Clean complete!"
