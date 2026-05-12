export default function HowItWorks() {
  return (
    <section className="py-32 bg-surface-container-lowest">
      <div className="max-w-container-max mx-auto px-margin-desktop text-center">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter relative">
          {/* Connectors for Desktop */}
          <div className="hidden md:block absolute top-1/2 left-1/3 w-1/3 border-t-2 border-dashed border-primary/20 -translate-y-1/2"></div>
          <div className="hidden md:block absolute top-1/2 left-2/3 w-1/3 border-t-2 border-dashed border-primary/20 -translate-y-1/2"></div>
          
          <div className="flex flex-col items-center">
            <div className="w-24 h-24 rounded-full glass-primary flex items-center justify-center mb-8 relative z-10">
              <span className="material-symbols-outlined text-primary text-4xl" data-icon="sensors">sensors</span>
            </div>
            <h4 className="font-label-caps text-primary mb-2">Step 1</h4>
            <h3 className="font-headline-lg-mobile text-on-surface mb-4 uppercase">We Collect</h3>
            <p className="text-on-surface-variant font-body-sm">Deep-sea buoys, orbital satellites, and shoreline acoustic sensors harvest petabytes of environmental data.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-24 h-24 rounded-full glass-primary flex items-center justify-center mb-8 relative z-10">
              <span className="material-symbols-outlined text-primary text-4xl" data-icon="memory">memory</span>
            </div>
            <h4 className="font-label-caps text-primary mb-2">Step 2</h4>
            <h3 className="font-headline-lg-mobile text-on-surface mb-4 uppercase">We Compute</h3>
            <p className="text-on-surface-variant font-body-sm">The Ocean Health Engine processes live feeds with proprietary AI to detect anomalies and stress events.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-24 h-24 rounded-full glass-primary flex items-center justify-center mb-8 relative z-10">
              <span className="material-symbols-outlined text-primary text-4xl" data-icon="emergency_share">emergency_share</span>
            </div>
            <h4 className="font-label-caps text-primary mb-2">Step 3</h4>
            <h3 className="font-headline-lg-mobile text-on-surface mb-4 uppercase">We Alert</h3>
            <p className="text-on-surface-variant font-body-sm">Instant protocols are triggered, deploying NGO partners for rapid rescue and habitat stabilization.</p>
          </div>
        </div>
      </div>
    </section>
  )
}
