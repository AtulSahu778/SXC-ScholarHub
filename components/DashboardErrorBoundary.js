import { Component } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { RefreshCw, AlertTriangle } from 'lucide-react'

/**
 * Error boundary component to catch client-side exceptions
 * Especially important for mobile devices where errors can be more frequent
 */
export class DashboardErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    // Log error for debugging
    console.error('Dashboard Error Boundary caught an error:', error, errorInfo)
    
    // You can also log the error to an error reporting service here
    // e.g., Sentry, LogRocket, etc.
  }

  handleRetry = () => {
    // Reset error boundary state
    this.setState({ hasError: false, error: null })
    
    // Optionally reload the page on mobile devices where memory might be limited
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      window.location.reload()
    }
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI for mobile-friendly error display
      return (
        <div className="w-full p-4 sm:p-6">
          <Alert className="bg-red-50/80 dark:bg-red-950/20 border-red-200 dark:border-red-800 backdrop-blur-sm">
            <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400" />
            <AlertDescription className="text-sm text-red-800 dark:text-red-400">
              <div className="flex flex-col space-y-3">
                <div>
                  <h4 className="font-medium mb-1">Dashboard temporarily unavailable</h4>
                  <p className="text-xs">
                    Something went wrong while loading the dashboard. This often happens on mobile devices with limited memory.
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Button 
                    onClick={this.handleRetry}
                    size="sm" 
                    variant="outline"
                    className="w-full sm:w-auto text-xs border-red-300 hover:bg-red-50 dark:hover:bg-red-950/10"
                  >
                    <RefreshCw className="h-3 w-3 mr-2" />
                    Try Again
                  </Button>
                  <Button
                    onClick={() => window.location.reload()}
                    size="sm"
                    className="w-full sm:w-auto text-xs bg-red-600 hover:bg-red-700 text-white"
                  >
                    Reload Page
                  </Button>
                </div>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Hook-based error boundary wrapper for functional components
 */
export function withErrorBoundary(Component, fallback) {
  return function WrappedComponent(props) {
    return (
      <DashboardErrorBoundary>
        <Component {...props} />
      </DashboardErrorBoundary>
    )
  }
}