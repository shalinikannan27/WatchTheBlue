import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Problem from './components/Problem'
import HowItWorks from './components/HowItWorks'
import Zones from './components/Zones'
import Partners from './components/Partners'
import Signup from './components/Signup'
import Footer from './components/Footer'
import MapPage from './components/MapPage'
import './App.css'

function HomePage() {
  return (
    <div className="w-screen bg-background overflow-x-hidden">
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <HowItWorks />
        <Zones />
        <Partners />
        <Signup />
      </main>
      <Footer />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/map" element={<MapPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App