const BASE_URL = "http://localhost:8000";

// ── Zone endpoints ────────────────────────────────────────────────────────────
export const getZoneData = async (zoneId: string) => {
  const res = await fetch(`${BASE_URL}/api/zone/${zoneId}`);
  if (!res.ok) throw new Error(`Zone fetch failed: ${res.status}`);
  return res.json();
};

export const getAllZones = async () => {
  const res = await fetch(`${BASE_URL}/api/overview`);
  if (!res.ok) throw new Error(`Overview fetch failed: ${res.status}`);
  return res.json();
};

// ── Species endpoints ─────────────────────────────────────────────────────────
export const getSpeciesRisk = async (speciesName: string) => {
  const encoded = encodeURIComponent(speciesName);
  const res = await fetch(`${BASE_URL}/api/species/${encoded}`);
  if (!res.ok) throw new Error(`Species fetch failed: ${res.status}`);
  return res.json();
};

// ── NOAA SST endpoint ─────────────────────────────────────────────────────────
export const getNoaaSST = async (lat: number, lon: number) => {
  const res = await fetch(`${BASE_URL}/api/noaa/sst?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`NOAA fetch failed: ${res.status}`);
  return res.json();
};

// ── CMEMS marine metrics ──────────────────────────────────────────────────────
export const getCmemsMetrics = async (lat: number, lon: number) => {
  const res = await fetch(`${BASE_URL}/api/cmems/marine-metrics?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`CMEMS fetch failed: ${res.status}`);
  return res.json();
};

// ── Ecological stress ─────────────────────────────────────────────────────────
export const getEcologicalStress = async (lat: number, lon: number) => {
  const res = await fetch(`${BASE_URL}/api/ecological-stress?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`Stress fetch failed: ${res.status}`);
  return res.json();
};

// ── ML zone analysis (click on map) ──────────────────────────────────────────
export const getZoneAnalysis = async (lat: number, lon: number) => {
  const res = await fetch(`${BASE_URL}/api/zone-analysis?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`Zone analysis fetch failed: ${res.status}`);
  return res.json();
};

// ── Drift path ────────────────────────────────────────────────────────────────
export const getDriftPath = async (lat: string | number, lon: string | number, date: string) => {
  const res = await fetch(`${BASE_URL}/api/drift?lat=${lat}&lon=${lon}&date=${date}`);
  if (!res.ok) throw new Error(`Drift fetch failed: ${res.status}`);
  return res.json();
};

// ── Health check ──────────────────────────────────────────────────────────────
export const getBackendHealth = async () => {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
};
