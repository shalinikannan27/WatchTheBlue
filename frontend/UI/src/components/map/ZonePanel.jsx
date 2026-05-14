function normalizeSpeciesEntry(raw, fallbackRisk = 'moderate') {
    if (raw == null) return null
    if (typeof raw === 'string') {
        return {
            name: raw,
            risk: fallbackRisk,
            ngo: 'Regional monitoring',
            note: 'Listed from ecosystem stress heuristics.',
        }
    }
    const risk = raw.risk === 'critical' ? 'high' : (raw.risk || fallbackRisk)
    return {
        name: raw.name || 'Unknown',
        risk,
        ngo: raw.ngo || '—',
        note: raw.note || '',
        model_confidence: raw.model_confidence,
    }
}

export default function ZonePanel({ data, loading, onClose, predictionError = false }) {
    const riskColors = {
        low: '#22c55e',
        moderate: '#facc15',
        high: '#ef4444',
    }

    const zoneLabel = (data?.zone_display || data?.zone || '').replace(/_/g, ' ')
    const zoneTitle = zoneLabel ? zoneLabel.toUpperCase() : 'LOADING…'

    const pred = data?.prediction
    const fallbackRisk = data?.stress_level || 'moderate'
    const speciesList = (data?.species_at_risk || [])
        .map(s => normalizeSpeciesEntry(s, fallbackRisk))
        .filter(Boolean)

    const tempAnom = data?.conditions?.temperature_anomaly
    const rows = data
        ? [
              {
                  icon: '🌡️',
                  label: 'Temperature',
                  value: `${data.conditions?.temperature ?? '—'}°C`,
                  sub:
                      tempAnom != null
                          ? `${tempAnom >= 0 ? '+' : ''}${tempAnom}°C vs seasonal baseline`
                          : 'Live SST from NOAA blend',
              },
              {
                  icon: '💧',
                  label: 'Dissolved Oxygen',
                  value: `${data.conditions?.oxygen ?? '—'} mg/L`,
                  sub:
                      data.conditions?.oxygen != null && data.conditions.oxygen < 4
                          ? 'Below safe threshold'
                          : 'Estimated from productivity & mixing',
              },
              {
                  icon: 'pH',
                  label: 'pH Level',
                  value: data.conditions?.ph ?? '—',
                  sub:
                      data.conditions?.ph != null && data.conditions.ph < 8
                          ? 'Acidification pressure'
                          : 'Within typical surface range',
              },
          ]
        : []

    return (
        <aside className="zone-detail-panel">
            <div className="zdp-header">
                <div className="zdp-header-left">
                    <div className="zdp-badge">ZONE ANALYSIS</div>
                    <h2 className="zdp-title">{zoneTitle}</h2>
                </div>
                <button type="button" onClick={onClose} className="zdp-close-btn" aria-label="Close panel">
                    ✕
                </button>
            </div>

            {loading && (
                <div className="zdp-loading">
                    <div className="zdp-loading-dot" />
                    <span>Fetching live ocean conditions · running ML risk fusion…</span>
                </div>
            )}

            {!loading && data && (
                <div className="zdp-body">
                    {predictionError && (
                        <div className="zdp-fallback-banner" role="alert">
                            <span>Prediction service unavailable — showing cached sample layout. Check API logs.</span>
                        </div>
                    )}

                    {data.ml_layer_summary && (
                        <p className="zdp-context-line">{data.ml_layer_summary}</p>
                    )}

                    {data.coral_bleaching_alert && (
                        <div className="zdp-alert">
                            <div className="zdp-alert-icon">⚠️</div>
                            <div>
                                <p className="zdp-alert-title">CORAL BLEACHING ALERT</p>
                                <p className="zdp-alert-sub">Thermal stress elevated vs seasonal baseline (NOAA DHW blend).</p>
                            </div>
                        </div>
                    )}

                    <div className="zdp-score-card">
                        <p className="zdp-score-label">OCEAN STRESS SCORE</p>
                        <div className="zdp-score-gauge">
                            <svg viewBox="0 0 120 120" width="120" height="120" style={{ transform: 'rotate(-90deg)' }}>
                                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(0,180,255,0.15)" strokeWidth="8" />
                                <circle
                                    cx="60"
                                    cy="60"
                                    r="50"
                                    fill="none"
                                    stroke={data.stress_color || '#00d4ff'}
                                    strokeWidth="9"
                                    strokeLinecap="round"
                                    strokeDasharray={`${2 * Math.PI * 50}`}
                                    strokeDashoffset={`${2 * Math.PI * 50 * (1 - (data.stress_score || 0) / 100)}`}
                                    style={{ transition: 'stroke-dashoffset 0.6s ease', filter: `drop-shadow(0 0 6px ${data.stress_color || '#00d4ff'})` }}
                                />
                            </svg>
                            <div className="zdp-score-center">
                                <span className="zdp-score-number">{data.stress_score}</span>
                                <span className="zdp-score-level" style={{ color: data.stress_color }}>
                                    {data.stress_level?.toUpperCase()}
                                </span>
                            </div>
                        </div>
                    </div>

                    {pred && (
                        <>
                            <div className="zdp-section-header">
                                <span>AI PREDICTION INSIGHTS</span>
                                <div className="zdp-section-line" />
                            </div>
                            <div className="zdp-pred-grid">
                                <div className="zdp-pred-metric">
                                    <span className="zdp-pred-label">Stranding stress index</span>
                                    <span className="zdp-pred-value">{Math.round((pred.risk_probability || 0) * 100)}%</span>
                                </div>
                                <div className="zdp-pred-metric">
                                    <span className="zdp-pred-label">Risk band</span>
                                    <span className="zdp-pred-badge" data-level={pred.risk_level}>{pred.risk_level}</span>
                                </div>
                                <div className="zdp-pred-metric zdp-pred-metric-wide">
                                    <span className="zdp-pred-label">Model confidence</span>
                                    <div className="zdp-confidence-track">
                                        <div className="zdp-confidence-fill" style={{ width: `${Math.min(100, (pred.confidence_score || 0) * 100)}%` }} />
                                    </div>
                                    <span className="zdp-pred-sub">
                                        {pred.models_used?.length ? `Artifacts: ${pred.models_used.join(', ')}` : 'Stress engine only (no .pkl in models/)'}
                                    </span>
                                </div>
                            </div>

                            {pred.top_environmental_factors?.length > 0 && (
                                <div className="zdp-shap-block">
                                    <p className="zdp-shap-title">Ecological drivers (SHAP-style)</p>
                                    {pred.top_environmental_factors.map(f => (
                                        <div key={f.factor} className="zdp-shap-row">
                                            <span className="zdp-shap-name">{String(f.factor).replace(/_/g, ' ')}</span>
                                            <div className="zdp-shap-bar-wrap">
                                                <div className="zdp-shap-bar" style={{ width: `${Math.min(100, Math.max(6, (f.contribution || 0) * 220))}%` }} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}

                    <div className="zdp-section-header"><span>CURRENT CONDITIONS</span><div className="zdp-section-line" /></div>
                    <div className="zdp-conditions">
                        {rows.map(item => (
                            <div key={item.label} className="zdp-condition-row">
                                <div className="zdp-condition-left">
                                    <span className="zdp-condition-icon">{item.icon}</span>
                                    <div>
                                        <p className="zdp-condition-label">{item.label}</p>
                                        <p className="zdp-condition-sub">{item.sub}</p>
                                    </div>
                                </div>
                                <span className="zdp-condition-value">{item.value}</span>
                            </div>
                        ))}
                    </div>

                    <div className="zdp-section-header"><span>SPECIES &amp; SENTINELS</span><div className="zdp-section-line" /></div>
                    <div className="zdp-species-list">
                        {speciesList.map(species => (
                            <div key={species.name} className="zdp-species-card" style={{ '--risk-color': riskColors[species.risk] || '#ef4444' }}>
                                <div className="zdp-species-header">
                                    <strong className="zdp-species-name">{species.name}</strong>
                                    <span className="zdp-species-badge" style={{ background: riskColors[species.risk] || '#ef4444' }}>
                                        {(species.risk || 'high').toUpperCase()}
                                    </span>
                                </div>
                                {species.model_confidence != null && (
                                    <div className="zdp-mini-confidence">
                                        <span>RF confidence</span>
                                        <div className="zdp-confidence-track zdp-confidence-track--thin">
                                            <div className="zdp-confidence-fill" style={{ width: `${Math.min(100, species.model_confidence * 100)}%` }} />
                                        </div>
                                    </div>
                                )}
                                <p className="zdp-species-note">{species.note}</p>
                                <p className="zdp-species-ngo">🤝 {species.ngo}</p>
                            </div>
                        ))}
                    </div>

                    <div className="zdp-footer">
                        <span>{data.platform_tagline || 'WatchTheBlue · Indian Ocean resilience watch'}</span>
                        <span>Source: NOAA / CMEMS / OBIS blend</span>
                    </div>
                </div>
            )}
        </aside>
    )
}