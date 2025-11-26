import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import LandingPage from '../app/page'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}))

// Mock wagmi
jest.mock('wagmi', () => ({
  useAccount: () => ({
    isConnected: false,
  }),
}))

// Mock RainbowKit
jest.mock('@rainbow-me/rainbowkit', () => ({
  ConnectButton: ({ label }: { label: string }) => <button>{label}</button>,
}))

describe('LandingPage - Dummy Wallet Flow', () => {
  const mockPush = jest.fn()
  const mockLocalStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    })
  })

  it('renders the dummy wallet button', () => {
    render(<LandingPage />)
    
    const dummyButton = screen.getByText(/Enter with Dummy Wallet/i)
    expect(dummyButton).toBeInTheDocument()
  })

  it('sets dummy_mode in localStorage and navigates to dashboard when dummy wallet is clicked', async () => {
    render(<LandingPage />)
    
    const dummyButton = screen.getByText(/Enter with Dummy Wallet/i)
    fireEvent.click(dummyButton)

    // Verify localStorage was set
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('dummy_mode', 'true')
    
    // Verify navigation occurred
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })
  })

  it('has correct styling for dummy wallet button', () => {
    render(<LandingPage />)
    
    const dummyButton = screen.getByText(/Enter with Dummy Wallet/i)
    expect(dummyButton).toHaveClass('btn', 'btn-outline', 'btn-sm')
  })
})
