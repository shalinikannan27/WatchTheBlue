import { MapContainer, TileLayer, Marker, Tooltip, useMapEvents, Rectangle, CircleMarker } from 'react-leaflet'
import { useState, useMemo, useCallback, useEffect } from 'react'
import { divIcon } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import ZonePanel from './ZonePanel'
import DriftTracker from './DriftTracker'
import { DRIFT_SPECIES } from './data/driftData'
import { API_BASE_URL } from './config'
import './map.css'

const ZONES = [
    { id: 'arabian_sea',   name: 'Arabian Sea',    color: '#22c55e', center: [16, 72], bounds: [[10, 68], [23, 77]] },
    { id: 'bay_of_bengal', name: 'Bay of Bengal',  color: '#facc15', center: [15, 85], bounds: [[10, 80], [20, 90]] },
    { id: 'lakshadweep',   name: 'Lakshadweep Sea',color: '#facc15', center: [10, 73], bounds: [[8, 72],  [12, 74]] },
    { id: 'andaman_sea',   name: 'Andaman Sea',    color: '#22c55e', center: [12, 95], bounds: [[10, 92], [14, 98]] }
]

// Species and their zone assignments for map display
const SPECIES_ZONE_MAP = [
    { name: 'Olive Ridley Turtle', icon: '🐢', zone: 'bay_of_bengal', positions: [[15.2, 84.5], [14.8, 85.3], [16.1, 84.0], [13.5, 86.2]] },
    { name: 'Whale Shark', icon: '🦈', zone: 'arabian_sea', positions: [[18.0, 70.5], [16.5, 72.0], [20.0, 69.5], [17.2, 71.8]] },
    { name: 'Dugong', icon: '🌊', zone: 'andaman_sea', positions: [[12.5, 93.5], [11.8, 94.2], [13.0, 93.0]] },
    { name: 'Spinner Dolphin', icon: '🐬', zone: 'lakshadweep', positions: [[10.2, 73.1], [9.8, 72.8], [10.5, 73.4]] },
    { name: 'Humpback Whale', icon: '🐋', zone: 'arabian_sea', positions: [[14.5, 70.0], [15.8, 69.5]] },
    { name: 'Manta Ray', icon: '🦑', zone: 'lakshadweep', positions: [[10.0, 72.5], [9.5, 73.2]] },
    { name: 'Reef Shark', icon: '🦈', zone: 'andaman_sea', positions: [[12.0, 93.8], [11.5, 94.5]] },
    { name: 'Clownfish', icon: '🐠', zone: 'arabian_sea', positions: [[19.5, 71.0]] },
    { name: 'Blue Whale', icon: '🐳', zone: 'arabian_sea', positions: [[13.0, 68.5]] },
    { name: 'Green Sea Turtle', icon: '🐢', zone: 'lakshadweep', positions: [[10.3, 72.9], [9.9, 73.3]] },
]

const SAMPLE_ZONE_DATA = {
    arabian_sea: {
        zone: 'arabian_sea',
        zone_display: 'Arabian Sea',
        conditions: { temperature: 28.1, temperature_anomaly: 0.7, oxygen: 4.8, ph: 8.11 },
        stress_score: 35, stress_level: 'moderate', stress_color: '#facc15',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Indian Ocean Humpback Dolphin', risk: 'moderate', ngo: 'Terra Conscious', note: 'Entanglement risk increasing in coastal shipping lanes.' },
            { name: 'Green Sea Turtle', risk: 'moderate', ngo: 'Wildlife Trust of India', note: 'Nesting beaches under pressure from light pollution.' }
        ],
        ml_layer_summary: 'Offline sample: connect the backend for live NOAA/CMEMS fusion and .pkl inference.',
    },
    bay_of_bengal: {
        zone: 'bay_of_bengal',
        zone_display: 'Bay of Bengal',
        conditions: { temperature: 29.8, temperature_anomaly: 1.6, oxygen: 3.9, ph: 8.02 },
        stress_score: 67, stress_level: 'high', stress_color: '#ef4444',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Olive Ridley Sea Turtle', risk: 'high', ngo: 'TREE Foundation', note: 'Mass strandings documented on Odisha coast.' },
            { name: 'Irrawaddy Dolphin', risk: 'high', ngo: 'WWF India', note: 'Delta habitat fragmentation impacting breeding zones.' }
        ],
        ml_layer_summary: 'Offline sample: connect the backend for live NOAA/CMEMS fusion and .pkl inference.',
    },
    lakshadweep: {
        zone: 'lakshadweep',
        zone_display: 'Lakshadweep Sea',
        conditions: { temperature: 31.2, temperature_anomaly: 2.3, oxygen: 3.5, ph: 7.94 },
        stress_score: 82, stress_level: 'high', stress_color: '#ef4444',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Hawksbill Turtle', risk: 'high', ngo: 'Dakshin Foundation', note: 'Reef bleaching reducing foraging habitat quality.' },
            { name: 'Spinner Dolphin', risk: 'high', ngo: 'Coastal Impact', note: 'Tourism vessel traffic disrupting resting lagoons.' }
        ],
        ml_layer_summary: 'Offline sample: connect the backend for live NOAA/CMEMS fusion and .pkl inference.',
    },
    andaman_sea: {
        zone: 'andaman_sea',
        zone_display: 'Andaman Sea',
        conditions: { temperature: 27.4, temperature_anomaly: 0.3, oxygen: 5.2, ph: 8.16 },
        stress_score: 28, stress_level: 'low', stress_color: '#22c55e',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Dugong', risk: 'moderate', ngo: 'ReefWatch Marine Conservation', note: 'Seagrass meadows are stable but monitored for decline.' },
            { name: 'Andaman Clownfish', risk: 'low', ngo: 'ANET', note: 'Localized reef stress near high-diving routes.' }
        ],
        ml_layer_summary: 'Offline sample: connect the backend for live NOAA/CMEMS fusion and .pkl inference.',
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
    { color: '#22c55e', label: 'Low' },
    { color: '#facc15', label: 'Moderate' },
    { color: '#ef4444', label: 'High' },
]

const RISK_LEVEL_COLORS = {
    LOW: '#22c55e',
    MODERATE: '#facc15',
    HIGH: '#ef4444',
}

const RISK_FILL_OPACITY = {
    LOW: 0.1,
    MODERATE: 0.14,
    HIGH: 0.22,
}

function ZoneRiskOverlays({ zones, overlay }) {
    if (!overlay) return null
    return (
        <>
            {zones.map(zone => {
                const meta = overlay[zone.id]
                if (!meta) return null
                const lvl = meta.risk_level || 'LOW'
                const color = RISK_LEVEL_COLORS[lvl] || '#38bdf8'
                const [[south, west], [north, east]] = zone.bounds
                const pulse = lvl === 'HIGH' ? ' risk-zone-rect--pulse' : ''
                return (
                    <Rectangle
                        key={`risk-${zone.id}`}
                        bounds={[[south, west], [north, east]]}
                        pathOptions={{
                            color,
                            weight: 1.5,
                            opacity: 0.85,
                            fillColor: color,
                            fillOpacity: RISK_FILL_OPACITY[lvl] ?? 0.12,
                            className: `risk-zone-rect risk-zone-rect--${String(lvl).toLowerCase()}${pulse}`,
                        }}
                    />
                )
            })}
        </>
    )
}

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

function SpeciesTrackerBar({ selectedSpecies, onSelectSpecies }) {
    return (
        <div className="drift-species-bar species-tracker-bar">
            <span className="drift-bar-label" style={{ color: 'rgba(34, 197, 94, 0.55)' }}>SPECIES TRACKER</span>
            <select
                value={selectedSpecies || ''}
                onChange={e => onSelectSpecies(e.target.value || null)}
                className="species-tracker-dropdown"
            >
                <option value="">All Species</option>
                {SPECIES_ZONE_MAP.map(s => (
                    <option key={s.name} value={s.name}>{s.icon} {s.name}</option>
                ))}
            </select>
        </div>
    )
}

function SpeciesZoneMarkers({ selectedSpecies }) {
    const speciesToShow = selectedSpecies
        ? SPECIES_ZONE_MAP.filter(s => s.name === selectedSpecies)
        : SPECIES_ZONE_MAP

    return (
        <>
            {speciesToShow.map(species =>
                species.positions.map((pos, i) => (
                    <CircleMarker
                        key={`${species.name}-${i}`}
                        center={pos}
                        radius={6}
                        pathOptions={{
                            color: '#22c55e',
                            fillColor: '#22c55e',
                            fillOpacity: 0.7,
                            weight: 1.5,
                            opacity: 0.9,
                        }}
                    >
                        <Tooltip>
                            <div className="drift-tooltip">
                                <strong>{species.icon} {species.name}</strong>
                                <span>{pos[0].toFixed(2)}°N, {pos[1].toFixed(2)}°E</span>
                                <span className="drift-tooltip-status">Zone: {ZONES.find(z => z.id === species.zone)?.name || species.zone}</span>
                            </div>
                        </Tooltip>
                    </CircleMarker>
                ))
            )}
        </>
    )
}

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

export default function MapPage() {
    const [selectedData, setSelectedData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [selectedSpeciesId, setSelectedSpeciesId] = useState(null)
    const [selectedTrackerSpecies, setSelectedTrackerSpecies] = useState(null)
    const [zonesRiskOverlay, setZonesRiskOverlay] = useState(null)
    const [predictionError, setPredictionError] = useState(false)
    const [predictionService, setPredictionService] = useState({ status: 'checking', message: 'Checking prediction service…' })

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
        setPredictionError(false)
        try {
            const res = await fetch(`${API_BASE_URL}/api/zone-analysis?lat=${lat}&lon=${lon}`)
            if (!res.ok) throw new Error(`zone-analysis ${res.status}`)
            const data = await res.json()
            if (data.zones_risk_overlay) setZonesRiskOverlay(data.zones_risk_overlay)
            if (data.zone && data.conditions) {
                setSelectedData(data)
            } else {
                setSelectedData({ ...SAMPLE_ZONE_DATA[zone.id], prediction: null })
                setPredictionError(true)
            }
        } catch (err) {
            console.error('[WatchTheBlue] zone-analysis failed, using sample data:', err)
            setSelectedData({ ...SAMPLE_ZONE_DATA[zone.id], prediction: null })
            setPredictionError(true)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        let cancelled = false
        ;(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/health/prediction`)
                if (!res.ok) throw new Error(`prediction health ${res.status}`)
                const data = await res.json()
                if (!cancelled) {
                    setPredictionService(data.status === 'online' ? { status: 'online', message: 'Prediction online' } : { status: 'offline', message: 'Prediction offline' })
                }
            } catch (e) {
                console.warn('[WatchTheBlue] prediction preflight failed:', e)
                if (!cancelled) setPredictionService({ status: 'offline', message: 'Prediction offline' })
            }
        })()
        return () => { cancelled = true }
    }, [])

    useEffect(() => {
        let cancelled = false
        ;(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/zone-analysis?lat=13&lon=80`)
                if (!res.ok) return
                const data = await res.json()
                if (!cancelled && data.zones_risk_overlay) setZonesRiskOverlay(data.zones_risk_overlay)
            } catch (e) {
                console.warn('[WatchTheBlue] initial sector overlay prefetch:', e)
            }
        })()
        return () => { cancelled = true }
    }, [])

    useEffect(() => {
        if (!selectedSpeciesId) return undefined
        const sp = DRIFT_SPECIES.find(s => s.id === selectedSpeciesId)
        if (!sp) return undefined
        let cancelled = false
        ;(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/species-risk?lat=${sp.strandingLat}&lon=${sp.strandingLon}`)
                if (!res.ok) throw new Error(String(res.status))
                const j = await res.json()
                if (!cancelled && j.zones_risk_overlay) setZonesRiskOverlay(j.zones_risk_overlay)
            } catch (e) {
                console.warn('[WatchTheBlue] species-risk overlay:', e)
            }
        })()
        return () => { cancelled = true }
    }, [selectedSpeciesId])

    return (
        <div className="map-page-root">
            <header className="map-topbar">
                <div className="map-topbar-center">
                    <span className="map-live-dot" />
                    <span className="map-live-label">LIVE FEED</span>
                    <span className={`map-health-chip map-health-chip--${predictionService.status}`}>
                        {predictionService.message}
                    </span>
                    <span className="map-topbar-tagline">Indian Ocean · AI-assisted stranding risk intelligence</span>
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

            <DriftSpeciesBar selected={selectedSpeciesId} onSelect={setSelectedSpeciesId} />
            <SpeciesTrackerBar selectedSpecies={selectedTrackerSpecies} onSelectSpecies={setSelectedTrackerSpecies} />

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

                        <ZoneRiskOverlays zones={ZONES} overlay={zonesRiskOverlay} />
                        <SpeciesZoneMarkers selectedSpecies={selectedTrackerSpecies} />

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

                        <DriftTracker
                            selectedSpeciesId={selectedSpeciesId}
                            onSelectSpecies={setSelectedSpeciesId}
                            mapZones={ZONES}
                            zonesRiskOverlay={zonesRiskOverlay}
                        />

                        <MapClickHandler onZoneSelect={fetchZoneData} />
                    </MapContainer>

                    <DriftInfoCard speciesId={selectedSpeciesId} />
                </div>

                <div className={`map-side-panel-wrap${selectedData ? ' map-side-panel-open' : ''}`}>
                    {selectedData && (
                        <ZonePanel
                            data={selectedData}
                            loading={loading}
                            predictionError={predictionError}
                            onClose={() => setSelectedData(null)}
                        />
                    )}
                </div>
            </div>
        </div>
    )
}