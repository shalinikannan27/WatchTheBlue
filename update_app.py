import os

filepath = 'frontend/UI/src/App.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
imports = """import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { getAllZones, getSpeciesRisk, getDriftPath } from './api/oceanApi';
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
  FileText,
  Search
} from 'lucide-react';

// Fix leaflet icon paths
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});"""

old_imports = """import { useState } from 'react';
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
} from 'lucide-react';"""
content = content.replace(old_imports, imports)

# 2. Update SpeciesCard
old_species_card = """function SpeciesCard({ species, idx }: any) {
  return (
    <motion.div"""

new_species_card = """function SpeciesCard({ species, idx }: any) {
  const [riskData, setRiskData] = useState<any>(null);

  useEffect(() => {
    getSpeciesRisk(species.name).then((data) => {
      const highestZone = data.zones.reduce((prev: any, current: any) => 
        (prev.risk_probability > current.risk_probability) ? prev : current
      );
      setRiskData(highestZone);
    }).catch(console.error);
  }, [species.name]);

  const threatVal = riskData ? Math.round(riskData.risk_probability * 100) : species.threat;
  const isHighRisk = threatVal > 70;

  return (
    <motion.div"""

content = content.replace(old_species_card, new_species_card)

# 3. Update species.threat references in SpeciesCard
content = content.replace("""<span className={`text-xs font-black ${species.threat > 70 ? 'text-red-400' : 'text-cyan-400'}`}>{species.threat}%</span>""", """<span className={`text-xs font-black ${isHighRisk ? 'text-red-400' : 'text-cyan-400'}`}>{threatVal}%</span>""")
content = content.replace("""className={`h-full rounded-full ${species.threat > 70 ? 'bg-red-400' : 'bg-cyan-400 shadow-[0_0_8px_#06b6d4]'}`}""", """className={`h-full rounded-full ${isHighRisk ? 'bg-red-400' : 'bg-cyan-400 shadow-[0_0_8px_#06b6d4]'}`}""")
content = content.replace("""animate={{ width: `${species.threat}%` }}""", """animate={{ width: `${threatVal}%` }}""")

# 4. App state
old_app_state = """function App() {

  const [activeCard, setActiveCard] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0); 
  const [hoveredStep, setHoveredStep] = useState<string | null>(null);

  const bgImage = "/c1b3e851af2b6979c4770070f5e2f779.jpg";"""

new_app_state = """function App() {

  const [activeCard, setActiveCard] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0); 
  const [hoveredStep, setHoveredStep] = useState<string | null>(null);
  const [liveZones, setLiveZones] = useState<any[]>([]);

  // Drift simulation state
  const [driftLat, setDriftLat] = useState('16.0');
  const [driftLon, setDriftLon] = useState('72.0');
  const [driftDate, setDriftDate] = useState('2026-05-12');
  const [driftPath, setDriftPath] = useState<any[]>([]);
  const [driftLoading, setDriftLoading] = useState(false);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const data = await getAllZones();
        setLiveZones(data.zones);
      } catch (err) {
        console.error("Failed to fetch zones", err);
      }
    };
    fetchZones();
    const interval = setInterval(fetchZones, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleDriftSubmit = async (e: any) => {
    e.preventDefault();
    setDriftLoading(true);
    try {
      const data = await getDriftPath(driftLat, driftLon, driftDate);
      setDriftPath(data.drift_path);
    } catch (err) {
      console.error(err);
    } finally {
      setDriftLoading(false);
    }
  };

  const bgImage = "/c1b3e851af2b6979c4770070f5e2f779.jpg";"""

content = content.replace(old_app_state, new_app_state)

# 5. Live Monitor replacement
old_monitor = """            {currentPage === 2 && (
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
            )}"""

new_monitor = """            {currentPage === 2 && (
              <motion.div
                key="coming-soon"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-7xl mx-auto h-[70vh]"
              >
                {/* Live Zone Summary Table */}
                <div className="bg-[#02182b]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl flex flex-col h-full overflow-hidden">
                  <div className="flex items-center gap-3 mb-6">
                    <Activity className="w-6 h-6 text-cyan-400 animate-pulse" />
                    <h2 className="text-xl font-black uppercase tracking-widest text-white">Live Monitor Summary</h2>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto pr-2">
                    {liveZones.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-white/50 text-sm">
                        <Radio className="w-8 h-8 mb-3 animate-spin text-cyan-400" />
                        Fetching Live Ocean Conditions...
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {liveZones.map((z, idx) => (
                          <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col gap-2 relative overflow-hidden group hover:border-cyan-400/30 transition-all">
                            <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: z.stress_score > 70 ? '#f87171' : z.stress_score > 40 ? '#fbbf24' : '#34d399' }} />
                            <div className="flex justify-between items-center pl-2">
                              <h3 className="font-bold text-white text-lg tracking-wide">{z.zone_name}</h3>
                              <span className={`text-xs font-black px-2 py-1 rounded border uppercase tracking-wider ${
                                z.stress_score > 70 ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                z.stress_score > 40 ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                                'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              }`}>Stress: {z.overall_stress} ({z.stress_score}%)</span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 mt-2 pl-2 text-xs text-white/70">
                              <div><span className="text-white/40 uppercase text-[0.6rem]">Temp</span><br/>{z.conditions.temperature.toFixed(1)}°C</div>
                              <div><span className="text-white/40 uppercase text-[0.6rem]">Salinity</span><br/>{z.conditions.salinity.toFixed(1)} PSU</div>
                              <div><span className="text-white/40 uppercase text-[0.6rem]">O₂</span><br/>{z.conditions.oxygen.toFixed(1)} mg/L</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Drift Simulator Map */}
                <div className="bg-[#02182b]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl flex flex-col h-full">
                  <div className="flex items-center gap-3 mb-6">
                    <History className="w-6 h-6 text-cyan-400" />
                    <h2 className="text-xl font-black uppercase tracking-widest text-white">Backward Drift Simulation</h2>
                  </div>
                  
                  <form onSubmit={handleDriftSubmit} className="grid grid-cols-3 gap-3 mb-4">
                    <input 
                      type="number" step="0.0001" value={driftLat} onChange={(e) => setDriftLat(e.target.value)}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/30 focus:border-cyan-400/50 outline-none"
                      placeholder="Lat" required
                    />
                    <input 
                      type="number" step="0.0001" value={driftLon} onChange={(e) => setDriftLon(e.target.value)}
                      className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/30 focus:border-cyan-400/50 outline-none"
                      placeholder="Lon" required
                    />
                    <div className="flex gap-2">
                      <input 
                        type="date" value={driftDate} onChange={(e) => setDriftDate(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-cyan-400/50 outline-none"
                        required
                        style={{colorScheme: 'dark'}}
                      />
                      <button 
                        type="submit" 
                        disabled={driftLoading}
                        className="bg-cyan-400 hover:bg-cyan-300 text-[#02182b] p-2 rounded-lg transition-colors flex items-center justify-center shrink-0 disabled:opacity-50"
                      >
                        {driftLoading ? <Radio className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                      </button>
                    </div>
                  </form>
                  
                  <div className="flex-1 rounded-xl overflow-hidden border border-white/10 relative z-0">
                    <MapContainer center={[16, 72]} zoom={4} style={{ height: '100%', width: '100%', zIndex: 0 }}>
                      <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; CARTO'
                      />
                      {driftPath.length > 0 && (
                        <>
                          <Marker position={[driftPath[0].lat, driftPath[0].lon]}>
                            <Popup>Stranding Point</Popup>
                          </Marker>
                          <Polyline 
                            positions={driftPath.map((p: any) => [p.lat, p.lon])} 
                            color="#22d3ee" 
                            weight={3} 
                            dashArray="5, 10" 
                          />
                          <Marker position={[driftPath[driftPath.length-1].lat, driftPath[driftPath.length-1].lon]}>
                            <Popup>Estimated Origin</Popup>
                          </Marker>
                        </>
                      )}
                    </MapContainer>
                  </div>
                </div>
              </motion.div>
            )}"""

content = content.replace(old_monitor, new_monitor)

# 6. Ocean Zones Page Integration
old_ocean_zones = """                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                  {OCEAN_ZONES.map((zone, idx) => (
                    <ZoneCard key={zone.id} zone={zone} idx={idx} />
                  ))}
                </div>"""

new_ocean_zones = """                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                  {OCEAN_ZONES.map((zone, idx) => {
                    let stressStr = zone.stress;
                    let color = zone.stressColor;
                    let dotCol = zone.dotColor;

                    if (liveZones.length > 0) {
                      const live = liveZones.find((z) => z.zone_name === zone.name || z.zone_name.includes(zone.name.split(' ')[0]));
                      if (live) {
                        stressStr = live.overall_stress;
                        if (live.stress_score > 70) {
                          color = 'text-red-400';
                          dotCol = 'bg-red-400';
                        } else if (live.stress_score > 40) {
                          color = 'text-yellow-400';
                          dotCol = 'bg-yellow-400';
                        } else {
                          color = 'text-emerald-400';
                          dotCol = 'bg-emerald-400';
                        }
                      }
                    }

                    return (
                      <ZoneCard key={zone.id} zone={{...zone, stress: stressStr, stressColor: color, dotColor: dotCol}} idx={idx} />
                    );
                  })}
                </div>"""

content = content.replace(old_ocean_zones, new_ocean_zones)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated App.tsx successfully.")
