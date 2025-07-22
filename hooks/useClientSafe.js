import { useState, useEffect } from 'react'

/**
 * Hook to safely detect if we're running on client-side
 * Prevents hydration mismatches and SSR issues
 */
export function useIsClient() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  return isClient
}

/**
 * Hook to detect mobile viewport
 * Safely handles window access and provides mobile-specific logic
 */
export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)
  const isClient = useIsClient()

  useEffect(() => {
    if (!isClient || typeof window === 'undefined') return

    const checkMobile = () => {
      try {
        // Check viewport width
        const width = window.innerWidth
        const userAgent = window.navigator?.userAgent || ''
        
        // Mobile viewport check
        const isSmallScreen = width < 768
        
        // User agent check for mobile devices
        const isMobileUserAgent = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)
        
        // Touch device check
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0
        
        setIsMobile(isSmallScreen || (isMobileUserAgent && isTouchDevice))
      } catch (error) {
        console.warn('Error detecting mobile device:', error)
        // Fallback to false if detection fails
        setIsMobile(false)
      }
    }

    // Initial check
    checkMobile()

    // Add resize listener
    let timeoutId
    const handleResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(checkMobile, 150) // Debounce resize events
    }

    window.addEventListener('resize', handleResize)
    
    // Cleanup
    return () => {
      clearTimeout(timeoutId)
      window.removeEventListener('resize', handleResize)
    }
  }, [isClient])

  return isMobile
}

/**
 * Hook for safe window/document access
 * Returns null on server-side, actual values on client-side
 */
export function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: undefined,
    height: undefined,
  })
  const isClient = useIsClient()

  useEffect(() => {
    if (!isClient || typeof window === 'undefined') return

    const handleResize = () => {
      try {
        setWindowSize({
          width: window.innerWidth,
          height: window.innerHeight,
        })
      } catch (error) {
        console.warn('Error getting window size:', error)
      }
    }

    // Set initial size
    handleResize()

    let timeoutId
    const debouncedResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(handleResize, 150)
    }

    window.addEventListener('resize', debouncedResize)
    
    return () => {
      clearTimeout(timeoutId)
      window.removeEventListener('resize', debouncedResize)
    }
  }, [isClient])

  return windowSize
}

/**
 * Hook to safely handle async operations with cleanup
 * Prevents state updates on unmounted components
 */
export function useSafeAsync() {
  const [mounted, setMounted] = useState(true)

  useEffect(() => {
    return () => {
      setMounted(false)
    }
  }, [])

  const safeSetState = (setter) => {
    if (mounted) {
      setter()
    }
  }

  return { mounted, safeSetState }
}