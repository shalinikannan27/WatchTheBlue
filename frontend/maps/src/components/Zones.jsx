export default function Zones() {
  const zones = [
    { id: 1, name: 'Lakshadweep', stress: 'High', stressColor: 'error' },
    { id: 2, name: 'Andaman', stress: 'Low', stressColor: 'tertiary' },
    { id: 3, name: 'Gulf of Kutch', stress: 'Mid', stressColor: 'secondary-fixed-dim' },
    { id: 4, name: 'Sundarbans', stress: 'High', stressColor: 'error' }
  ]

  const species = [
    {
      name: 'Olive Ridley Turtle',
      threat: 'Vulnerable',
      threatPct: 82,
      threatColor: 'error',
      img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC1SR_6UDv8dmKKRpfM1gJHiThkuK-Pin-OoEtl3-7ytg2uiQkf-4Ey-2_jAYI-I4d65i8VZBlEGMk_27eryQs4fBl7SELYKxGURp-v_WtuADLk5_1MQWBW0A1HSyJ41Ee6i9V4AkWl_iYyo8jYuyjsdXq15J91zTNZLIMTBjHnqXhmKaNYa_jd8zmH8EEP4JqpGRzyxR410n2wJcEKHpG0-3ZLEsMLtfZSTYnP8KvzwG4N5wg5RvNBnt2l3v9eHKKs7YGHkRtubm8'
    },
    {
      name: 'Whale Shark',
      threat: 'Endangered',
      threatPct: 45,
      threatColor: 'tertiary',
      img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBV-8x2B-2aKrXV2Jm4Y8ID0_BxCy388n1mJYs5mreGfgc0tJIlL2JjLL2tEzm93lHNd7_w-DZGXJ_x6VN82BEiu8kzbYZvvVPOgIsTC5EJQdB_va0kZYrhkhfh6K_jzPn-XMFdOlUzgi3osghXnDnEpy5Vovyetjx-JP8GXvEwCWXDQEO9RTXWfPWPrbg9-GvFarG-_lJ0lhiybmVW99j1WLokA6E06lJmDCLe8HgPcMOf95suGnu7Rl4FQhIYv0CT2_zh6DLLJog'
    },
    {
      name: 'Dugong',
      threat: 'Protected',
      threatPct: 68,
      threatColor: 'secondary-fixed-dim',
      img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBbEp86_5ry2NmEprEP149_Mf7DER0CItL0trt0z9aoxud5HsIr4WfavDjxfHWsrz6pjR7wRdUbcO_tc-hapSHSaonSg6teT-eVstJXvfrqjt4xsyP2hRKDVUQyDE6z-xasABJwGdAV0xgBM8Af7RoWUnaw9u67BindMx0ySojW8SMO-Pk4MKOTl6hsF3Ol6Ro4Gihtrl5peJLWWhIPnjfvc7vdV3CnMchUmeQDGZl8z8zbU5QvYOGS1MtLv4YoefpVDXBtgNULlU'
    }
  ]

  const stressColors = {
    error: 'text-error',
    tertiary: 'text-tertiary',
    'secondary-fixed-dim': 'text-secondary-fixed-dim'
  }

  return (
    <>
      <section className="py-32 px-margin-desktop max-w-container-max mx-auto" id="zones">
        <h2 className="font-headline-lg text-on-surface mb-16 text-center uppercase">Coastal Priority Zones</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-32">
          {zones.map(zone => (
            <div key={zone.id} className="glass p-8 border-white/5 hover:border-primary/50 transition-all cursor-pointer">
              <div className="font-label-caps text-primary mb-2">Zone {String(zone.id).padStart(2, '0')}</div>
              <h3 className="font-headline-lg-mobile mb-4">{zone.name}</h3>
              <div className="flex items-center gap-2 mb-6">
                <span className={`w-2 h-2 rounded-full ${zone.stress === 'High' ? 'bg-error animate-pulse' : 'bg-' + (zone.stress === 'Low' ? 'tertiary' : 'secondary-fixed-dim')}`}></span>
                <span className={`text-xs ${zone.stress === 'High' ? 'text-error' : 'text-' + (zone.stress === 'Low' ? 'tertiary' : 'secondary-fixed-dim')}`}>Stress: {zone.stress}</span>
              </div>
              <button className="text-primary font-data-point text-xs flex items-center gap-2">
                ANALYZE SECTOR
                <span className="material-symbols-outlined text-sm" data-icon="chevron_right">chevron_right</span>
              </button>
            </div>
          ))}
        </div>

        <h2 className="font-headline-lg text-on-surface mb-16 text-center uppercase" id="species">Sentinels of the Deep</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {species.map(s => (
            <div key={s.name} className="glass overflow-hidden group">
              <div className="h-64 relative overflow-hidden">
                <img
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  alt={s.name}
                  src={s.img}
                />
                <div className={`absolute top-4 right-4 px-3 py-1 rounded text-xs font-bold text-white uppercase ${s.threat === 'Vulnerable' ? 'bg-error/80' : s.threat === 'Endangered' ? 'bg-tertiary/80' : 'bg-secondary-fixed-dim/80'} backdrop-blur-md`}>
                  {s.threat}
                </div>
              </div>
              <div className="p-8">
                <h3 className="font-headline-lg-mobile mb-4">{s.name}</h3>
                <div className="flex justify-between items-center mb-6">
                  <span className="text-on-surface-variant text-sm">Threat Meter</span>
                  <span className={`font-data-point ${s.threatColor === 'error' ? 'text-error' : s.threatColor === 'tertiary' ? 'text-tertiary' : 'text-secondary-fixed-dim'}`}>{s.threatPct}%</span>
                </div>
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <div className={`h-full ${s.threatColor === 'error' ? 'bg-error' : s.threatColor === 'tertiary' ? 'bg-tertiary' : 'bg-secondary-fixed-dim'}`} style={{width: `${s.threatPct}%`}}></div>
                </div>
                <button className="w-full mt-8 border border-white/10 py-3 font-label-caps hover:bg-white/5 transition-all">LIVE TRACKING</button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}
