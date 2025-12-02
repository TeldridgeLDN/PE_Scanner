import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import ScrollTracker from "@/components/ScrollTracker";
import Navigation from "@/components/Navigation";
import { generateLandingMetadata } from "@/lib/metadata";

// Use comprehensive metadata with full OG and Twitter Card tags
export const metadata: Metadata = generateLandingMetadata();

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en-GB">
      <head>
        {/* Plausible Analytics - Privacy-friendly, no cookies */}
        {process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN && (
          <Script
            defer
            data-domain={process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN}
            src="https://plausible.io/js/script.js"
          />
        )}
      </head>
      <body className="antialiased">
        {/* Global Navigation */}
        <Navigation />
        
        {/* Main Content */}
        <main id="main-content">
          {children}
        </main>
        
        {/* Scroll depth tracking */}
        <ScrollTracker />
      </body>
    </html>
  );
}
