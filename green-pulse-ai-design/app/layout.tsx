import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'

import { AppProviders } from '@/components/providers/app-providers'

import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'GreenPulse AI | Energy Intelligence Platform',
    template: '%s | GreenPulse AI',
  },
  description:
    'Monitor energy usage, detect anomalies and optimize sustainability across your manufacturing plants with GreenPulse AI.',
  applicationName: 'GreenPulse AI',
}

export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#F5F7FA' },
    { media: '(prefers-color-scheme: dark)', color: '#111A24' },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="font-sans antialiased">
        <AppProviders>{children}</AppProviders>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
