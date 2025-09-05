import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Instrument_Serif } from "next/font/google"
import "./globals.css"
import { cn } from "@/lib/utils"
import { V0Provider } from "@/lib/context"

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  subsets: ["latin"],
  weight: ["400"],
  style: ["normal", "italic"],
})

const isV0 = process.env["VERCEL_URL"]?.includes("vusercontent.net") ?? false

export const metadata: Metadata = {
  title: {
    template: "%s | ReefShield",
    default: "ReefShield",
  },
  description:
    "ReefShield is an AI-powered alert system that monitors coral reefs with live satellite data, predicting bleaching risks, oil spills, and other threats to protect marine life and coastal communities.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={cn(GeistSans.variable, GeistMono.variable, instrumentSerif.variable)}>
        <V0Provider isV0={isV0}>{children}</V0Provider>
      </body>
    </html>
  )
}
