export default function Partners() {
  const partners = [
    { icon: 'eco', name: 'ReefWatch' },
    { icon: 'forest', name: 'TREE Foundation' },
    { icon: 'water', name: 'Blue Cross' },
    { icon: 'monitoring', name: 'Marine Life' },
    { icon: 'handshake', name: 'OceanTrust' },
    { icon: 'policy', name: 'Wildlife Prot' }
  ]

  return (
    <section className="py-32 bg-surface-container-low border-y border-white/5" id="partners">
      <div className="max-w-container-max mx-auto px-margin-desktop text-center">
        <h4 className="font-label-caps text-primary mb-4 tracking-widest">Powering Real-World Conservation</h4>
        <h2 className="font-display-xl text-headline-lg md:text-headline-lg mb-20 uppercase">7,500km Coastline Monitored</h2>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-700">
          {partners.map(partner => (
            <div key={partner.name} className="flex flex-col items-center gap-4">
              <span className="material-symbols-outlined text-4xl text-primary" data-icon={partner.icon}>{partner.icon}</span>
              <span className="font-label-caps">{partner.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
