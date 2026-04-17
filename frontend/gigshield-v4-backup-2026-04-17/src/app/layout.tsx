import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { PageTransition } from "@/components/PageTransition";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "TriggerPe — When it triggers, you get paid.",
  description: "Zero-touch parametric income insurance for delivery heroes in India. When it triggers, you get paid.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased selection:bg-blue-500/30`}>
        {/* Glowing Background Blobs */}
        <div className="fixed top-[-100px] right-[-100px] w-[600px] h-[600px] rounded-full bg-[#7c3aed] opacity-20 blur-[100px] pointer-events-none z-[-1]" />
        <div className="fixed bottom-[-100px] left-[-100px] w-[500px] h-[500px] rounded-full bg-[#3b82f6] opacity-15 blur-[100px] pointer-events-none z-[-1]" />

        <PageTransition />
        <Navigation />
        <main className="relative z-10 w-full">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
