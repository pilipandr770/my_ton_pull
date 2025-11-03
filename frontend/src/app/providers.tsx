'use client';

import React from 'react';
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
    return { hasError: true, error };
  }

  componentDidCatch(error: Error) {
    console.error('ErrorBoundary caught:', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{padding: '20px', backgroundColor: '#fee', color: '#c00', fontFamily: 'sans-serif'}}>
          <h1>Помилка застосунку</h1>
          <p>{this.state.error?.message || 'Невідома помилка'}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{padding: '8px 16px', cursor: 'pointer'}}
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
  return (
    <ErrorBoundary>
      <AuthProvider>
        <TonConnectUIProvider 
          manifestUrl="/tonconnect-manifest.json"
        >
          {children}
        </TonConnectUIProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
