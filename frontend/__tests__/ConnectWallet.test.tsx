import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { ConnectWallet } from '../components/ConnectWallet'

// Mock the ConnectButton from RainbowKit
// We need to mock ConnectButton.Custom which is a render prop pattern
jest.mock('@rainbow-me/rainbowkit', () => ({
  ConnectButton: {
    Custom: ({ children }: { children: (props: any) => JSX.Element }) => {
      // Simulate a disconnected state
      const mockProps = {
        account: null,
        chain: null,
        openAccountModal: jest.fn(),
        openChainModal: jest.fn(),
        openConnectModal: jest.fn(),
        authenticationStatus: 'unauthenticated',
        mounted: true,
      }
      return children(mockProps)
    },
  },
}))

describe('ConnectWallet', () => {
  it('renders the connect button when not connected', () => {
    render(<ConnectWallet />)
    
    // Check if the "Connect Wallet" button is rendered
    expect(screen.getByText('Connect Wallet')).toBeInTheDocument()
  })

  it('button has proper styling classes', () => {
    render(<ConnectWallet />)
    
    const button = screen.getByText('Connect Wallet')
    expect(button).toHaveClass('btn', 'btn-primary', 'btn-sm', 'font-bold')
  })
})

