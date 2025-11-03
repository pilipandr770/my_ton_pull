"use client";

import { Inter } from "next/font/google";
import "./globals.css";
import { TonConnectUIProvider } from "@tonconnect/ui-react";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="uk">
      <head>
        <title>TON Staking Pool - Децентралізований пул</title>
        <meta name="description" content="Стейкайте TON та отримуйте винагороди" />
      </head>
      <body className={inter.className}>
        <AuthProvider>
          <TonConnectUIProvider 
            manifestUrl="/tonconnect-manifest.json"
          >
            {children}
          </TonConnectUIProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
