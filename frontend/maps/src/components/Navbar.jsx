import { useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()

  return (
    <nav className="fixed top-0 w-full z-50 bg-surface/60 backdrop-blur-xl border-b border-white/10 shadow-[0_0_20px_rgba(0,219,240,0.1)] transition-all duration-300 ease-in-out">
      <div className="flex justify-between items-center px-margin-desktop py-4 max-w-container-max mx-auto">
        <div className="font-display-xl text-headline-lg-mobile text-primary tracking-tighter uppercase">WatchTheBlue</div>
        <div className="hidden md:flex gap-8 font-body-md text-body-md tracking-tight">
          <a className="text-primary font-bold border-b-2 border-primary pb-1" href="#home">Home</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#monitor">Live Monitor</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#zones">Ocean Zones</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#species">Species</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#partners">NGO Partners</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#about">About</a>
        </div>
        <div className="flex items-center gap-6">
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer transition-colors" data-icon="notifications">notifications</span>
          <button
            onClick={() => navigate('/map')}
            className="bg-primary text-on-primary px-6 py-2 rounded-lg font-bold hover:brightness-110 transition-all"
          >
            View Live Map
          </button>
        </div>
      </div>
    </nav>
  )
}
