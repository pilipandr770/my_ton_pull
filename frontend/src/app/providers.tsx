'use client';

import { TonConnectUIProvider } from "@tonconnect/ui-react";
import { AuthProvider } from "@/contexts/AuthContext";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <TonConnectUIProvider 
        manifestUrl="/tonconnect-manifest.json"
      >
        {children}
      </TonConnectUIProvider>
    </AuthProvider>
  );
}
