# 🤖 Hyperliquid Trading Bot

Automated trading system for Hyperliquid DEX with a professional dashboard interface.

## Overview

This project consists of:
- **Backend** (FastAPI): Trading engine with risk management and order execution
- **Frontend** (Next.js): Real-time dashboard for monitoring and control
- **Dual Strategy System**: Short-term trading + long-term HODL

## Features

### Backend
- ✅ Risk management with position sizing
- ✅ Hyperliquid SDK integration
- ✅ Real-time market data ingestion
- ✅ Automated trade execution
- ✅ Regime-based allocation (Bull 80% / Bear 20%)
- ✅ Unit tested (pytest)

### Frontend
- ✅ TradingView-style charts
- ✅ RainbowKit wallet integration
- ✅ Real-time portfolio tracking
- ✅ Dummy mode for testing
- ✅ Unit tested (Jest + RTL)

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Using Makefile (Recommended)

```bash
# Start both backend and frontend
make dev

# Individual commands
make backend        # Start only backend
make frontend       # Start only frontend
make install        # Install all dependencies
make test           # Run all tests
make clean          # Clean build artifacts
```

### Manual Setup

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure your settings
python create_tables.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Backend `.env`
```env
HYPERLIQUID_ENV=TESTNET  # or MAINNET
PRIVATE_KEY=your_private_key_here
SYMBOL=ETH
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend `.env.local` (Optional)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
trader-bot/
├── backend/            # FastAPI trading engine
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Bot logic
│   │   ├── domain/    # Business logic
│   │   └── infrastructure/  # Database & Hyperliquid
│   ├── tests/         # Unit tests
│   └── requirements.txt
├── frontend/          # Next.js dashboard
│   ├── app/          # App router pages
│   ├── components/   # React components
│   ├── __tests__/    # Jest tests
│   └── package.json
├── planning/         # Architecture docs
├── Makefile         # Build automation
└── README.md        # This file
```

## Testing

### Backend Tests
```bash
cd backend
venv/bin/python -m pytest tests
```

**Coverage**: RiskManager, OrderExecutor (10 tests)

### Frontend Tests
```bash
cd frontend
npm test
```

**Coverage**: ConnectWallet, LandingPage (5 tests)

## API Endpoints

- `GET /` - Health check
- `POST /start` - Start bot
- `POST /stop` - Stop bot
- `GET /status` - Bot status
- `GET /api/v2/portfolio/summary` - Portfolio data
- `GET /api/v2/market/candles` - Chart data

## Development

### Running Tests
```bash
make test           # All tests
make test-backend   # Backend only
make test-frontend  # Frontend only
```

### Cleaning Build Artifacts
```bash
make clean
```

## Safety Features

- **1x Leverage Only**: Never uses borrowed funds
- **Liquidity Reserve**: Maintains 20% cash
- **Signal Validation**: All trades validated by RiskManager
- **Testnet First**: Test on Hyperliquid testnet before mainnet

## Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Architecture](planning/ARCHITECTURE.md)

## Troubleshooting

### Port Conflicts
If port 8000 or 3000 is in use:
```bash
# Find and kill process
lsof -ti:8000 | xargs kill
lsof -ti:3000 | xargs kill
```

### Backend Not Connecting
Ensure backend is running on port 8000 (not 8001/8002/8003):
```bash
curl http://localhost:8000/
```

### Frontend Shows No Data with Dummy Wallet
1. Check backend is running: `curl http://localhost:8000/`
2. Check browser console for API errors
3. Verify `dummy_mode` in localStorage is `"true"`

## License

Private Project

## Authors

Albert Perez
