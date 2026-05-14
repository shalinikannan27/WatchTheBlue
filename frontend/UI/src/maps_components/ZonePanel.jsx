export default function ZonePanel({ data, loading, onClose }) {
    const riskColors = {
        low:      '#22c55e',
        moderate: '#facc15',
        high:     '#a855f7',
        critical: '#ef4444'
    }

    const zoneTitle = (data?.zone_name || data?.zone || '')
        .replace(/_/g, ' ')
        .toUpperCase()

    const conds = data?.conditions || {}

    // Timestamp formatting
    const formattedTime = (() => {
        try {
            const d = new Date(data?.timestamp)
            return d.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', hour12: true,
                year: 'numeric', month: 'short', day: 'numeric',
                hour: '2-digit', minute: '2-digit' })
        } catch { return 'Live' }
    })()

    const rows = data ? [
        {
            icon: '🌡️',
            label: 'Temperature',
            value: `${Number(conds.temperature ?? 28).toFixed(1)}°C`,
            sub: `${conds.temperature_anomaly >= 0 ? '+' : ''}${Number(conds.temperature_anomaly ?? 0).toFixed(1)}°C above normal`
        },
        {
            icon: '💧',
            label: 'Dissolved Oxygen',
            value: `${Number(conds.oxygen ?? 5).toFixed(1)} ml/L`,
            sub: (conds.oxygen ?? 5) < 4 ? '⚠ Below safe threshold' : 'Normal range'
        },
        {
            icon: '⚗️',
            label: 'pH Level',
            value: Number(conds.ph ?? 8.1).toFixed(2),
            sub: (conds.ph ?? 8.1) < 8 ? '⚠ Acidification risk' : 'Normal range'
        },
        {
            icon: '🧂',
            label: 'Salinity',
            value: `${Number(conds.salinity ?? 35).toFixed(1)} PSU`,
            sub: (conds.salinity ?? 35) > 37 ? 'Elevated evaporation' : 'Normal range'
        },
        {
            icon: '🌊',
            label: 'Current Speed',
            value: `${Number(conds.current_speed ?? 0.3).toFixed(2)} m/s`,
            sub: (conds.current_speed ?? 0.3) > 0.5 ? 'Strong — drift risk elevated' : 'Moderate flow'
        }
    ] : []

    return (
        <aside className="zone-detail-panel">
            {/* Header */}
            <div className="zdp-header">
                <div className="zdp-header-left">
                    <div className="zdp-badge">ZONE ANALYSIS</div>
                    <h2 className="zdp-title">{zoneTitle || 'LOADING…'}</h2>
                </div>
                <button onClick={onClose} className="zdp-close-btn" aria-label="Close panel">✕</button>
            </div>

            {loading && (
                <div className="zdp-loading">
                    <div className="zdp-loading-dot" />
                    <span>Fetching live ocean conditions…</span>
                </div>
            )}

            {!loading && data && (
                <div className="zdp-body">
                    {/* Data source badge */}
                    {data.data_source && (
                        <div style={{
                            fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase',
                            letterSpacing: '0.1em', color: 'rgba(255,255,255,0.3)',
                            padding: '4px 0 8px', borderBottom: '1px solid rgba(255,255,255,0.06)',
                            marginBottom: '8px'
                        }}>
                            📡 {data.data_source}
                        </div>
                    )}

                    {/* Coral bleaching alert */}
                    {data.coral_bleaching_alert && (
                        <div className="zdp-alert">
                            <div className="zdp-alert-icon">⚠️</div>
                            <div>
                                <p className="zdp-alert-title">CORAL BLEACHING ALERT</p>
                                <p className="zdp-alert-sub">
                                    Temperature {Number(conds.temperature_anomaly ?? 0).toFixed(1)}°C above seasonal average
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Stress score gauge */}
                    <div className="zdp-score-card">
                        <p className="zdp-score-label">OCEAN STRESS SCORE</p>
                        <div className="zdp-score-gauge">
                            <svg viewBox="0 0 120 120" width="120" height="120" style={{ transform: 'rotate(-90deg)' }}>
                                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(0,180,255,0.15)" strokeWidth="8" />
                                <circle
                                    cx="60" cy="60" r="50"
                                    fill="none"
                                    stroke={data.stress_color || '#00d4ff'}
                                    strokeWidth="9"
                                    strokeLinecap="round"
                                    strokeDasharray={`${2 * Math.PI * 50}`}
                                    strokeDashoffset={`${2 * Math.PI * 50 * (1 - (data.stress_score ?? 0) / 100)}`}
                                    style={{
                                        transition: 'stroke-dashoffset 0.6s ease',
                                        filter: `drop-shadow(0 0 6px ${data.stress_color || '#00d4ff'})`
                                    }}
                                />
                            </svg>
                            <div className="zdp-score-center">
                                <span className="zdp-score-number">{data.stress_score ?? '–'}</span>
                                <span className="zdp-score-level" style={{ color: data.stress_color }}>
                                    {(data.stress_level || '').toUpperCase()}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Current conditions */}
                    <div className="zdp-section-header">
                        <span>CURRENT CONDITIONS</span>
                        <div className="zdp-section-line" />
                    </div>
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

                    {/* Species at risk */}
                    {(data.species_at_risk || []).length > 0 && (
                        <>
                            <div className="zdp-section-header">
                                <span>SPECIES AT RISK</span>
                                <div className="zdp-section-line" />
                            </div>
                            <div className="zdp-species-list">
                                {data.species_at_risk.map(species => (
                                    <div
                                        key={species.name}
                                        className="zdp-species-card"
                                        style={{ '--risk-color': riskColors[species.risk] || '#a855f7' }}
                                    >
                                        <div className="zdp-species-header">
                                            <strong className="zdp-species-name">{species.name}</strong>
                                            <span
                                                className="zdp-species-badge"
                                                style={{ background: riskColors[species.risk] || '#a855f7' }}
                                            >
                                                {(species.risk || 'high').toUpperCase()}
                                            </span>
                                        </div>
                                        <p className="zdp-species-note">{species.note}</p>
                                        <p className="zdp-species-ngo">🤝 {species.ngo}</p>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {/* Footer */}
                    <div className="zdp-footer">
                        <span>Updated: {formattedTime}</span>
                        <span>Source: WatchTheBlue</span>
                    </div>
                </div>
            )}
        </aside>
    )
}