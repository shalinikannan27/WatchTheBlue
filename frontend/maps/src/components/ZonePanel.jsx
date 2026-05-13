export default function ZonePanel({ data, loading, onClose }) {
    const riskColors = {
        low:      '#22c55e',
        moderate: '#facc15',
        high:     '#a855f7',
        critical: '#ef4444'
    }

    const zoneTitle = data?.zone?.replace(/_/g, ' ').toUpperCase()

    const rows = data ? [
        {
            icon: '🌡️',
            label: 'Temperature',
            value: `${data.conditions.temperature}°C`,
            sub: `+${data.conditions.temperature_anomaly}°C above normal`
        },
        {
            icon: '💧',
            label: 'Dissolved Oxygen',
            value: `${data.conditions.oxygen} ml/L`,
            sub: data.conditions.oxygen < 4 ? 'Below safe threshold' : 'Normal range'
        },
        {
            icon: 'pH',
            label: 'pH Level',
            value: data.conditions.ph,
            sub: data.conditions.ph < 8 ? 'Acidification risk' : 'Normal range'
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
                    <span>Fetching ocean conditions…</span>
                </div>
            )}

            {!loading && data && (
                <div className="zdp-body">
                    {/* Coral bleaching alert */}
                    {data.coral_bleaching_alert && (
                        <div className="zdp-alert">
                            <div className="zdp-alert-icon">⚠️</div>
                            <div>
                                <p className="zdp-alert-title">CORAL BLEACHING ALERT</p>
                                <p className="zdp-alert-sub">
                                    Temperature {data.conditions.temperature_anomaly}°C above seasonal average
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Stress score */}
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
                                    strokeDashoffset={`${2 * Math.PI * 50 * (1 - data.stress_score / 100)}`}
                                    style={{
                                        transition: 'stroke-dashoffset 0.6s ease',
                                        filter: `drop-shadow(0 0 6px ${data.stress_color || '#00d4ff'})`
                                    }}
                                />
                            </svg>
                            <div className="zdp-score-center">
                                <span className="zdp-score-number">{data.stress_score}</span>
                                <span className="zdp-score-level" style={{ color: data.stress_color }}>{data.stress_level?.toUpperCase()}</span>
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
                    <div className="zdp-section-header">
                        <span>SPECIES AT RISK</span>
                        <div className="zdp-section-line" />
                    </div>
                    <div className="zdp-species-list">
                        {data.species_at_risk.map(species => (
                            <div key={species.name} className="zdp-species-card" style={{ '--risk-color': riskColors[species.risk] || '#a855f7' }}>
                                <div className="zdp-species-header">
                                    <strong className="zdp-species-name">{species.name}</strong>
                                    <span className="zdp-species-badge" style={{ background: riskColors[species.risk] || '#a855f7' }}>
                                        {(species.risk || 'high').toUpperCase()}
                                    </span>
                                </div>
                                <p className="zdp-species-note">{species.note}</p>
                                <p className="zdp-species-ngo">🤝 {species.ngo}</p>
                            </div>
                        ))}
                    </div>

                    {/* Footer */}
                    <div className="zdp-footer">
                        <span>Updated: May 20, 2025 · 10:30 AM</span>
                        <span>Source: WatchTheBlue</span>
                    </div>
                </div>
            )}
        </aside>
    )
}