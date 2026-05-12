export default function Signup() {
  return (
    <section className="py-32 px-margin-desktop">
      <div className="max-w-container-max mx-auto grid grid-cols-1 md:grid-cols-2 gap-20 items-center">
        <div>
          <h2 className="font-display-xl text-headline-lg leading-tight text-primary mb-8">GET OCEAN ALERTS BEFORE DISASTER STRIKES.</h2>
          <p className="text-on-surface-variant max-w-md">Join a network of thousands dedicated to immediate marine intervention. Choose your mission profile to begin.</p>
        </div>
        <div className="glass p-10 border-white/10 rounded-2xl relative">
          <div className="flex gap-4 mb-10 border-b border-white/10">
            <button className="pb-4 font-label-caps text-primary border-b-2 border-primary">As NGO Partner</button>
            <button className="pb-4 font-label-caps text-on-surface-variant hover:text-white transition-colors">As Citizen Scientist</button>
          </div>
          <form className="space-y-6">
            <div>
              <label className="block font-label-caps text-xs text-on-surface-variant mb-2">Full Legal Name</label>
              <input
                className="w-full bg-white/5 border border-white/10 rounded-lg p-4 focus:border-primary focus:ring-0 text-white"
                placeholder="Dr. Sarah K."
                type="text"
              />
            </div>
            <div>
              <label className="block font-label-caps text-xs text-on-surface-variant mb-2">Professional Email</label>
              <input
                className="w-full bg-white/5 border border-white/10 rounded-lg p-4 focus:border-primary focus:ring-0 text-white"
                placeholder="sarah@ocean-research.org"
                type="email"
              />
            </div>
            <button className="w-full bg-primary text-on-primary font-bold py-5 rounded-xl uppercase tracking-widest hover:brightness-110 transition-all">
              Request Mission Credentials
            </button>
          </form>
        </div>
      </div>
    </section>
  )
}
