import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Header } from "@/components/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Hyperliquid Trading Bot",
  description: "Professional Trading Suite",
};

import { AuthGuard } from "@/components/AuthGuard";
import { ConditionalHeader } from "@/components/ConditionalHeader";
import "./wallet-extension-fix";


// ... imports

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-theme="lofi">
      {/* suppressHydrationWarning is required because the agent/browser environment injects 
          'antigravity-scroll-lock' class to the body, causing a mismatch with server HTML. 
          This is a known issue with the preview environment, not the code. */}
      <body className={inter.className} suppressHydrationWarning>
        <Providers>
          <AuthGuard>
            <div className="min-h-screen bg-base-100 text-base-content font-sans">
              {/* Header is handled inside AuthGuard or we check path here? 
                  AuthGuard wraps everything. Let's make Header conditional on path or auth. 
                  Actually, the user said "Home should have ONLY the button". 
                  So header should be hidden on /.
              */}
              <ConditionalHeader />
              <main className="p-6 max-w-[1600px] mx-auto">
                {children}
              </main>
            </div>
          </AuthGuard>
        </Providers>
      </body>
    </html>
  );
}
