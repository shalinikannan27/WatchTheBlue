import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Problem from './components/Problem'
import HowItWorks from './components/HowItWorks'
import LiveMonitor from './components/LiveMonitor'
import Zones from './components/Zones'
import Partners from './components/Partners'
import Signup from './components/Signup'
import Footer from './components/Footer'
import './App.css'

function App() {
  return (
    <div className="w-screen bg-background overflow-x-hidden">
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <HowItWorks />
        <LiveMonitor />
        <Zones />
        <Partners />
        <Signup />
      </main>
      <Footer />
    </div>
  )
}

export default App