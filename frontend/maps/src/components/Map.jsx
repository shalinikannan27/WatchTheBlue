import { MapContainer, TileLayer, Marker, Tooltip, useMapEvents } from 'react-leaflet'
import { useState } from 'react'
import { divIcon } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import ZonePanel from './ZonePanel'

const ZONES = [
    { id: 'arabian_sea', name: 'Arabian Sea', color: '#22c55e', center: [16, 72], bounds: [[10, 68], [23, 77]] },
    { id: 'bay_of_bengal', name: 'Bay of Bengal', color: '#facc15', center: [15, 85], bounds: [[10, 80], [20, 90]] },
    { id: 'lakshadweep', name: 'Lakshadweep Sea', color: '#a855f7', center: [10, 73], bounds: [[8, 72], [12, 74]] },
    { id: 'andaman_sea', name: 'Andaman Sea', color: '#ef4444', center: [12, 95], bounds: [[10, 92], [14, 98]] }
]

const SAMPLE_ZONE_DATA = {
    arabian_sea: {
        zone: 'arabian_sea',
        conditions: { temperature: 28.1, temperature_anomaly: 0.7, oxygen: 4.8, ph: 8.11 },
        stress_score: 35,
        stress_level: 'moderate',
        stress_color: '#facc15',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Indian Ocean Humpback Dolphin', risk: 'moderate', ngo: 'Terra Conscious', note: 'Entanglement risk increasing in coastal shipping lanes.' },
            { name: 'Green Sea Turtle', risk: 'moderate', ngo: 'Wildlife Trust of India', note: 'Nesting beaches under pressure from light pollution.' }
        ]
    },
    bay_of_bengal: {
        zone: 'bay_of_bengal',
        conditions: { temperature: 29.8, temperature_anomaly: 1.6, oxygen: 3.9, ph: 8.02 },
        stress_score: 67,
        stress_level: 'high',
        stress_color: '#a855f7',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Olive Ridley Sea Turtle', risk: 'high', ngo: 'TREE Foundation', note: 'Mass strandings documented on Odisha coast.' },
            { name: 'Irrawaddy Dolphin', risk: 'high', ngo: 'WWF India', note: 'Delta habitat fragmentation impacting breeding zones.' }
        ]
    },
    lakshadweep: {
        zone: 'lakshadweep',
        conditions: { temperature: 31.2, temperature_anomaly: 2.3, oxygen: 3.5, ph: 7.94 },
        stress_score: 82,
        stress_level: 'critical',
        stress_color: '#ef4444',
        coral_bleaching_alert: true,
        species_at_risk: [
            { name: 'Hawksbill Turtle', risk: 'critical', ngo: 'Dakshin Foundation', note: 'Reef bleaching reducing foraging habitat quality.' },
            { name: 'Spinner Dolphin', risk: 'high', ngo: 'Coastal Impact', note: 'Tourism vessel traffic disrupting resting lagoons.' }
        ]
    },
    andaman_sea: {
        zone: 'andaman_sea',
        conditions: { temperature: 27.4, temperature_anomaly: 0.3, oxygen: 5.2, ph: 8.16 },
        stress_score: 28,
        stress_level: 'healthy',
        stress_color: '#22c55e',
        coral_bleaching_alert: false,
        species_at_risk: [
            { name: 'Dugong', risk: 'moderate', ngo: 'ReefWatch Marine Conservation', note: 'Seagrass meadows are stable but monitored for decline.' },
            { name: 'Andaman Clownfish', risk: 'low', ngo: 'ANET', note: 'Localized reef stress near high-diving routes.' }
        ]
    }
}

function createZoneDotIcon(zone) {
    return divIcon({
        className: 'zone-dot-icon-wrapper',
        html: `<div class="zone-dot" style="--zone-color:${zone.color};"></div>`,
        iconSize: [10, 10],
        iconAnchor: [5, 5]
    })
}

function zoneForPoint(lat, lon) {
    const matched = ZONES.find((zone) => {
        const [[south, west], [north, east]] = zone.bounds
        return lat >= south && lat <= north && lon >= west && lon <= east
    })
    if (matched) return matched

    return ZONES.reduce((nearest, zone) => {
        const [zLat, zLon] = zone.center
        const [nLat, nLon] = nearest.center
        const d1 = (lat - zLat) ** 2 + (lon - zLon) ** 2
        const d2 = (lat - nLat) ** 2 + (lon - nLon) ** 2
        return d1 < d2 ? zone : nearest
    }, ZONES[0])
}

export default function Map() {
    const [selectedData, setSelectedData] = useState(null)
    const [loading, setLoading] = useState(false)

    async function fetchZoneData(zone) {
        const [lat, lon] = zone.center
        setLoading(true)
        try {
            const res = await fetch(`http://localhost:8000/api/zone?lat=${lat}&lon=${lon}`)
            const data = await res.json()
            setSelectedData(data?.zone ? data : { ...SAMPLE_ZONE_DATA[zone.id] })
        } catch (err) {
            setSelectedData({ ...SAMPLE_ZONE_DATA[zone.id] })
        } finally {
            setLoading(false)
        }
    }

    function MapClickHandler() {
        useMapEvents({
            click(e) {
                const zone = zoneForPoint(e.latlng.lat, e.latlng.lng)
                fetchZoneData(zone)
            }
        })
        return null
    }

    return (
        <div style={{ display: 'flex', height: '100%', width: '100%', position: 'relative' }}>
            <div style={{ height: '100%', width: '100%', position: 'relative' }}>

            <div className="classic-legend">
                {[
                    { color: '#22c55e', label: 'Healthy' },
                    { color: '#facc15', label: 'Moderate' },
                    { color: '#a855f7', label: 'High' },
                    { color: '#ef4444', label: 'Critical' }
                ].map(item => (
                    <div key={item.label} className="classic-legend-item">
                        <span className="classic-legend-dot" style={{ '--dot-color': item.color }} />
                        <span>{item.label}</span>
                    </div>
                ))}
            </div>

            <MapContainer center={[18, 70]} zoom={3} style={{ height: '100%', width: '100%' }} zoomControl={false}>
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
                    attribution="Esri Ocean Basemap"
                />
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png"
                    attribution="Carto"
                />

                {ZONES.map(zone => (
                    <Marker
                        key={zone.id}
                        position={zone.center}
                        icon={createZoneDotIcon(zone)}
                        eventHandlers={{ click: () => fetchZoneData(zone) }}
                    >
                        <Tooltip permanent direction="top" offset={[0, -8]} className="classic-zone-label">
                            <span className="classic-zone-label-text">{zone.name}</span>
                        </Tooltip>
                    </Marker>
                ))}
                <MapClickHandler />
            </MapContainer>
            </div>

            {selectedData && <ZonePanel data={selectedData} loading={loading} onClose={() => setSelectedData(null)} />}
        </div>
    )
}