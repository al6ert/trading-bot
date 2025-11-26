# Hyperliquid Trading Bot - Backend

FastAPI-based trading bot for automated trading on Hyperliquid DEX.

## Features

- 🔐 **Risk Management**: RiskManager validates signals and calculates position sizes
- 📊 **Order Execution**: OrderExecutor handles trade execution with Hyperliquid SDK
- 🎯 **Strategy System**: Modular strategy architecture for different trading approaches
- 📈 **Market Data**: Real-time and historical candle data via Hyperliquid API
- 💾 **Database**: SQLAlchemy ORM for trade and portfolio tracking

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (can be upgraded to PostgreSQL)
- **Exchange SDK**: hyperliquid-python-sdk
- **Testing**: pytest
- **Environment**: Python 3.10+

## Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file:
```env
HYPERLIQUID_ENV=TESTNET  # or MAINNET
PRIVATE_KEY=your_private_key_here
SYMBOL=ETH
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Initialize Database
```bash
python create_tables.py
```

### 5. Run the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or using the venv directly:
```bash
venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

Run all unit tests:
```bash
venv/bin/python -m pytest tests
```

Run with coverage:
```bash
venv/bin/python -m pytest tests --cov=app
```

### Test Coverage

- **RiskManager**: Signal validation, position sizing (bull/bear modes)
- **OrderExecutor**: Account state fetching, order execution
- Total: 10 unit tests

## API Endpoints

### Health Check
- `GET /` - Check if the server is running

### Bot Control
- `POST /start` - Start the trading bot
- `POST /stop` - Stop the trading bot
- `GET /status` - Get bot status

### Portfolio (API v2)
- `GET /api/v2/portfolio/summary` - Portfolio summary
- `GET /api/v2/portfolio/bags` - Trading and HODL bag details

### Market Data
- `GET /api/v2/market/candles?timeframe=1h` - Get OHLCV candles
- `GET /api/v2/market/trades` - Get recent trades

## Project Structure

```
backend/
├── app/
│   ├── api/            # API routes
│   ├── core/           # Core bot logic
│   ├── domain/         # Business logic (risk, execution, strategies)
│   ├── infrastructure/ # External integrations (database, Hyperliquid)
│   └── main.py         # FastAPI application
├── tests/              # Unit tests
├── venv/               # Virtual environment
├── .env                # Environment variables (not committed)
├── requirements.txt    # Python dependencies
└── create_tables.py    # Database initialization
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HYPERLIQUID_ENV` | Trading environment | `TESTNET` |
| `PRIVATE_KEY` | Wallet private key | - |
| `SYMBOL` | Trading symbol | `ETH` |
| `API_HOST` | Server host | `0.0.0.0` |
| `API_PORT` | Server port | `8000` |

## Development

### Adding New Strategies
1. Create a new file in `app/domain/strategies/`
2. Inherit from base strategy class
3. Implement required methods
4. Register in strategy manager

### Running Tests
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_risk_manager.py

# With verbose output
pytest tests/ -v
```

## Safety Features

- **1x Leverage Only**: Never uses borrowed funds
- **Liquidity Reserve**: Maintains 20% cash reserve
- **Signal Validation**: All signals pass through RiskManager
- **Regime-Based Allocation**: Bull (80% crypto) / Bear (20% crypto)

## License

Private Project
