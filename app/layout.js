import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import Head from 'next/head'

export const metadata = {
  title: 'SXC ScholarHub',
  description: 'St. Xavier\'s College Academic Resources Hub - Your one-stop platform for study materials, previous year papers, and academic assistance.',
}

export default function RootLayout({ children }) {
  return (
    <>
      <Head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="shortcut icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      </Head>
      <html lang="en" suppressHydrationWarning>
        <body className="min-h-screen bg-background font-sans antialiased">
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange={false}
          >
            {children}
          </ThemeProvider>
        </body>
      </html>
    </>
  )
}