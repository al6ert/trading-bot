// Suppress wallet extension errors that don't affect functionality
// This handles conflicts between Next.js and browser wallet extensions

if (typeof window !== 'undefined') {
  // Store original console.error
  const originalError = console.error;

  // Override console.error to filter out known extension conflicts
  console.error = (...args: any[]) => {
    // Filter out wallet extension property assignment errors
    if (
      args[0]?.toString().includes('opnet') ||
      args[0]?.toString().includes('pageProvider.js') ||
      args[0]?.toString().includes('chrome-extension')
    ) {
      // Silently ignore these - they don't affect functionality
      return;
    }
    
    // Pass through all other errors
    originalError.apply(console, args);
  };

  // Prevent wallet extensions from causing hydration errors
  Object.defineProperty(window, 'opnet', {
    configurable: true,
    writable: true,
    value: undefined
  });
}

export {};
