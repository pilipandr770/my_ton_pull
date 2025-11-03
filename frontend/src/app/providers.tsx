'use client';

import React, { useMemo } from 'react';
import { TonConnectUIProvider } from "@tonconnect/ui-react";
import { AuthProvider } from "@/contexts/AuthContext";

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    console.error('getDerivedStateFromError:', error);
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught error:', error);
    console.error('Error info:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{padding: '20px', backgroundColor: '#fee', color: '#c00', fontFamily: 'sans-serif', minHeight: '100vh'}}>
          <h1>Помилка застосунку</h1>
          <details style={{whiteSpace: 'pre-wrap', marginTop: '10px', padding: '10px', backgroundColor: '#fdd', borderRadius: '4px'}}>
            <summary style={{cursor: 'pointer', fontWeight: 'bold'}}>Деталі помилки</summary>
            {this.state.error?.toString()}
          </details>
          <button 
            onClick={() => window.location.reload()}
            style={{marginTop: '10px', padding: '8px 16px', cursor: 'pointer', backgroundColor: '#00c', color: '#fff', border: 'none', borderRadius: '4px'}}
          >
            Перезавантажити
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default function Providers({ children }: { children: React.ReactNode }) {
  // Compute manifest URL on client side using useMemo
  const manifestUrl = useMemo(() => {
    if (typeof window !== 'undefined') {
      return `${window.location.origin}/tonconnect-manifest.json`;
    }
    // Fallback for SSR (should not be used since this is 'use client')
    return 'https://my-ton-pull.onrender.com/tonconnect-manifest.json';
  }, []);

  return (
    <ErrorBoundary>
      <AuthProvider>
        <TonConnectUIProvider 
          manifestUrl={manifestUrl}
        >
          {children}
        </TonConnectUIProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
