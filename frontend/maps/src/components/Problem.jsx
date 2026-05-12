export default function Problem() {
  return (
    <section className="py-32 relative grid-bg">
      <div className="max-w-container-max mx-auto px-margin-desktop">
        <h2 className="font-headline-lg text-primary text-center mb-16 uppercase tracking-widest">THE INDIAN OCEAN IS UNDER STRESS.</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass p-10 border-white/10 hover:border-primary/30 transition-all group">
            <span className="material-symbols-outlined text-primary text-5xl mb-6 block group-hover:scale-110 transition-transform" data-icon="waves">waves</span>
            <h3 className="font-headline-lg-mobile text-on-surface mb-4">2,000+</h3>
            <p className="text-on-surface-variant">Marine animals strand on Indian coasts every year, signal of increasing environmental distress.</p>
          </div>
          <div className="glass p-10 border-white/10 hover:border-error/30 transition-all group">
            <span className="material-symbols-outlined text-error text-5xl mb-6 block group-hover:scale-110 transition-transform" data-icon="thermostat">thermostat</span>
            <h3 className="font-headline-lg-mobile text-on-surface mb-4">1.2°C</h3>
            <p className="text-on-surface-variant">Indian Ocean warming is 1.2°C faster than global average since 1950, disrupting ancient migration patterns.</p>
          </div>
          <div className="glass p-10 border-white/10 hover:border-tertiary/30 transition-all group">
            <span className="material-symbols-outlined text-tertiary text-5xl mb-6 block group-hover:scale-110 transition-transform" data-icon="rebase">rebase</span>
            <h3 className="font-headline-lg-mobile text-on-surface mb-4">40%</h3>
            <p className="text-on-surface-variant">Of Indian coral reefs face severe bleaching threats from unprecedented heatwaves and pollution.</p>
          </div>
        </div>
      </div>
    </section>
  )
}
