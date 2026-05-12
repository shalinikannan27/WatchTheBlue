import Map from './Map'

export default function LiveMonitor() {
  return (
    <section className="min-h-[600px] bg-surface-container relative flex flex-col" id="monitor">
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="w-full h-full grid-bg"></div>
      </div>
      
      <div className="p-8 flex justify-between items-center relative z-20">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-4 py-1 rounded-full border border-error/50 bg-error/10">
            <span className="w-2 h-2 bg-error rounded-full animate-pulse"></span>
            <span className="text-error font-label-caps">LIVE FEED</span>
          </div>
          <div className="flex gap-4">
            <button className="px-4 py-1 font-label-caps border border-primary/20 text-primary hover:bg-primary/10 transition-all">Arabian Sea</button>
            <button className="px-4 py-1 font-label-caps border border-primary text-primary bg-primary/10">Bay of Bengal</button>
            <button className="px-4 py-1 font-label-caps border border-primary/20 text-primary hover:bg-primary/10 transition-all">Lakshadweep</button>
          </div>
        </div>
        <div className="text-on-surface-variant font-data-point">08°12'26"N 76°15'32"E</div>
      </div>

      <div className="flex-1 relative flex items-center justify-center p-margin-desktop overflow-hidden">
        {/* Map Container */}
        <div className="relative w-full h-[500px] rounded-xl overflow-hidden border border-white/5 shadow-2xl">
          <Map />
        </div>
      </div>
    </section>
  )
}
