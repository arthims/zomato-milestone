import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zomato AI — Restaurant Recommendations",
  description: "Find your next meal, powered by AI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg">
        <header className="border-b border-gray-100 bg-white">
          <div className="mx-auto max-w-content px-4 py-4 flex items-center gap-3">
            <span className="text-2xl font-bold text-accent">Zomato AI</span>
            <span className="text-sm text-gray-400 hidden sm:block">
              Find your next meal, powered by AI
            </span>
          </div>
        </header>
        <main className="mx-auto max-w-content px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
