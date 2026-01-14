import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Auto Bidder AI",
  description: "AI-powered proposal automation agent",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
