import { MapContainer, TileLayer, Marker, Tooltip, useMapEvents } from 'react-leaflet'
import { useState, useMemo, useCallback } from 'react'
import { divIcon } from 'leaflet'
import { useNavigate } from 'react-router-dom'
import 'leaflet/dist/leaflet.css'
import ZonePanel from './ZonePanel'
import DriftTracker from './DriftTracker'
import { DRIFT_SPECIES } from '../data/driftData'

// ─── Zone definitions ────────────────────────────────────────────────────────
const ZONES = [
    { id: 'arabian_sea',   name: 'Arabian Sea',    color: '#22c55e', center: [16, 72], bounds: [[10, 68], [23, 77]] },
    { id: 'bay_of_bengal', name: 'Bay of Bengal',  color: '#facc15', center: [15, 85], bounds: [[10, 80], [20, 90]] },
    { id: 'lakshadweep',   name: 'Lakshadweep Sea',color: '#a855f7', center: [10, 73], bounds: [[8, 72],  [12, 74]] },
    { id: 'andaman_sea',   name: 'Andaman Sea',    color: '#ef4444', center: [12, 95], bounds: [[10, 92], [14, 98]] }
]

const SAMPLE_ZONE_DATA = {
    arabian_sea: {
        zone: 'arabian_sea',
        conditions: { temperature: 28.1, temperature_anomaly: 0.7, oxygen: 4.8, ph: 8.11 },
        stress_score: 35, stress_level: 'moderate', stress_color: '#facc15',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Indian Ocean Humpback Dolphin', risk: 'moderate', ngo: 'Terra Conscious', note: 'Entanglement risk increasing in coastal shipping lanes.' },
            { name: 'Green Sea Turtle', risk: 'moderate', ngo: 'Wildlife Trust of India', note: 'Nesting beaches under pressure from light pollution.' }
        ]
    },
    bay_of_bengal: {
        zone: 'bay_of_bengal',
        conditions: { temperature: 29.8, temperature_anomaly: 1.6, oxygen: 3.9, ph: 8.02 },
        stress_score: 67, stress_level: 'high', stress_color: '#a855f7',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Olive Ridley Sea Turtle', risk: 'high', ngo: 'TREE Foundation', note: 'Mass strandings documented on Odisha coast.' },
            { name: 'Irrawaddy Dolphin', risk: 'high', ngo: 'WWF India', note: 'Delta habitat fragmentation impacting breeding zones.' }
        ]
    },
    lakshadweep: {
        zone: 'lakshadweep',
        conditions: { temperature: 31.2, temperature_anomaly: 2.3, oxygen: 3.5, ph: 7.94 },
        stress_score: 82, stress_level: 'critical', stress_color: '#ef4444',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Hawksbill Turtle', risk: 'critical', ngo: 'Dakshin Foundation', note: 'Reef bleaching reducing foraging habitat quality.' },
            { name: 'Spinner Dolphin', risk: 'high', ngo: 'Coastal Impact', note: 'Tourism vessel traffic disrupting resting lagoons.' }
        ]
    },
    andaman_sea: {
        zone: 'andaman_sea',
        conditions: { temperature: 27.4, temperature_anomaly: 0.3, oxygen: 5.2, ph: 8.16 },
        stress_score: 28, stress_level: 'healthy', stress_color: '#22c55e',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Dugong', risk: 'moderate', ngo: 'ReefWatch Marine Conservation', note: 'Seagrass meadows are stable but monitored for decline.' },
            { name: 'Andaman Clownfish', risk: 'low', ngo: 'ANET', note: 'Localized reef stress near high-diving routes.' }
        ]
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
export default function MapPage() {
    const [selectedData, setSelectedData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [selectedSpeciesId, setSelectedSpeciesId] = useState(null)
    const navigate = useNavigate()

    const zoneIcons = useMemo(() =>
        ZONES.reduce((acc, zone) => {
            acc[zone.id] = divIcon({
                className: 'zone-dot-icon-wrapper',
                html: `<div class="zone-dot" style="--zone-color:${zone.color};"></div>`,
                iconSize: [10, 10],
                iconAnchor: [5, 5]
            })
            return acc
        }, {}),
    [])

    const fetchZoneData = useCallback(async (zone) => {
        const [lat, lon] = zone.center
        setLoading(true)
        setSelectedSpeciesId(null) // clear drift when zone selected
        try {
            const res = await fetch(`http://localhost:8000/api/zone?lat=${lat}&lon=${lon}`)
            const data = await res.json()
            setSelectedData(data?.zone ? data : { ...SAMPLE_ZONE_DATA[zone.id] })
        } catch {
            setSelectedData({ ...SAMPLE_ZONE_DATA[zone.id] })
        } finally {
            setLoading(false)
        }
    }, [])

    return (
        <div className="map-page-root">
            {/* ── Top bar ── */}
            <header className="map-topbar">
                <button className="map-back-btn" onClick={() => navigate('/')} aria-label="Back">
                    <span className="map-back-arrow">←</span>
                    <span>Dashboard</span>
                </button>

                <div className="map-topbar-center">
                    <span className="map-live-dot" />
                    <span className="map-live-label">LIVE FEED</span>
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

                        {/* Zone markers */}
                        {ZONES.map(zone => (
                            <Marker
                                key={zone.id}
                                position={zone.center}
                                icon={zoneIcons[zone.id]}
                                eventHandlers={{ click: () => fetchZoneData(zone) }}
                            >
                                <Tooltip permanent direction="top" offset={[0, -8]} className="classic-zone-label">
                                    <span className="classic-zone-label-text">{zone.name}</span>
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
