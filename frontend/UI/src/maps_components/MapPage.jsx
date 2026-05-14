import { MapContainer, TileLayer, Marker, Tooltip, useMapEvents } from 'react-leaflet'
import { useState, useMemo, useCallback, useEffect } from 'react'
import { divIcon } from 'leaflet'

import 'leaflet/dist/leaflet.css'
import ZonePanel from './ZonePanel'
import DriftTracker from './DriftTracker'
import { DRIFT_SPECIES } from './data/driftData'

// ─── Zone definitions ────────────────────────────────────────────────────────
const ZONES = [
    { id: 'arabian_sea',   name: 'Arabian Sea',    color: '#22c55e', center: [16, 72], bounds: [[10, 68], [23, 77]] },
    { id: 'bay_of_bengal', name: 'Bay of Bengal',  color: '#facc15', center: [15, 85], bounds: [[10, 80], [20, 90]] },
    { id: 'lakshadweep',   name: 'Lakshadweep Sea',color: '#a855f7', center: [10, 73], bounds: [[8, 72],  [12, 74]] },
    { id: 'andaman_sea',   name: 'Andaman Sea',    color: '#ef4444', center: [12, 95], bounds: [[10, 92], [14, 98]] }
]

// ── Helper: normalise backend zone response → ZonePanel shape ─────────────────
function normaliseZoneData(raw, zone) {
    if (!raw) return null

    // Backend /api/zone/{id} returns:
    // { zone_id, zone_name, conditions, overall_stress, stress_score, species_risks, timestamp }
    const conds = raw.conditions || {}
    const stressScore  = raw.stress_score  ?? 50
    const overallStr   = (raw.overall_stress || 'MODERATE').toUpperCase()

    // Derive stress color from score
    let stressColor = '#22c55e'
    if (stressScore > 70)      stressColor = '#ef4444'
    else if (stressScore > 40) stressColor = '#facc15'

    // Build species_at_risk from backend species_risks list
    const speciesAtRisk = (raw.species_risks || []).slice(0, 4).map((s) => ({
        name: s.species,
        risk: s.risk_level?.toLowerCase() || 'moderate',
        note: (s.top_factors || []).join(' · ') || 'Monitoring required.',
        ngo:  'WatchTheBlue Network'
    }))

    // Coral bleaching alert: triggered if DHW present or stress > 70
    const bleachingAlert = stressScore > 70 || (conds.sst_celsius && conds.sst_celsius > 30)

    return {
        // ZonePanel-expected fields
        zone:                 zone.id,
        zone_name:            raw.zone_name || zone.name,
        conditions: {
            temperature:        conds.temperature  ?? conds.sst_celsius ?? 28,
            temperature_anomaly: conds.sst_celsius
                ? Number((conds.sst_celsius - 28).toFixed(2))
                : (conds.current_speed ?? 0),
            salinity:           conds.salinity     ?? 34.5,
            oxygen:             conds.oxygen       ?? 5.0,
            ph:                 conds.ph           ?? 8.1,
            current_speed:      conds.current_speed ?? 0.3,
        },
        stress_score:         stressScore,
        stress_level:         overallStr.charAt(0) + overallStr.slice(1).toLowerCase(),
        stress_color:         stressColor,
        coral_bleaching_alert: bleachingAlert,
        species_at_risk:      speciesAtRisk,
        timestamp:            raw.timestamp || new Date().toISOString(),
        data_source:          conds.source || 'CMEMS + NOAA',
        // Pass raw through for full access in panel
        _raw: raw
    }
}

// ── Fallback static data per zone (when backend is down) ─────────────────────
const FALLBACK = {
    arabian_sea: {
        zone: 'arabian_sea', zone_name: 'Arabian Sea',
        conditions: { temperature: 28.1, temperature_anomaly: 0.7, salinity: 36.0, oxygen: 4.8, ph: 8.11, current_speed: 0.28 },
        stress_score: 35, stress_level: 'Moderate', stress_color: '#facc15',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Indian Ocean Humpback Dolphin', risk: 'moderate', ngo: 'Terra Conscious', note: 'Entanglement risk increasing in coastal shipping lanes.' },
            { name: 'Green Sea Turtle', risk: 'moderate', ngo: 'Wildlife Trust of India', note: 'Nesting beaches under pressure from light pollution.' }
        ],
        timestamp: new Date().toISOString(), data_source: 'Simulated (backend offline)'
    },
    bay_of_bengal: {
        zone: 'bay_of_bengal', zone_name: 'Bay of Bengal',
        conditions: { temperature: 29.8, temperature_anomaly: 1.6, salinity: 33.5, oxygen: 3.9, ph: 8.02, current_speed: 0.35 },
        stress_score: 67, stress_level: 'High', stress_color: '#a855f7',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Olive Ridley Sea Turtle', risk: 'high', ngo: 'TREE Foundation', note: 'Mass strandings documented on Odisha coast.' },
            { name: 'Irrawaddy Dolphin', risk: 'high', ngo: 'WWF India', note: 'Delta habitat fragmentation impacting breeding zones.' }
        ],
        timestamp: new Date().toISOString(), data_source: 'Simulated (backend offline)'
    },
    lakshadweep: {
        zone: 'lakshadweep', zone_name: 'Lakshadweep Sea',
        conditions: { temperature: 31.2, temperature_anomaly: 2.3, salinity: 34.2, oxygen: 3.5, ph: 7.94, current_speed: 0.18 },
        stress_score: 82, stress_level: 'Critical', stress_color: '#ef4444',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Hawksbill Turtle', risk: 'critical', ngo: 'Dakshin Foundation', note: 'Reef bleaching reducing foraging habitat quality.' },
            { name: 'Spinner Dolphin', risk: 'high', ngo: 'Coastal Impact', note: 'Tourism vessel traffic disrupting resting lagoons.' }
        ],
        timestamp: new Date().toISOString(), data_source: 'Simulated (backend offline)'
    },
    andaman_sea: {
        zone: 'andaman_sea', zone_name: 'Andaman Sea',
        conditions: { temperature: 27.4, temperature_anomaly: 0.3, salinity: 33.8, oxygen: 5.2, ph: 8.16, current_speed: 0.22 },
        stress_score: 28, stress_level: 'Healthy', stress_color: '#22c55e',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Dugong', risk: 'moderate', ngo: 'ReefWatch Marine Conservation', note: 'Seagrass meadows are stable but monitored for decline.' },
            { name: 'Andaman Clownfish', risk: 'low', ngo: 'ANET', note: 'Localized reef stress near high-diving routes.' }
        ],
        timestamp: new Date().toISOString(), data_source: 'Simulated (backend offline)'
    }
}

function zoneForPoint(lat, lon) {
    const matched = ZONES.find(z => {
        const [[s, w], [n, e]] = z.bounds
        return lat >= s && lat <= n && lon >= w && lon <= e
    })
    if (matched) return matched
    return ZONES.reduce((near, z) => {
        const d1 = (lat - z.center[0]) ** 2 + (lon - z.center[1]) ** 2
        const d2 = (lat - near.center[0]) ** 2 + (lon - near.center[1]) ** 2
        return d1 < d2 ? z : near
    }, ZONES[0])
}

function MapClickHandler({ onZoneSelect }) {
    useMapEvents({ click(e) { onZoneSelect(zoneForPoint(e.latlng.lat, e.latlng.lng)) } })
    return null
}

const LEGEND = [
    { color: '#22c55e', label: 'Healthy' },
    { color: '#facc15', label: 'Moderate' },
    { color: '#a855f7', label: 'High' },
    { color: '#ef4444', label: 'Critical' },
]

// ── Zone dot colors from live overview data ───────────────────────────────────
function useZoneColors() {
    const [colors, setColors] = useState({})

    useEffect(() => {
        fetch('http://localhost:8000/api/overview')
            .then(r => r.json())
            .then(data => {
                const map = {}
                ;(data.zones || []).forEach(z => {
                    let c = '#22c55e'
                    if (z.stress_score > 70)      c = '#ef4444'
                    else if (z.stress_score > 40) c = '#facc15'
                    map[z.zone_id] = c
                })
                setColors(map)
            })
            .catch(() => {}) // silent fail – keep default colors
    }, [])

    return colors
}

// ─── Drift species selector pill list ────────────────────────────────────────
function DriftSpeciesBar({ selected, onSelect }) {
    return (
        <div className="drift-species-bar">
            <span className="drift-bar-label">DRIFT TRACKER</span>
            {DRIFT_SPECIES.map(s => (
                <button
                    key={s.id}
                    className={`drift-pill${selected === s.id ? ' drift-pill-active' : ''}`}
                    style={{ '--pill-color': s.color, '--pill-glow': s.glowColor }}
                    onClick={() => onSelect(prev => prev === s.id ? null : s.id)}
                    title={s.note}
                >
                    <span className="drift-pill-dot" />
                    {s.icon} {s.name}
                </button>
            ))}
        </div>
    )
}

// ─── Drift info card (bottom-left) ───────────────────────────────────────────
function DriftInfoCard({ speciesId }) {
    const species = DRIFT_SPECIES.find(s => s.id === speciesId)
    if (!species) return null
    return (
        <div className="drift-info-card" style={{ '--card-color': species.color, '--card-glow': species.glowColor }}>
            <div className="dic-header">
                <span className="dic-icon">{species.icon}</span>
                <div>
                    <p className="dic-name">{species.name}</p>
                    <p className="dic-status">{species.status}</p>
                </div>
                <span className={`dic-risk dic-risk-${species.risk}`}>{species.risk.toUpperCase()}</span>
            </div>
            <p className="dic-note">{species.note}</p>
            <div className="dic-coords">
                <span>📍 Stranding: {species.strandingLat}°N, {species.strandingLon}°E</span>
                <span>⏱ {species.hours}h backward drift simulation</span>
            </div>
        </div>
    )
}

// ─── Main MapPage ─────────────────────────────────────────────────────────────
export default function MapPage({ onBack }) {
    const [selectedData, setSelectedData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [selectedSpeciesId, setSelectedSpeciesId] = useState(null)
    const [backendOnline, setBackendOnline] = useState(true)

    const liveColors = useZoneColors()

    // Merge live colors into zone icons
    const zoneIcons = useMemo(() =>
        ZONES.reduce((acc, zone) => {
            const color = liveColors[zone.id] || zone.color
            acc[zone.id] = divIcon({
                className: 'zone-dot-icon-wrapper',
                html: `<div class="zone-dot-hitbox">
                         <div class="zone-dot" style="--zone-color:${color};"></div>
                       </div>`,
                iconSize: [40, 40],
                iconAnchor: [20, 20]
            })
            return acc
        }, {}),
    [liveColors])

    const fetchZoneData = useCallback(async (zone) => {
        setLoading(true)
        setSelectedSpeciesId(null)
        try {
            // Use the correct endpoint: /api/zone/{zone_id}
            const res = await fetch(`http://localhost:8000/api/zone/${zone.id}`)
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const raw = await res.json()
            setBackendOnline(true)

            // Normalise to ZonePanel shape
            const normalised = normaliseZoneData(raw, zone)
            setSelectedData(normalised)
        } catch (err) {
            console.warn('Backend unavailable, using fallback:', err.message)
            setBackendOnline(false)
            setSelectedData(FALLBACK[zone.id] || FALLBACK.arabian_sea)
        } finally {
            setLoading(false)
        }
    }, [])

    return (
        <div className="map-page-root">
            {/* ── Top bar ── */}
            <header className="map-topbar">
                <button className="map-back-btn" onClick={onBack} aria-label="Back">
                    <span className="map-back-arrow">←</span>
                    <span>Dashboard</span>
                </button>

                <div className="map-topbar-center">
                    <span className={`map-live-dot${backendOnline ? '' : ' offline'}`} />
                    <span className="map-live-label">{backendOnline ? 'LIVE FEED' : 'OFFLINE MODE'}</span>
                    <span className="map-topbar-coords">08°12′26″N &nbsp; 76°15′32″E</span>
                </div>

                <div className="map-topbar-right">
                    {LEGEND.map(item => (
                        <div key={item.label} className="map-legend-item">
                            <span className="map-legend-dot" style={{ background: item.color }} />
                            <span>{item.label}</span>
                        </div>
                    ))}
                </div>
            </header>

            {/* ── Drift species selector bar ── */}
            <DriftSpeciesBar selected={selectedSpeciesId} onSelect={setSelectedSpeciesId} />

            {/* ── Map + panel ── */}
            <div className="map-body">
                <div className="map-container-wrap">
                    <MapContainer
                        center={[13, 80]}
                        zoom={5}
                        style={{ height: '100%', width: '100%' }}
                        zoomControl={false}
                        preferCanvas={true}
                        updateWhenZooming={false}
                        updateWhenIdle={true}
                    >
                        <TileLayer
                            url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
                            attribution="Esri Ocean Basemap"
                            keepBuffer={4}
                        />
                        <TileLayer
                            url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png"
                            attribution="Carto"
                            keepBuffer={4}
                        />

                        {/* Zone markers — colored from live overview data */}
                        {ZONES.map(zone => (
                            <Marker
                                key={zone.id}
                                position={zone.center}
                                icon={zoneIcons[zone.id]}
                                eventHandlers={{ click: () => fetchZoneData(zone) }}
                            >
                                <Tooltip permanent direction="top" offset={[0, -12]} className="classic-zone-label" interactive={true}>
                                    <div 
                                        className="classic-zone-label-text" 
                                        style={{ cursor: 'pointer' }}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            fetchZoneData(zone);
                                        }}
                                    >
                                        {zone.name}
                                    </div>
                                </Tooltip>
                            </Marker>
                        ))}

                        {/* Drift tracker overlay */}
                        <DriftTracker
                            selectedSpeciesId={selectedSpeciesId}
                            onSelectSpecies={setSelectedSpeciesId}
                        />

                        <MapClickHandler onZoneSelect={fetchZoneData} />
                    </MapContainer>

                    {/* Drift info card over map bottom-left */}
                    <DriftInfoCard speciesId={selectedSpeciesId} />
                </div>

                {/* Zone detail panel */}
                <div className={`map-side-panel-wrap${selectedData ? ' map-side-panel-open' : ''}`}>
                    {selectedData && (
                        <ZonePanel
                            data={selectedData}
                            loading={loading}
                            onClose={() => setSelectedData(null)}
                        />
                    )}
                </div>
            </div>
        </div>
    )
}
