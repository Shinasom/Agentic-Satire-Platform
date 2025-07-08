import { Inter, Lora } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const lora = Lora({ subsets: ['latin'], variable: '--font-lora' })

export const metadata = {
  title: 'The Absurd Chronicle',
  description: 'AI-Generated Satire. Mostly.',
}

// Reusable Header Component
function Header() {
  // Added a bottom border to the nav for better separation
  return (
    <header className="border-b bg-white">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="text-3xl font-serif font-bold text-brand-red">
            The Absurd Chronicle
          </Link>
          <p className="text-sm text-gray-500 hidden sm:block">
            Tuesday, July 8, 2025
          </p>
        </div>
        <nav className="border-t">
          {/* Added a subtle transition to the hover effect */}
          <ul className="flex space-x-6 text-sm font-semibold text-gray-700 py-2">
            <li><Link href="/?category=India" className="hover:text-brand-red transition-colors duration-200">India</Link></li>
            <li><Link href="/?category=World" className="hover:text-brand-red transition-colors duration-200">World</Link></li>
            <li><Link href="/?category=Business" className="hover:text-brand-red transition-colors duration-200">Business</Link></li>
            <li><Link href="/?category=Tech" className="hover:text-brand-red transition-colors duration-200">Tech</Link></li>
            {/* Changed Cricket to Sports */}
            <li><Link href="/?category=Sports" className="hover:text-brand-red transition-colors duration-200">Sports</Link></li>
            <li><Link href="/?category=Entertainment" className="hover:text-brand-red transition-colors duration-200">Entertainment</Link></li>
          </ul>
        </nav>
      </div>
    </header>
  )
}

// Reusable Footer Component
function Footer() {
  return (
    <footer className="bg-gray-800 text-gray-400 mt-16">
      <div className="container mx-auto px-4 py-8">
        <p>&copy; 2025 The Absurd Chronicle. All Rights Reserved.</p>
        <p className="text-sm mt-2">This is a satirical website for entertainment purposes. Do not take it seriously.</p>
      </div>
    </footer>
  )
}


export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${lora.variable}`}>
      <body className="font-sans bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  )
}