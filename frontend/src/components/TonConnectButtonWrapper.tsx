'use client';

import { TonConnectButton, useTonConnectUI, useTonAddress } from "@tonconnect/ui-react";
import { Suspense, useEffect } from "react";

export default function TonConnectButtonWrapper() {
  const [tonConnectUI] = useTonConnectUI();
  const address = useTonAddress();

  useEffect(() => {
    if (address) {
      console.log('✅ Wallet connected:', address);
    }
  }, [address]);

  useEffect(() => {
    const handleStatusChange = () => {
      console.log('🔄 Wallet status changed');
    };

    tonConnectUI?.onStatusChange(handleStatusChange);

    return () => {
      // Clean up the listener
    };
  }, [tonConnectUI]);

  return (
    <Suspense fallback={<div className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">Завантаження гаманця...</div>}>
      <TonConnectButton />
    </Suspense>
  );
}
