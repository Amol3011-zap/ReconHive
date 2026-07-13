import './globals.css'

export const metadata = {
  title: 'ReconHive - Enterprise Security Assessment',
  description: 'Enterprise Security Assessment Management Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-slate-950 text-slate-50">
        {children}
      </body>
    </html>
  )
}
