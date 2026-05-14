/**
 * driftData.js
 * Mirrors the backward drift algorithm from drift.py (WatchTheBlue/drift.py).
 * Uses the same dummy current_speed grid as the Python fallback.
 * Output: array of [lat, lon] tuples — oldest (origin) → newest (stranding).
 */

const GRID_LATS = [20.0, 20.2, 20.4]
const GRID_LONS = [86.5, 86.7, 86.9]
const U_GRID = [
  [0.10, 0.20, 0.15],
  [0.25, 0.30, 0.20],
  [0.10, 0.18, 0.12],
]
const V_GRID = U_GRID

function interpolate(grid, lats, lons, lat, lon) {
  const clampedLat = Math.max(lats[0], Math.min(lats[lats.length - 1], lat))
  const clampedLon = Math.max(lons[0], Math.min(lons[lons.length - 1], lon))

  let i = lats.findIndex(l => l > clampedLat) - 1
  let j = lons.findIndex(l => l > clampedLon) - 1
  i = Math.max(0, Math.min(lats.length - 2, i))
  j = Math.max(0, Math.min(lons.length - 2, j))

  const t = (clampedLat - lats[i]) / (lats[i + 1] - lats[i])
  const s = (clampedLon - lons[j]) / (lons[j + 1] - lons[j])

  return (
    grid[i][j] * (1 - t) * (1 - s) +
    grid[i + 1][j] * t * (1 - s) +
    grid[i][j + 1] * (1 - t) * s +
    grid[i + 1][j + 1] * t * s
  )
}

export function computeDriftPath(
  strandingLat,
  strandingLon,
  hours = 72,
  dtHours = 6,
  baseDate = new Date('2025-05-20T10:30:00')
) {
  const dtSeconds = dtHours * 3600
  const steps = Math.floor(hours / dtHours)

  const path = []
  let curLat = strandingLat
  let curLon = strandingLon

  path.push({
    lat: curLat,
    lon: curLon,
    step: 0,
    timestamp: new Date(baseDate).toISOString(),
  })

  for (let step = 1; step <= steps; step++) {
    const uAtPt = interpolate(U_GRID, GRID_LATS, GRID_LONS, curLat, curLon)
    const vAtPt = interpolate(V_GRID, GRID_LATS, GRID_LONS, curLat, curLon)

    const deltaLat = -(vAtPt * dtSeconds) / 111_000
    const deltaLon = -(uAtPt * dtSeconds) / (111_000 * Math.cos((curLat * Math.PI) / 180))

    curLat = parseFloat((curLat + deltaLat).toFixed(4))
    curLon = parseFloat((curLon + deltaLon).toFixed(4))

    const ts = new Date(baseDate.getTime() - step * dtHours * 3600 * 1000)
    path.push({ lat: curLat, lon: curLon, step, timestamp: ts.toISOString() })
  }

  return path
}

export const DRIFT_SPECIES = [
  {
    id: 'olive_ridley',
    name: 'Olive Ridley Turtle',
    icon: '🐢',
    color: '#22c55e',
    glowColor: 'rgba(34,197,94,0.55)',
    strandingLat: 20.2,
    strandingLon: 86.7,
    hours: 72,
    dtHours: 6,
    zone: 'bay_of_bengal',
    status: 'Tracked · Backward drift 72h',
    risk: 'high',
    note: 'Mass stranding documented on Odisha coast. Backward drift traces oceanic origin.',
  },
  {
    id: 'spinner_dolphin',
    name: 'Spinner Dolphin',
    icon: '🐬',
    color: '#38bdf8',
    glowColor: 'rgba(56,189,248,0.55)',
    strandingLat: 10.5,
    strandingLon: 72.8,
    hours: 48,
    dtHours: 6,
    zone: 'lakshadweep',
    status: 'Tracked · Backward drift 48h',
    risk: 'high',
    note: 'Tourism vessel traffic disrupts resting lagoons. Drift trace from Lakshadweep.',
  },
  {
    id: 'dugong',
    name: 'Dugong',
    icon: '🌊',
    color: '#a78bfa',
    glowColor: 'rgba(167,139,250,0.55)',
    strandingLat: 12.3,
    strandingLon: 93.1,
    hours: 60,
    dtHours: 6,
    zone: 'andaman_sea',
    status: 'Tracked · Backward drift 60h',
    risk: 'moderate',
    note: 'Seagrass meadows monitored. Drift path estimated from Andaman Sea sighting.',
  },
  {
    id: 'green_sea_turtle',
    name: 'Green Sea Turtle',
    icon: '🐠',
    color: '#f59e0b',
    glowColor: 'rgba(245,158,11,0.55)',
    strandingLat: 15.8,
    strandingLon: 73.7,
    hours: 72,
    dtHours: 6,
    zone: 'arabian_sea',
    status: 'Tracked · Backward drift 72h',
    risk: 'moderate',
    note: 'Nesting beaches under light pollution pressure. Drift traced from Arabian Sea.',
  },
]

const _cache = {}
export function getSpeciesDriftPath(speciesId) {
  if (_cache[speciesId]) return _cache[speciesId]
  const species = DRIFT_SPECIES.find(s => s.id === speciesId)
  if (!species) return []
  const path = computeDriftPath(
    species.strandingLat,
    species.strandingLon,
    species.hours,
    species.dtHours
  )
  _cache[speciesId] = path
  return path
}