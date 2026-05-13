import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  ChevronRight, 
  Radio, 
  MapPin, 
  Activity, 
  Waves,
  ExternalLink,
  Thermometer,
  Cpu,
  Target,
  History,
  FileText
} from 'lucide-react';

const CARDS = [
  {
    id: '01',
    icon: <Waves className="w-8 h-8 text-cyan-400" />,
    title: '2,000+',
    description: 'Marine animals strand on Indian coasts every year, signaling increasing environmental distress.',
    buttonText: 'Analysis',
  },
  {
    id: '02',
    icon: <Thermometer className="w-8 h-8 text-pink-400" />,
    title: '1.2°C',
    description: 'Indian Ocean warming faster than global average since 1950, disrupting ancient migration patterns.',
    buttonText: 'Metrics',
  },
  {
    id: '03',
    icon: <Activity className="w-8 h-8 text-emerald-400" />,
    title: '40%',
    description: 'Of Indian coral reefs face severe bleaching threats from unusual heatwaves and pollution.',
    buttonText: 'Reports',
  }
];

// Workflow Data
const WORKFLOW_STEPS = [
  {
    step: "STEP 1",
    title: "COLLECT",
    subtitle: "Intelligence Gathering",
    description: "Data from CMEMS, NOAA, NASA, and OBIS: temp, oxygen, pH, salinity, currents, and species signals.",
    icon: <Radio className="w-6 h-6 text-white" />
  },
  {
    step: "STEP 2",
    title: "CALCULATE",
    subtitle: "Stress Score Engine",
    description: "Environmental data processed through the Stress Score Formula to measure ecosystem vulnerability.",
    icon: <Cpu className="w-6 h-6 text-white" />
  },
  {
    step: "STEP 3",
    title: "PREDICT",
    subtitle: "XGBoost Risk AI",
    description: "ML model predicts strandings and bleaching by analyzing stress signals and historical patterns.",
    icon: <Target className="w-6 h-6 text-white" />
  },
  {
    step: "STEP 4",
    title: "BACKTRACK",
    subtitle: "Origin Analysis",
    description: "Conditions reconstructed to identify the cause, origin, and timeline behind marine incidents.",
    icon: <History className="w-6 h-6 text-white" />
  },
  {
    step: "STEP 5",
    title: "VISUALIZE",
    subtitle: "Interactive Mapping",
    description: "Risks, incidents, and predictions shown on a Leaflet map with precise location insights.",
    icon: <MapPin className="w-6 h-6 text-white" />
  },
  {
    step: "STEP 6",
    title: "REPORT",
    subtitle: "PDF Generation",
    description: "Downloadable reports containing risks, conditions, predictions, and incident analysis.",
    icon: <FileText className="w-6 h-6 text-white" />
  },
  {
    step: "STEP 7",
    title: "ALERT",
    subtitle: "NGO Automation",
    description: "Critical incidents sent to nearby NGOs via WhatsApp/email using agentic workflows.",
    icon: <Bell className="w-6 h-6 text-white" />
  }
];
const OCEAN_ZONES = [
  {
    id: '01',
    name: 'Lakshadweep Sea',
    stress: 'Medium',
    stressColor: 'text-orange-400',
    dotColor: 'bg-orange-400',
    key: 'Coral Reefs, Reef Fish',
    ngos: 1,
    image: '/species_image/species_image/clownfish.jpg'
  },
  {
    id: '02',
    name: 'Andaman Sea',
    stress: 'Low',
    stressColor: 'text-emerald-400',
    dotColor: 'bg-emerald-400',
    key: 'Dugong, Sea Turtle, Coral',
    ngos: 1,
    image: '/species_image/species_image/dungoung.jpg'
  },
  {
    id: '03',
    name: 'Arabian Sea',
    stress: 'Moderate',
    stressColor: 'text-yellow-400',
    dotColor: 'bg-yellow-400',
    key: 'Whale Shark, Spinner Dolphin',
    ngos: 1,
    image: '/species_image/species_image/whale shark.jpg'
  },
  {
    id: '04',
    name: 'Bay of Bengal',
    stress: 'High',
    stressColor: 'text-red-400',
    dotColor: 'bg-red-400',
    key: 'Olive Ridley, Humpback Dolphin',
    ngos: 1,
    image: '/species_image/species_image/Olive ridley sea turtle.jpg'
  }
];

const NGO_PARTNERS = [
  { 
    name: 'ReefWatch Marine Conservation', 
    impact: 'Coral Restoration & Reef Monitoring', 
    location: 'Andaman & Nicobar Islands', 
    website: 'https://reefwatchindia.org', 
    image: '/species1.png',
    focus: 'Restoring damaged coral ecosystems and marine life rescue.'
  },
  { 
    name: 'TREE Foundation', 
    impact: 'Sea Turtle Protection & Education', 
    location: 'Chennai Coast', 
    website: 'https://www.treefoundationindia.org', 
    image: '/species1.png',
    focus: 'Community-led sea turtle conservation and youth education.'
  },
  { 
    name: 'Wildlife Trust of India', 
    impact: 'Species Recovery & Policy', 
    location: 'Gulf of Kutch & Mithapur', 
    website: 'https://www.wti.org.in', 
    image: '/species2.png',
    focus: 'Conserving wildlife and its habitat through legal and field action.'
  },
  { 
    name: 'Terra Conscious / IUCN India', 
    impact: 'Marine Conservation & Eco-Tourism', 
    location: 'Goa Coastline', 
    website: 'https://www.terraconscious.com', 
    image: '/species4.png',
    focus: 'Promoting responsible interaction with marine ecosystems.'
  },
  { 
    name: 'Coastal Impact', 
    impact: 'Research & Biodiversity Monitoring', 
    location: 'Goa & Western Ghats', 
    website: 'https://coastalimpact.in', 
    image: '/species6.png',
    focus: 'Scientific diving and ecosystem health assessments.'
  },
  { 
    name: 'SMRC Kerala', 
    impact: 'Marine Research & Local Governance', 
    location: 'Cochin, Kerala', 
    website: 'http://www.smrcindia.in', 
    image: '/species3.png',
    focus: 'Linking scientific research with coastal community welfare.'
  },
];

const SPECIES = [
  { name: 'Olive Ridley Turtle', region: 'Bay of Bengal', status: 'Vulnerable', statusColor: 'text-orange-400', temp: '24-30°C', o2: '4-8 mg/L', threat: 82, image: '/species_image/species_image/Olive ridley sea turtle.jpg' },
  { name: 'Whale Shark', region: 'Gujarat Coast', status: 'Endangered', statusColor: 'text-red-400', temp: '21-30°C', o2: '3.5-7 mg/L', threat: 45, image: '/species_image/species_image/whale shark.jpg' },
  { name: 'Dugong', region: 'Andaman Sea', status: 'Protected', statusColor: 'text-emerald-400', temp: '23-30°C', o2: '4-7 mg/L', threat: 68, image: '/species_image/species_image/dungoung.jpg' },
  { name: 'Spinner Dolphin', region: 'Lakshadweep', status: 'Vulnerable', statusColor: 'text-orange-400', temp: '24-29°C', o2: '5-8 mg/L', threat: 55, image: '/species_image/species_image/spinner dolphin.jpg' },
  { name: 'Humpback Whale', region: 'Arabian Sea', status: 'Recovering', statusColor: 'text-blue-400', temp: '18-28°C', o2: '5-9 mg/L', threat: 35, image: '/species_image/species_image/humpback whale.jpg' },
  { name: 'Manta Ray', region: 'Lakshadweep', status: 'Vulnerable', statusColor: 'text-orange-400', temp: '24-30°C', o2: '4-8 mg/L', threat: 60, image: '/species_image/species_image/manta ray.jpg' },
  { name: 'Reef Shark', region: 'Andaman Sea', status: 'Near Threatened', statusColor: 'text-yellow-400', temp: '22-30°C', o2: '4-7 mg/L', threat: 50, image: '/species_image/species_image/reef shark.jpg' },
  { name: 'Clownfish', region: 'Gulf of Kutch', status: 'Declining', statusColor: 'text-slate-400', temp: '26-30°C', o2: '5-8 mg/L', threat: 40, image: '/species_image/species_image/clownfish.jpg' },
  { name: 'Blue Whale', region: 'Deep Indian Ocean', status: 'Endangered', statusColor: 'text-red-400', temp: '15-25°C', o2: '6-9 mg/L', threat: 30, image: '/species_image/species_image/blue whale.jpg' },
  { name: 'Green Sea Turtle', region: 'Lakshadweep', status: 'Endangered', statusColor: 'text-red-400', temp: '24-30°C', o2: '4-7 mg/L', threat: 75, image: '/species_image/species_image/Green sea turtle.jpg' },
];

function NGOCard({ ngo, idx }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.05 }}
      className="bg-[#02182b]/60 backdrop-blur-sm border border-white/5 rounded-xl p-5 flex flex-col group hover:border-cyan-400/30 transition-all duration-300 shadow-xl min-h-[160px] justify-between"
    >
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-start gap-4">
          <h3 className="text-lg font-black text-white tracking-tight leading-tight group-hover:text-cyan-400 transition-colors">{ngo.name}</h3>
          <div className="flex items-center gap-1.5 shrink-0 px-2 py-0.5 bg-cyan-400/10 rounded-full border border-cyan-400/20">
            <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full shadow-[0_0_8px_#22d3ee]" />
            <p className="text-[0.55rem] text-cyan-400 font-black uppercase tracking-wider">{ngo.location.split(',')[0]}</p>
          </div>
        </div>

        <div className="mt-1">
          <p className="text-xs font-bold text-white/80 leading-snug line-clamp-1">{ngo.impact}</p>
          <p className="text-[0.65rem] text-white/40 leading-relaxed font-medium italic mt-1 line-clamp-2">
            "{ngo.focus}"
          </p>
        </div>
      </div>

      <a 
        href={ngo.website} 
        target="_blank" 
        rel="noopener noreferrer"
        className="mt-4 w-full py-2 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center gap-2 text-[0.6rem] font-black uppercase tracking-[0.2em] text-white/80 hover:bg-cyan-500 hover:text-[#02182b] hover:border-cyan-500 transition-all group/link"
      >
        Explore Partner
        <ExternalLink className="w-3 h-3 group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
      </a>
    </motion.div>
  );
}

function SpeciesCard({ species, idx }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: idx * 0.1 }}
      className="bg-[#02182b]/80 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden flex flex-col group hover:border-cyan-400/50 transition-all duration-500 shadow-2xl"
    >
      <div className="relative h-44 overflow-hidden">
        <img src={species.image} alt={species.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
        <div className="absolute top-4 right-4 px-3 py-1 bg-black/40 backdrop-blur-md rounded-full border border-white/10">
          <span className={`text-[0.6rem] font-black uppercase tracking-widest ${species.statusColor}`}>{species.status}</span>
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-[#02182b] to-transparent opacity-60" />
        <div className="absolute bottom-4 left-6">
          <h3 className="text-xl font-black text-white tracking-tight leading-none mb-1">{species.name}</h3>
          <p className="text-[0.65rem] text-white/60 font-bold uppercase tracking-wider">{species.region}</p>
        </div>
      </div>
      
      <div className="p-6 flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white/5 border border-white/10 rounded-xl p-3">
            <span className="text-[0.55rem] text-white/40 uppercase font-bold tracking-widest block mb-1">Temp</span>
            <span className="text-xs font-black text-white">{species.temp}</span>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-3">
            <span className="text-[0.55rem] text-white/40 uppercase font-bold tracking-widest block mb-1">O₂</span>
            <span className="text-xs font-black text-white">{species.o2}</span>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-end mb-2">
            <span className="text-[0.6rem] text-white/60 uppercase font-black tracking-widest">Threat Level</span>
            <span className={`text-xs font-black ${species.threat > 70 ? 'text-red-400' : 'text-cyan-400'}`}>{species.threat}%</span>
          </div>
          <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${species.threat}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className={`h-full rounded-full ${species.threat > 70 ? 'bg-red-400' : 'bg-cyan-400 shadow-[0_0_8px_#06b6d4]'}`}
            />
          </div>
        </div>

        <button className="mt-2 w-full py-2.5 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center gap-2 text-[0.6rem] font-black uppercase tracking-[0.2em] text-white hover:bg-white/10 transition-all group/btn">
          <MapPin className="w-3 h-3 text-cyan-400 group-hover/btn:scale-125 transition-transform" />
          Live Tracking
        </button>
      </div>
    </motion.div>
  );
}

function WorkflowCard({ step, idx, hoveredStep, setHoveredStep }: any) {
  const isHovered = hoveredStep === step.step;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 * idx }}
      onHoverStart={() => setHoveredStep(step.step)}
      onHoverEnd={() => setHoveredStep(null)}
      className="relative flex flex-col items-center flex-1 min-w-[120px] transition-all duration-500 group"
    >
      <motion.div 
        className="flex flex-col items-center w-full relative z-10 py-2"
        animate={{ 
          filter: isHovered ? 'blur(8px)' : 'blur(0px)', 
          opacity: isHovered ? 0.1 : 1,
          scale: isHovered ? 0.95 : 1
        }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <div className={`w-16 h-16 rounded-full bg-[#02182b] border transition-all duration-500 flex items-center justify-center mb-4 z-10 
          ${isHovered ? 'border-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.4)]' : 'border-white/10'}`}>
          {step.icon}
        </div>
        
        <span className="text-[0.5rem] font-bold tracking-[0.2em] text-cyan-400 mb-1 uppercase">{step.step}</span>
        <h4 className="text-xs font-black text-white uppercase tracking-tighter mb-2 drop-shadow-sm">{step.title}</h4>
      </motion.div>

      <AnimatePresence>
        {isHovered && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="absolute inset-x-[-40px] top-[-20px] bottom-[-20px] z-20 flex flex-col items-center justify-center p-6 bg-[#02182b]/95 backdrop-blur-md rounded-xl border border-cyan-400/50 shadow-[0_0_40px_rgba(34,211,238,0.3)]"
          >
            <h4 className="text-[0.9rem] font-black text-cyan-400 uppercase tracking-[0.1em] mb-4 text-center leading-tight">
              {step.subtitle}
            </h4>
            <p className="text-[0.85rem] text-white/90 leading-relaxed text-center font-bold">
              {step.description}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function StatItem({ label, value, color }: { label: string, value: string, color: 'cyan' | 'emerald' | 'orange' }) {
  const colorMap = {
    cyan: 'bg-cyan-400',
    emerald: 'bg-emerald-400',
    orange: 'bg-orange-300'
  };

  return (
    <div className="flex items-center gap-4">
      <div className={`w-3 h-3 rounded-full ${colorMap[color]} shadow-[0_0_8px_currentColor]`} />
      <div className="flex flex-col items-start text-left">
        <span className="text-2xl font-mono font-bold tracking-widest text-white leading-none mb-1">{value}</span>
        <span className="text-[0.65rem] font-bold tracking-[0.15em] uppercase text-white/60">{label}</span>
      </div>
    </div>
  );
}

function ZoneCard({ zone, idx }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 * idx, duration: 0.5 }}
      className="group relative bg-[#02182b]/80 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden hover:border-cyan-400/50 transition-all duration-500 shadow-xl"
    >
      <div className="relative h-48 w-full overflow-hidden">
        <img 
          src={zone.image} 
          alt={zone.name} 
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" 
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#02182b] to-transparent opacity-60" />
      </div>

      <div className="p-6">
        <span className="text-[0.65rem] font-bold tracking-[0.2em] text-cyan-400 uppercase mb-2 block">{`ZONE ${zone.id}`}</span>
        <h3 className="text-xl font-black text-white mb-4 tracking-tight">{zone.name}</h3>
        
        <div className="flex items-center gap-2 mb-4">
          <div className={`w-2 h-2 rounded-full ${zone.dotColor} shadow-[0_0_8px_currentColor]`} />
          <span className={`text-xs font-bold uppercase tracking-wider ${zone.stressColor}`}>
            Stress: {zone.stress}
          </span>
        </div>

        <p className="text-[0.7rem] text-white/60 leading-relaxed font-medium mb-6">
          <span className="text-white/80">Key:</span> {zone.key} · {zone.ngos} NGO{zone.ngos > 1 ? 's' : ''} active
        </p>

        <button className="flex items-center gap-2 text-[0.65rem] font-black uppercase tracking-[0.15em] text-cyan-400 hover:text-white transition-colors">
          View on Map <ChevronRight className="w-3 h-3" />
        </button>
      </div>
    </motion.div>
  );
}

function App() {

  const [activeCard, setActiveCard] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0); 
  const [hoveredStep, setHoveredStep] = useState<string | null>(null);

  const bgImage = "/c1b3e851af2b6979c4770070f5e2f779.jpg"; 

  const nextPage = () => setCurrentPage((prev) => {
    if (prev <= 1) return prev === 1 ? 0 : 1;
    if (prev >= 4 && prev <= 6) return prev === 6 ? 4 : prev + 1;
    return prev;
  });
  
  const prevPage = () => setCurrentPage((prev) => {
    if (prev <= 1) return prev === 0 ? 1 : 0;
    if (prev >= 4 && prev <= 6) return prev === 4 ? 6 : prev - 1;
    return prev;
  });

  return (
    <div className="relative h-screen w-full overflow-hidden text-white font-sans bg-gray-900">
      <motion.div 
        className="absolute inset-0 z-0"
        initial={{ scale: 1.1 }}
        animate={{ scale: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
      >
        <img 
          src={bgImage} 
          alt="Ocean Background" 
          className="w-full h-full object-cover object-center"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-teal-900/60 via-transparent to-black/40 mix-blend-multiply" />
        <div className="absolute inset-0 bg-black/40" />
      </motion.div>

      <div className="relative z-10 flex flex-col h-full justify-between pt-28 pb-12 px-6 lg:px-16 overflow-hidden">
        
        <header className="absolute top-6 left-1/2 -translate-x-1/2 z-50 flex items-center w-[95%] xl:w-[85%] max-w-7xl shrink-0 pl-6 pr-4 py-1.5 bg-[#f0f9ff]/80 backdrop-blur-md border border-white/60 rounded-full shadow-[0_8px_32px_rgba(0,50,100,0.15)]">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-6"
            onClick={() => setCurrentPage(0)}
            style={{ cursor: 'pointer' }}
          >
            <div className="relative flex items-center justify-center -my-2 -ml-3">
              <div className="absolute w-10 h-10 bg-white/60 blur-xl rounded-full"></div>
              <img src="/logo.png" alt="Logo" className="relative z-10 w-16 h-16 object-contain drop-shadow-sm" />
            </div>
            <div className="flex flex-col justify-center">
              <div className="text-xl tracking-tight leading-none">
                <span className="font-['Montserrat'] font-bold text-[#083344] drop-shadow-sm">WatchThe</span>
                <span className="font-['Fraunces'] font-bold text-[#0284c7] drop-shadow-sm">Blue</span>
              </div>
            </div>
          </motion.div>

          <div className="flex-1"></div>

          <motion.div className="flex items-center">
            <motion.nav 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="hidden lg:flex items-center gap-4 xl:gap-6 text-sm font-semibold whitespace-nowrap"
            >
              <a href="#" onClick={() => setCurrentPage(0)} className={`transition-all relative group py-1 px-1 ${currentPage <= 1 ? 'text-[#0284c7]' : 'text-slate-600 hover:text-[#083344]'}`}>
                Home
              </a>
              <a href="#" onClick={() => setCurrentPage(2)} className={`transition-all relative group py-1 px-1 ${currentPage === 2 ? 'text-[#0284c7]' : 'text-slate-600 hover:text-[#083344]'}`}>
                Live Monitor
              </a>
              <a href="#" onClick={() => setCurrentPage(3)} className={`transition-all relative group py-1 px-1 ${currentPage === 3 ? 'text-[#0284c7]' : 'text-slate-600 hover:text-[#083344]'}`}>
                Ocean Zones
              </a>
              <a href="#" onClick={() => setCurrentPage(4)} className={`transition-all relative group py-1 px-1 ${currentPage >= 4 && currentPage <= 6 ? 'text-[#0284c7]' : 'text-slate-600 hover:text-[#083344]'}`}>
                Species
              </a>
              <a href="#" onClick={() => setCurrentPage(7)} className={`transition-all relative group py-1 px-1 ${currentPage === 7 ? 'text-[#0284c7]' : 'text-slate-600 hover:text-[#083344]'}`}>
                NGO Partners
              </a>
              <a href="#" onClick={() => setCurrentPage(8)} className={`transition-all relative group py-1 px-1 ${currentPage === 8 ? 'text-[#0284c7]' : 'text-slate-600 hover:text-[#083344]'}`}>
                Join
              </a>
              
              <div className="w-[1px] h-5 bg-slate-300 mx-1 shrink-0"></div>
              
              <button title="Notifications" className="text-slate-600 hover:text-[#083344] transition-colors p-1 shrink-0">
                <Bell className="w-5 h-5" />
              </button>
              <button className="ml-1 px-6 py-1.5 bg-white/80 border border-[#bae6fd] text-[#0284c7] font-bold rounded-full hover:bg-[#0284c7] hover:text-white transition-all duration-300 shadow-sm hover:shadow-md whitespace-nowrap shrink-0">
                View Map
              </button>
            </motion.nav>
          </motion.div>
        </header>

        <div className="flex-1 flex flex-col justify-center min-h-0">
          <AnimatePresence mode="wait">
            {currentPage === 0 && (
              <motion.div 
                key="home"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
                className="grid grid-cols-1 lg:grid-cols-12 gap-8 w-full"
              >
                <div className="lg:col-span-6 flex flex-col justify-center h-full max-w-2xl">
                  <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-2 lg:mb-4 tracking-tight uppercase leading-[0.9] text-[#CCF2F4]">
                    The Ocean is <br /> Sending <br /> Signals.
                  </h1>
                  
                  <h2 className="text-base md:text-xl font-bold text-cyan-400 tracking-widest uppercase mb-4 lg:mb-6">
                    We're Listening.
                  </h2>
                  
                  <p className="text-white/80 text-sm md:text-base leading-relaxed max-w-xl">
                    One platform monitoring marine stress, endangered species, and ocean health across the Indian coastline in real time.
                  </p>
                </div>

                <div className="lg:col-span-6 grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 items-center">
                  {CARDS.map((card, idx) => (
                    <motion.div
                      key={card.id}
                      initial={{ opacity: 0, y: 50 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx, duration: 0.6 }}
                      onHoverStart={() => setActiveCard(card.id)}
                      onHoverEnd={() => setActiveCard(null)}
                      className={`relative p-6 lg:p-8 rounded-2xl backdrop-blur-md transition-all duration-500 ease-out cursor-pointer overflow-hidden border h-[220px] lg:h-[260px] flex flex-col
                        ${activeCard === card.id ? 'bg-cyan-500/30 shadow-2xl border-cyan-400/50 translate-y-[-10px]' : 'bg-white/10 border-white/20'}`}
                    >
                      <div className="absolute -top-4 -right-2 text-8xl font-black text-white/5 select-none pointer-events-none z-0">
                        {card.id}
                      </div>
                      
                      <motion.div 
                        className="relative z-10 flex-1 flex flex-col"
                        animate={{ 
                          opacity: activeCard === card.id ? 0.05 : 1,
                          filter: activeCard === card.id ? 'blur(20px)' : 'blur(0px)'
                        }}
                        transition={{ duration: 0.4, ease: "easeOut" }}
                      >
                        <div className="mb-2 lg:mb-4">{card.icon}</div>
                        <h3 className="text-2xl lg:text-3xl font-black mb-2 lg:mb-3 leading-tight text-white">{card.title}</h3>
                        <p className="text-[0.7rem] lg:text-xs text-white/70 leading-relaxed">
                          {card.description}
                        </p>
                      </motion.div>
                      
                      <AnimatePresence>
                        {activeCard === card.id && (
                          <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-4 bg-cyan-950/40 backdrop-blur-[2px]"
                          >
                            <motion.button 
                              initial={{ scale: 0.8, y: 10 }}
                              animate={{ scale: 1, y: 0 }}
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.95 }}
                              className="w-12 h-12 lg:w-16 lg:h-16 rounded-full bg-cyan-400 text-[#02182b] flex items-center justify-center shadow-[0_0_25px_rgba(34,211,238,0.6)]"
                            >
                              <span className="text-2xl lg:text-3xl font-bold">+</span>
                            </motion.button>
                            <motion.span 
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: 0.1 }}
                              className="text-[0.6rem] lg:text-sm font-black uppercase tracking-[0.25em] text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]"
                            >
                              {card.buttonText}
                            </motion.span>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {currentPage === 1 && (
              <motion.div 
                key="workflow"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
                className="w-full flex flex-col items-center justify-center relative"
              >
                <h2 className="text-center text-2xl lg:text-3xl font-bold tracking-widest text-[#CCF2F4] uppercase mb-8 lg:mb-12 drop-shadow-md">
                  How it works
                </h2>

                <div className="relative flex flex-row justify-between items-start w-full max-w-[95%] mx-auto z-10 gap-2">
                  <div className="hidden md:block absolute top-[2rem] left-[5%] right-[5%] h-[1px] border-t border-dashed border-white/10 z-0" />
                  
                  {WORKFLOW_STEPS.map((step, idx) => (
                    <WorkflowCard 
                      key={step.step} 
                      step={step} 
                      idx={idx} 
                      hoveredStep={hoveredStep} 
                      setHoveredStep={setHoveredStep} 
                    />
                  ))}
                </div>

                <motion.div 
                  initial={{ scale: 0.9, opacity: 0, y: 10 }}
                  animate={{ scale: 1, opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="w-full max-w-4xl mx-auto py-3 lg:py-4 px-8 rounded-2xl bg-[#02182b]/60 border border-white/5 flex flex-row justify-around items-center mt-8 lg:mt-12 shadow-2xl backdrop-blur-sm"
                >
                  <StatItem label="Active Zones" value="04" color="cyan" />
                  <StatItem label="Species Tracked" value="10" color="emerald" />
                  <StatItem label="NGO Partners" value="06" color="orange" />
                </motion.div>
              </motion.div>
            )}

            {currentPage === 2 && (
              <motion.div
                key="coming-soon"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex flex-col items-center justify-center text-center"
              >
                <Radio className="w-12 h-12 lg:w-16 lg:h-16 text-cyan-400 mb-4 lg:mb-6 animate-pulse" />
                <h2 className="text-4xl lg:text-6xl font-black uppercase tracking-tighter text-white mb-2 lg:mb-4">Live Monitor</h2>
                <div className="h-[2px] w-16 lg:w-24 bg-cyan-400/30 mb-4 lg:mb-6"></div>
                <p className="text-cyan-400 font-bold tracking-[0.4em] uppercase text-xs lg:text-sm">Deployment In Progress</p>
                <p className="text-white/40 text-[0.6rem] lg:text-xs mt-3 lg:mt-4 font-medium uppercase tracking-widest">Real-time Satellite Feed Coming Soon</p>
              </motion.div>
            )}

            {currentPage === 3 && (
              <motion.div
                key="zones"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
                className="w-full max-w-7xl mx-auto"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                  {OCEAN_ZONES.map((zone, idx) => (
                    <ZoneCard key={zone.id} zone={zone} idx={idx} />
                  ))}
                </div>
              </motion.div>
            )}

            {currentPage >= 4 && currentPage <= 6 && (
              <motion.div
                key="species"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
                className="w-full max-w-[90rem] mx-auto flex flex-col h-full"
              >
                <div className="text-center mb-6">
                  <p className="text-white/40 text-[0.6rem] lg:text-[0.7rem] uppercase tracking-[0.3em] font-black whitespace-nowrap">
                    All species loaded dynamically from our marine database. Click any card to track on the live map.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 px-4 mb-8">
                  {SPECIES.slice((currentPage - 4) * 4, (currentPage - 4) * 4 + 4).map((species, idx) => (
                    <SpeciesCard key={species.name} species={species} idx={idx} />
                  ))}
                </div>

                <div className="flex justify-center items-center gap-8 mt-auto pb-4">
                  <button 
                    title="Previous Page"
                    onClick={prevPage}
                    className="text-white/60 hover:text-cyan-400 transition-all hover:scale-125 active:scale-95"
                  >
                    <ChevronRight className="w-5 h-5 rotate-180" />
                  </button>
                  <div className="flex gap-3">
                    <div className={`w-12 h-[3px] transition-all duration-500 rounded-full ${currentPage === 4 ? 'bg-cyan-400 shadow-[0_0_12px_#22d3ee]' : 'bg-white/10'}`} />
                    <div className={`w-12 h-[3px] transition-all duration-500 rounded-full ${currentPage === 5 ? 'bg-cyan-400 shadow-[0_0_12px_#22d3ee]' : 'bg-white/10'}`} />
                    <div className={`w-12 h-[3px] transition-all duration-500 rounded-full ${currentPage === 6 ? 'bg-cyan-400 shadow-[0_0_12px_#22d3ee]' : 'bg-white/10'}`} />
                  </div>
                  <button 
                    title="Next Page"
                    onClick={nextPage}
                    className="text-white/60 hover:text-cyan-400 transition-all hover:scale-125 active:scale-95"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            )}

            {currentPage === 7 && (
              <motion.div
                key="ngo"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
                className="w-full max-w-[90rem] mx-auto flex flex-col h-full"
              >
                <div className="text-center mb-6">
                  <span className="text-[0.6rem] font-black tracking-[0.4em] text-cyan-400 uppercase mb-2 block">Our Conservation Network</span>
                  <p className="text-white/40 text-[0.6rem] lg:text-[0.7rem] uppercase tracking-[0.3em] font-black whitespace-nowrap">
                    Collaborating with India's leading marine organizations to protect our blue frontiers.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 px-4 mb-4 flex-1 items-center">
                  {NGO_PARTNERS.map((ngo, idx) => (
                    <NGOCard key={ngo.name} ngo={ngo} idx={idx} />
                  ))}
                </div>
              </motion.div>
            )}
            
            {currentPage === 8 && (
              <motion.div
                key="join"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
                className="grid grid-cols-1 lg:grid-cols-12 gap-12 w-full max-w-7xl mx-auto items-center"
              >
                <div className="lg:col-span-7 flex flex-col justify-center">
                  <span className="text-[0.6rem] font-black tracking-[0.4em] text-cyan-400 uppercase mb-4 block">Join the Network</span>
                  <h2 className="text-4xl lg:text-6xl font-black text-white tracking-tight uppercase leading-[0.9] mb-8">
                    Get Ocean Alerts <br /> Before <br /> Disaster Strikes.
                  </h2>
                  
                  <p className="text-white/60 text-sm lg:text-base leading-relaxed max-w-lg mb-12">
                    Join a network of marine scientists, NGOs, and citizen responders dedicated to immediate ocean intervention. Choose your mission profile.
                  </p>

                  <div className="flex gap-6">
                    <div className="bg-[#02182b]/40 backdrop-blur-md border border-white/5 p-6 rounded-2xl flex-1">
                      <div className="text-2xl font-black text-white mb-1">2,400+</div>
                      <div className="text-[0.55rem] font-black text-white/40 uppercase tracking-widest">Network Members</div>
                    </div>
                    <div className="bg-[#02182b]/40 backdrop-blur-md border border-white/5 p-6 rounded-2xl flex-1">
                      <div className="text-2xl font-black text-white mb-1">340</div>
                      <div className="text-[0.55rem] font-black text-white/40 uppercase tracking-widest">Alerts Sent</div>
                    </div>
                    <div className="bg-[#02182b]/40 backdrop-blur-md border border-white/5 p-6 rounded-2xl flex-1">
                      <div className="text-2xl font-black text-white mb-1 text-orange-400">98%</div>
                      <div className="text-[0.55rem] font-black text-white/40 uppercase tracking-widest">Response Rate</div>
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-5">
                  <div className="bg-[#02182b]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
                    <div className="flex gap-8 mb-10 border-b border-white/5">
                      <button className="pb-4 text-[0.65rem] font-black tracking-widest uppercase text-white border-b-2 border-cyan-400">As NGO Partner</button>
                      <button className="pb-4 text-[0.65rem] font-black tracking-widest uppercase text-white/40 hover:text-white transition-colors">As Citizen Scientist</button>
                    </div>

                    <div className="space-y-6">
                      <div className="space-y-2">
                        <label className="text-[0.55rem] font-black text-white/40 uppercase tracking-widest ml-1">Full Name</label>
                        <input 
                          type="text" 
                          placeholder="Dr. Sarah K." 
                          className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-400/50 transition-colors"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-[0.55rem] font-black text-white/40 uppercase tracking-widest ml-1">Professional Email</label>
                        <input 
                          type="email" 
                          placeholder="sarah@ocean-research.org" 
                          className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-400/50 transition-colors"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-[0.55rem] font-black text-white/40 uppercase tracking-widest ml-1">Organization</label>
                        <input 
                          type="text" 
                          placeholder="Marine Research Institute" 
                          className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 text-white placeholder:text-white/20 focus:outline-none focus:border-cyan-400/50 transition-colors"
                        />
                      </div>
                      
                      <button className="w-full mt-4 py-4 bg-cyan-400 text-[#02182b] font-black uppercase tracking-[0.2em] text-xs rounded-xl hover:bg-cyan-300 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_0_30px_rgba(34,211,238,0.3)]">
                        Request Mission Credentials
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {currentPage <= 1 && (
            <motion.footer 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.1 }}
              className="flex justify-center items-center w-full shrink-0 pb-4"
            >
              <div className="flex items-center gap-8 bg-[#02182b]/40 backdrop-blur-md px-8 py-3 rounded-2xl border border-white/5 shadow-2xl">
                <button 
                  title="Previous Slide"
                  onClick={prevPage}
                  className="text-white hover:text-cyan-400 transition-all hover:scale-125 active:scale-95"
                >
                  <ChevronRight className="w-6 h-6 rotate-180" />
                </button>
                <div className="flex gap-3">
                  <div className={`w-10 h-[2px] transition-all duration-500 ${currentPage === 0 ? 'bg-cyan-400 shadow-[0_0_12px_#22d3ee] w-12' : 'bg-white/20'}`} />
                  <div className={`w-10 h-[2px] transition-all duration-500 ${currentPage === 1 ? 'bg-cyan-400 shadow-[0_0_12px_#22d3ee] w-12' : 'bg-white/20'}`} />
                </div>
                <button 
                  title="Next Slide"
                  onClick={nextPage}
                  className="text-white hover:text-cyan-400 transition-all hover:scale-125 active:scale-95"
                >
                  <ChevronRight className="w-6 h-6" />
                </button>
              </div>
            </motion.footer>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
