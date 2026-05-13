/**
 * DriftTracker.jsx
 * Visualises backward drift paths on the Leaflet map.
 * Reads data from driftData.js — no backend changes required.
 */
import { useEffect, useState, useMemo, useCallback } from 'react'
import { Polyline, CircleMarker, Marker, Tooltip, useMap } from 'react-leaflet'
import { divIcon } from 'leaflet'
import { DRIFT_SPECIES, getSpeciesDriftPath } from '../data/driftData'

// ─── Helpers ────────────────────────────────────────────────────────────────
function formatTS(iso) {
  try {
    const d = new Date(iso)
    return d.toLocaleString('en-IN', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch { return iso }
}

function makeSpeciesIcon(species, isSelected) {
  const size = isSelected ? 32 : 24
  return divIcon({
    className: 'drift-icon-wrapper',
    html: `<div class="drift-species-icon${isSelected ? ' drift-icon-selected' : ''}"
              style="--drift-color:${species.color};--drift-glow:${species.glowColor};width:${size}px;height:${size}px;">
             <span style="font-size:${isSelected ? 18 : 14}px;">${species.icon}</span>
           </div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function makeOriginIcon(species) {
  return divIcon({
    className: 'drift-icon-wrapper',
    html: `<div class="drift-origin-icon" style="--drift-color:${species.color};">◎</div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  })
}

// ─── Animated current-position hook ─────────────────────────────────────────
function useAnimatedPosition(path, isSelected) {
  const [frame, setFrame] = useState(0)

  useEffect(() => {
    if (!isSelected || path.length < 2) { setFrame(0); return }
    // Animate forward along path (stranding → origin)
    const id = setInterval(() => {
      setFrame(f => (f + 1) % path.length)
    }, 900)
    return () => clearInterval(id)
  }, [isSelected, path.length])

  return frame
}

// ─── Map auto-pan when species selected ─────────────────────────────────────
function MapPanner({ path, active }) {
  const map = useMap()
  useEffect(() => {
    if (!active || !path.length) return
    const lats = path.map(p => p.lat)
    const lons = path.map(p => p.lon)
    const bounds = [
      [Math.min(...lats) - 0.5, Math.min(...lons) - 0.5],
      [Math.max(...lats) + 0.5, Math.max(...lons) + 0.5],
    ]
    map.flyToBounds(bounds, { duration: 1.2, padding: [60, 60] })
  }, [active]) // eslint-disable-line
  return null
}

// ─── Single species drift layer ──────────────────────────────────────────────
function SpeciesDriftLayer({ species, isSelected, onSelect }) {
  const path = useMemo(() => getSpeciesDriftPath(species.id), [species.id])
  const latlngs = useMemo(() => path.map(p => [p.lat, p.lon]), [path])
  const frame = useAnimatedPosition(path, isSelected)

  if (!path.length) return null

  const stranding = path[0]         // index 0 = stranding (most recent)
  const origin = path[path.length - 1] // last = estimated origin
  const currentPt = path[frame]

  const opacity = isSelected ? 1 : 0.35
  const weight = isSelected ? 2.5 : 1.5

  return (
    <>
      <MapPanner path={path} active={isSelected} />

      {/* ── Full historical trail (faded) ── */}
      <Polyline
        positions={latlngs}
        pathOptions={{
          color: species.color,
          weight,
          opacity: opacity * 0.4,
          dashArray: '6 5',
        }}
        eventHandlers={{ click: () => onSelect(species.id) }}
      >
        <Tooltip sticky>
          <div className="drift-tooltip">
            <strong>{species.icon} {species.name}</strong>
            <span>Backward drift path · {species.hours}h</span>
          </div>
        </Tooltip>
      </Polyline>

      {/* ── Glowing main route line ── */}
      <Polyline
        positions={latlngs.slice(0, frame + 1)}
        pathOptions={{
          color: species.color,
          weight: isSelected ? 3 : 2,
          opacity: isSelected ? 0.85 : 0.5,
        }}
        eventHandlers={{ click: () => onSelect(species.id) }}
      />

      {/* ── Historical waypoint dots ── */}
      {isSelected && path.slice(1, -1).map((pt, i) => (
        <CircleMarker
          key={`${species.id}-wp-${i}`}
          center={[pt.lat, pt.lon]}
          radius={3}
          pathOptions={{
            color: species.color,
            fillColor: species.color,
            fillOpacity: 0.5,
            weight: 1,
            opacity: 0.6,
          }}
        >
          <Tooltip>
            <div className="drift-tooltip">
              <strong>Step {pt.step}</strong>
              <span>{pt.lat.toFixed(3)}°N, {pt.lon.toFixed(3)}°E</span>
              <span>{formatTS(pt.timestamp)}</span>
              <span className="drift-tooltip-status">Backward drift waypoint</span>
            </div>
          </Tooltip>
        </CircleMarker>
      ))}

      {/* ── Origin (estimated source) marker ── */}
      <Marker
        position={[origin.lat, origin.lon]}
        icon={makeOriginIcon(species)}
        zIndexOffset={isSelected ? 500 : 100}
      >
        <Tooltip permanent={isSelected} direction="top" offset={[0, -12]}>
          <div className="drift-tooltip">
            <strong>🔵 Estimated Origin</strong>
            <span>{origin.lat.toFixed(3)}°N, {origin.lon.toFixed(3)}°E</span>
            <span>{formatTS(origin.timestamp)}</span>
            <span className="drift-tooltip-status">{species.hours}h backward drift</span>
          </div>
        </Tooltip>
      </Marker>

      {/* ── Stranding / current-position species icon ── */}
      <Marker
        position={[stranding.lat, stranding.lon]}
        icon={makeSpeciesIcon(species, isSelected)}
        zIndexOffset={isSelected ? 1000 : 200}
        eventHandlers={{ click: () => onSelect(species.id) }}
      >
        <Tooltip permanent={isSelected} direction="top" offset={[0, -20]}>
          <div className="drift-tooltip">
            <strong>{species.icon} {species.name}</strong>
            <span>📍 Stranding Point</span>
            <span>{stranding.lat.toFixed(3)}°N, {stranding.lon.toFixed(3)}°E</span>
            <span>{formatTS(stranding.timestamp)}</span>
            <span className="drift-tooltip-status">{species.status}</span>
          </div>
        </Tooltip>
      </Marker>

      {/* ── Animated current position pulse ── */}
      {isSelected && (
        <CircleMarker
          center={[currentPt.lat, currentPt.lon]}
          radius={7}
          pathOptions={{
            color: species.color,
            fillColor: species.color,
            fillOpacity: 0.9,
            weight: 2,
          }}
        >
          <Tooltip>
            <div className="drift-tooltip">
              <strong>📡 Tracking Position</strong>
              <span>{currentPt.lat.toFixed(4)}°N, {currentPt.lon.toFixed(4)}°E</span>
              <span>Step {currentPt.step} / {path.length - 1}</span>
              <span>{formatTS(currentPt.timestamp)}</span>
            </div>
          </Tooltip>
        </CircleMarker>
      )}
    </>
  )
}

// ─── Main exported component ─────────────────────────────────────────────────
export default function DriftTracker({ selectedSpeciesId, onSelectSpecies }) {
  const handleSelect = useCallback((id) => {
    onSelectSpecies(prev => prev === id ? null : id)
  }, [onSelectSpecies])

  return (
    <>
      {DRIFT_SPECIES.map(species => (
        <SpeciesDriftLayer
          key={species.id}
          species={species}
          isSelected={selectedSpeciesId === species.id}
          onSelect={handleSelect}
        />
      ))}
    </>
  )
}
