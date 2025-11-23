import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import {
  arbitrum,
  arbitrumSepolia,
  mainnet,
  sepolia,
} from 'wagmi/chains';

// Hyperliquid Testnet is an L1, but for the "Connect Wallet" part 
// we usually connect to Arbitrum (where USDC lives) or just use standard EVM chains 
// to sign the agent authorization.
// Hyperliquid Testnet Chain ID: 998 (Hyperliquid L1) - Not always standard in Wagmi.
// Usually we connect to Arbitrum Sepolia for Testnet USDC deposits.
// For the purpose of "Signing", any EVM chain works if we just use personal_sign.

export const config = getDefaultConfig({
  appName: 'Hyperliquid Trader Bot',
  projectId: 'YOUR_PROJECT_ID', // Get one from WalletConnect Cloud
  chains: [
    mainnet,
    arbitrum,
    arbitrumSepolia,
    sepolia,
  ],
  ssr: true,
});
