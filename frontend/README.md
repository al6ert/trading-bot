# Hyperliquid Trading Bot - Frontend

Next.js dashboard for monitoring and controlling the trading bot.

## Features

- 🎨 **Modern UI**: Built with Next.js 16, React 19, and DaisyUI
- 💼 **Wallet Integration**: RainbowKit + Wagmi for Web3 wallet connection
- 📊 **TradingView Charts**: Real-time price charts with trade markers
- 📈 **Portfolio Tracking**: Live portfolio updates with crypto/stable allocation
- 🎯 **Dual Bag System**: Separate tracking for trading and HODL strategies
- 🔄 **Real-time Updates**: Auto-refreshing data from backend API
- 🧪 **Dummy Mode**: Test the interface without connecting a wallet

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **UI**: React 19, DaisyUI, Tailwind CSS 4
- **Charts**: Lightweight Charts (TradingView)
- **Web3**: RainbowKit, Wagmi, Viem
- **Testing**: Jest, React Testing Library

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables (Optional)

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

```bash
npm test              # Run all tests
npm test -- --watch   # Watch mode
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm test` | Run Jest tests |

## Usage

### Landing Page
- **Connect Wallet**: Use RainbowKit to connect your Web3 wallet
- **Dummy Mode**: Click "Enter with Dummy Wallet" to test without a wallet

### Dashboard
- **Portfolio Progress Bar**: Total equity with crypto/stable allocation
- **Short-Term Bag**: Active trading strategies and 24h PnL
- **Long-Term Bag**: HODL positions and total yield
- **TradingView Chart**: BTC/USDT with multiple timeframes
- **Log Panel**: Real-time bot activity

## License

Private Project
