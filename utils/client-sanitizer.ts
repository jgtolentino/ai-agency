// SnowWhite Client Sanitizer - Hide Debug Info and Agent Internals
// Ensures clean client-facing deployment

interface SanitizationConfig {
  hideDebugInfo: boolean;
  sanitizeConsole: boolean;
  removeDevTools: boolean;
  anonymizeErrors: boolean;
}

class ClientSanitizer {
  private config: SanitizationConfig;
  private isProduction: boolean;

  constructor(config: Partial<SanitizationConfig> = {}) {
    this.config = {
      hideDebugInfo: true,
      sanitizeConsole: true,
      removeDevTools: true,
      anonymizeErrors: true,
      ...config
    };
    
    this.isProduction = process.env.NODE_ENV === 'production' || 
                       !window.location.hostname.includes('localhost');
    
    if (this.isProduction) {
      this.initializeSanitization();
    }
  }

  // Initialize all sanitization measures
  private initializeSanitization() {
    if (this.config.sanitizeConsole) {
      this.sanitizeConsole();
    }
    
    if (this.config.hideDebugInfo) {
      this.hideDebugElements();
    }
    
    if (this.config.removeDevTools) {
      this.disableDevTools();
    }
    
    if (this.config.anonymizeErrors) {
      this.setupErrorHandling();
    }
  }

  // Sanitize console output for client deployment
  private sanitizeConsole() {
    // Store original console methods
    const originalConsole = {
      debug: console.debug,
      info: console.info,
      warn: console.warn,
      error: console.error,
      log: console.log
    };

    // Override debug and info in production
    console.debug = () => {};
    console.info = () => {};
    
    // Filter sensitive information from warnings and errors
    console.warn = (...args: any[]) => {
      const filteredArgs = this.filterSensitiveInfo(args);
      originalConsole.warn(...filteredArgs);
    };
    
    console.error = (...args: any[]) => {
      const filteredArgs = this.filterSensitiveInfo(args);
      originalConsole.error(...filteredArgs);
    };
    
    console.log = (...args: any[]) => {
      // Only allow essential logs in production
      if (args.some(arg => 
        typeof arg === 'string' && 
        (arg.includes('error') || arg.includes('failed') || arg.includes('success'))
      )) {
        const filteredArgs = this.filterSensitiveInfo(args);
        originalConsole.log(...filteredArgs);
      }
    };
  }

  // Filter sensitive information from logs
  private filterSensitiveInfo(args: any[]): any[] {
    return args.map(arg => {
      if (typeof arg === 'string') {
        return arg
          .replace(/Platform/g, 'System')
          .replace(/Agent/g, 'Assistant')
          .replace(/Memory/g, 'Cache')
          .replace(/Orchestration/g, 'Automation')
          .replace(/\.ts|\.tsx/g, '')
          .replace(/localhost:\d+/g, 'application')
          .replace(/session-\w+/g, 'session-****')
          .replace(/key-\w+/g, 'key-****');
      }
      return arg;
    });
  }

  // Hide debug UI elements
  private hideDebugElements() {
    const debugSelectors = [
      '.debug-panel',
      '.dev-tools',
      '.agent-status',
      '.memory-viewer',
      '.system-info',
      '.performance-metrics',
      '[data-debug]',
      '[data-dev-only]',
      '.development-only'
    ];

    // Hide elements on DOM ready
    const hideElements = () => {
      debugSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
          (element as HTMLElement).style.display = 'none';
        });
      });
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', hideElements);
    } else {
      hideElements();
    }

    // Also hide dynamically added debug elements
    const observer = new MutationObserver(() => {
      hideElements();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  // Disable development tools and debugging
  private disableDevTools() {
    // Disable right-click context menu in production
    document.addEventListener('contextmenu', (e) => {
      if (this.isProduction) {
        e.preventDefault();
      }
    });

    // Disable F12 and other dev tool shortcuts
    document.addEventListener('keydown', (e) => {
      if (this.isProduction) {
        // F12
        if (e.key === 'F12') {
          e.preventDefault();
        }
        
        // Ctrl+Shift+I (DevTools)
        if (e.ctrlKey && e.shiftKey && e.key === 'I') {
          e.preventDefault();
        }
        
        // Ctrl+Shift+C (Inspect)
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
          e.preventDefault();
        }
        
        // Ctrl+U (View Source)
        if (e.ctrlKey && e.key === 'u') {
          e.preventDefault();
        }
      }
    });

    // Detect DevTools and show warning
    let devtools = { open: false };
    const threshold = 160;

    setInterval(() => {
      if (window.outerHeight - window.innerHeight > threshold || 
          window.outerWidth - window.innerWidth > threshold) {
        if (!devtools.open) {
          devtools.open = true;
          console.warn('⚠️ This application is optimized for production use.');
        }
      } else {
        devtools.open = false;
      }
    }, 500);
  }

  // Setup client-safe error handling
  private setupErrorHandling() {
    // Global error handler
    window.addEventListener('error', (event) => {
      // Prevent detailed error information from being exposed
      event.preventDefault();
      
      // Log sanitized error for monitoring
      this.logSanitizedError('Runtime Error', {
        message: 'An error occurred while processing your request',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      });
    });

    // Promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      event.preventDefault();
      
      this.logSanitizedError('Promise Rejection', {
        message: 'A request could not be completed',
        timestamp: new Date().toISOString()
      });
    });
  }

  // Log sanitized errors for client monitoring
  private logSanitizedError(type: string, details: any) {
    // Only log essential information for client support
    const sanitizedError = {
      type,
      message: details.message,
      timestamp: details.timestamp,
      session: 'client-session',
      version: '1.0.0'
    };

    // Send to client-safe logging endpoint (if available)
    if (typeof fetch !== 'undefined') {
      fetch('/api/client-errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitizedError)
      }).catch(() => {
        // Silent fail for error reporting
      });
    }
  }

  // Clean component props for client display
  static sanitizeProps(props: Record<string, any>): Record<string, any> {
    const sanitized = { ...props };
    
    // Remove internal debugging props
    delete sanitized.debugMode;
    delete sanitized.devTools;
    delete sanitized.agentId;
    delete sanitized.sessionId;
    delete sanitized.memoryKey;
    delete sanitized.internalState;
    
    // Sanitize string values
    Object.keys(sanitized).forEach(key => {
      if (typeof sanitized[key] === 'string') {
        sanitized[key] = sanitized[key]
          .replace(/Platform/g, 'System')
          .replace(/Agent/g, 'Assistant')
          .replace(/Memory/g, 'Cache');
      }
    });
    
    return sanitized;
  }

  // Clean data for client export
  static sanitizeExportData(data: any): any {
    if (Array.isArray(data)) {
      return data.map(item => this.sanitizeExportData(item));
    }
    
    if (typeof data === 'object' && data !== null) {
      const sanitized: any = {};
      
      Object.keys(data).forEach(key => {
        // Skip internal fields
        if (key.startsWith('_') || 
            key.includes('debug') || 
            key.includes('internal') ||
            key.includes('agent') ||
            key.includes('memory')) {
          return;
        }
        
        sanitized[key] = this.sanitizeExportData(data[key]);
      });
      
      return sanitized;
    }
    
    return data;
  }

  // Initialize sanitization for client deployment
  static initializeClientMode() {
    // Only run in production or client environments
    if (process.env.NODE_ENV === 'production' || 
        window.location.hostname !== 'localhost') {
      new ClientSanitizer();
      
      // Add client theme
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/styles/client-theme.css';
      document.head.appendChild(link);
      
      // Set client title
      document.title = 'Retail Intelligence Dashboard';
      
      // Update meta tags
      const metaDescription = document.querySelector('meta[name="description"]');
      if (metaDescription) {
        metaDescription.setAttribute('content', 'Advanced retail analytics and insights platform');
      }
    }
  }
}

// Auto-initialize in client mode
if (typeof window !== 'undefined') {
  ClientSanitizer.initializeClientMode();
}

export { ClientSanitizer };
export default ClientSanitizer;