export default function Hero() {
  return (
    <header className="relative min-h-screen flex items-center justify-center pt-24 overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img
          alt="Cinematic underwater coral reef"
          className="w-full h-full object-cover opacity-60 scale-105"
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuC63UVPDlKY6iPATq_3gLLK3iLhpkdjAY9tG2NQdRsw0oDtRwC3t5xhswokGgn56K-UEjMSfEUA7aEbEVRylIqsFq9jKSpAjdFA10k2X9DQF20V5zj2ROTKJoWW1OTU60rJcwmVZTJXRrD5aa1T69siNJk828aKDE78Q23Y3aJF2Cy6xwnKdSXvECmbH3fSVqAGVg8nQbRbK2goBi1XjS_OP5z0cLRp74aEeABWosvhrZllMLS4zrnv4byNI7T6sz5GDCAMNTTuDco"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-surface/40 via-surface/20 to-surface"></div>
      </div>
      <div className="relative z-10 text-center px-margin-mobile md:px-margin-desktop max-w-5xl">
        <div className="mb-8 bioluminescent-glow">
          <svg className="w-48 h-48 mx-auto opacity-80" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle className="text-primary-fixed-dim" cx="100" cy="100" fill="none" r="40" stroke="currentColor" strokeWidth="0.5"></circle>
            <circle className="text-primary-fixed-dim" cx="100" cy="100" fill="none" r="60" stroke="currentColor" strokeWidth="0.2"></circle>
            <path className="text-tertiary" d="M100 40 Q 110 70 100 100 T 100 160" fill="none" stroke="currentColor" strokeWidth="1"></path>
            <path className="text-tertiary" d="M80 50 Q 70 80 90 110 T 80 150" fill="none" stroke="currentColor" strokeWidth="0.5"></path>
            <path className="text-tertiary" d="M120 50 Q 130 80 110 110 T 120 150" fill="none" stroke="currentColor" strokeWidth="0.5"></path>
          </svg>
        </div>
        <h1 className="font-display-xl text-headline-lg md:text-display-xl leading-none mb-4 tracking-tighter text-primary">THE OCEAN IS SENDING SIGNALS.</h1>
        <h2 className="font-headline-lg text-tertiary-fixed-dim mb-6">WE'RE LISTENING.</h2>
        <p className="font-body-md text-on-surface-variant max-w-2xl mx-auto mb-12">One platform monitoring marine stress, endangered species, and ocean health across the Indian coastline in real time.</p>
        <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
          <button className="bg-primary text-on-primary font-bold px-10 py-4 rounded-xl text-lg shadow-[0_0_30px_rgba(0,219,240,0.3)] hover:scale-105 transition-all">Open Live Monitor</button>
          <button className="border border-primary/40 text-primary font-bold px-10 py-4 rounded-xl text-lg glass-primary hover:bg-primary/10 transition-all">How It Works</button>
        </div>
        
        {/* Live Stats Bar */}
        <div className="mt-20 glass rounded-full px-8 py-6 flex flex-wrap justify-center gap-12 border-white/5">
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 bg-primary rounded-full pulse-aqua"></div>
            <div>
              <div className="font-data-point text-display-xs text-primary">04</div>
              <div className="font-label-caps text-on-surface-variant">Active Zones</div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 bg-tertiary rounded-full pulse-aqua" style={{animationDelay: '0.5s'}}></div>
            <div>
              <div className="font-data-point text-display-xs text-tertiary">06</div>
              <div className="font-label-caps text-on-surface-variant">Species Tracked</div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 bg-secondary-fixed-dim rounded-full pulse-aqua" style={{animationDelay: '1s'}}></div>
            <div>
              <div className="font-data-point text-display-xs text-secondary-fixed-dim">06</div>
              <div className="font-label-caps text-on-surface-variant">NGO Partners</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
