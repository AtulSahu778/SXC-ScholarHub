import { useState, useEffect } from 'react'

/**
 * Safe localStorage hook that handles SSR and mobile device issues
 * Provides fallback for when localStorage is not available
 */
export function useSafeLocalStorage(key, initialValue) {
  // State to store our value
  const [storedValue, setStoredValue] = useState(initialValue)
  const [isClient, setIsClient] = useState(false)

  // Initialize on client mount
  useEffect(() => {
    setIsClient(true)
    
    try {
      // Check if localStorage is available
      if (typeof window !== 'undefined' && window.localStorage) {
        const item = window.localStorage.getItem(key)
        if (item) {
          const parsedItem = JSON.parse(item)
          setStoredValue(parsedItem)
        }
      }
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error)
      setStoredValue(initialValue)
    }
  }, [key, initialValue])

  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = (value) => {
    try {
      // Allow value to be a function so we have same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      
      // Save to localStorage only on client side
      if (isClient && typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, JSON.stringify(valueToStore))
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error)
    }
  }

  const removeValue = () => {
    try {
      setStoredValue(initialValue)
      if (isClient && typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.removeItem(key)
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue, removeValue, isClient]
}