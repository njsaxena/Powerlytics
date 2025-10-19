import type { AppProps } from 'next/app'
import '../styles/globals.css'
import { EnergyProvider } from '../lib/context/EnergyContext'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <EnergyProvider>
      <Component {...pageProps} />
    </EnergyProvider>
  )
}
