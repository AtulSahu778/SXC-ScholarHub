import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import ChatBot from '@/components/ChatBot'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ScholarHub - Academic Knowledge Hub',
  description: 'Your intelligent academic companion powered by AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <ChatBot />
      </body>
    </html>
  )
}