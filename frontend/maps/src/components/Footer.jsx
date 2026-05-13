export default function Footer() {
  return (
    <footer className="bg-surface-container-lowest border-t border-white/5 py-12 px-margin-desktop">
      <div className="max-w-container-max mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="font-headline-lg text-primary uppercase text-2xl tracking-tighter">WatchTheBlue</div>
        <div className="flex flex-wrap justify-center gap-8 font-body-sm text-body-sm text-on-surface-variant">
          <a className="hover:text-tertiary transition-colors" href="#privacy">Privacy Policy</a>
          <a className="hover:text-tertiary transition-colors" href="#terms">Terms of Service</a>
          <a className="hover:text-tertiary transition-colors" href="#credits">Research Credits</a>
          <a className="hover:text-tertiary transition-colors" href="#partner">Partner Portal</a>
        </div>
        <div className="text-tertiary font-body-sm text-body-sm opacity-80 hover:opacity-100 transition-opacity">
          © 2024 WatchTheBlue. Mission-critical marine intelligence.
        </div>
      </div>
      <div className="text-center mt-8 text-[10px] uppercase tracking-[0.3em] text-white/20">
        Powered by Social Hackathon Credits & Satellite Telemetry
      </div>
    </footer>
  )
}
