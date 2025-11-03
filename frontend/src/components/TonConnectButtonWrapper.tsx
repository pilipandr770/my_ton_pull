'use client';

import { TonConnectButton, useTonConnectUI, useTonAddress, useTonConnectModal } from "@tonconnect/ui-react";
import { Suspense, useEffect } from "react";

export default function TonConnectButtonWrapper() {
  const [tonConnectUI] = useTonConnectUI();
  const address = useTonAddress();
  const { state } = useTonConnectModal();

  useEffect(() => {
    console.log('🔗 TonConnectButtonWrapper mounted');
    
    if (!tonConnectUI) {
      console.log('⚠️ tonConnectUI is not initialized');
      return;
    }

    // Log current state
    console.log('📊 Current state:', {
      address,
      modalState: state,
    });

    // Subscribe to status changes
    const unsubscribeStatus = tonConnectUI.onStatusChange((wallet) => {
      if (wallet) {
        console.log('✅ Wallet connected:', {
          name: wallet.name,
          address: wallet.account?.address,
        });
        window.dispatchEvent(new CustomEvent('tonconnect:connected', { detail: wallet }));
      } else {
        console.log('❌ Wallet disconnected');
      }
    });

    return () => {
      unsubscribeStatus?.();
    };
  }, [tonConnectUI, state, address]);

  useEffect(() => {
    if (address) {
      console.log('✨ Address available:', address);
    }
  }, [address]);

  return (
    <>
      <Suspense fallback={<div className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">Завантаження гаманця...</div>}>
        <TonConnectButton />
      </Suspense>
      {address && (
        <div className="ml-2 text-sm text-green-600 font-medium">
          ✅ Підключено: {address.slice(0, 6)}...{address.slice(-4)}
        </div>
      )}
    </>
  );
}
