import './globals.css'
import Head from 'next/head'

export const metadata = {
  title: 'SXC ScholarHub',
  description: 'St. Xavier\'s College Academic Resources Hub - Your one-stop platform for study materials, previous year papers, and academic assistance.',
}

export default function RootLayout({ children }) {
  return (
    <>
      <Head>
        <link rel="icon" href="/sxc-logofinal.png" />
      </Head>
      <html lang="en">
        <body className="min-h-screen bg-background font-sans antialiased">
          {children}
        </body>
      </html>
    </>
  )
}