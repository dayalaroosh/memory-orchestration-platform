import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Memory Orchestration Platform',
  description: 'Advanced memory management and orchestration system',
  keywords: ['memory', 'orchestration', 'platform', 'management'],
  authors: [{ name: 'Memory Platform Team' }],
  openGraph: {
    title: 'Memory Orchestration Platform',
    description: 'Advanced memory management and orchestration system',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          {children}
        </div>
      </body>
    </html>
  )
}
