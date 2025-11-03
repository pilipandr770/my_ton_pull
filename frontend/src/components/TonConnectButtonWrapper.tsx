'use client';

import { TonConnectButton } from "@tonconnect/ui-react";
import { Suspense } from "react";

export default function TonConnectButtonWrapper() {
  return (
    <Suspense fallback={<div className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium">Завантаження гаманця...</div>}>
      <TonConnectButton />
    </Suspense>
  );
}
