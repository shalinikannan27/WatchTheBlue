export default function ZonePanel({ data, loading, onClose }) {
    const riskColors = { low: '#22c55e', moderate: '#facc15', high: '#a855f7', critical: '#ef4444' }
    const zoneTitle = data?.zone?.replace(/_/g, ' ').toUpperCase()

    const rows = data ? [
        { icon: '🌡', label: 'Temperature', value: `${data.conditions.temperature}°C`, sub: `+${data.conditions.temperature_anomaly}°C above normal` },
        { icon: '💧', label: 'Dissolved Oxygen', value: `${data.conditions.oxygen} ml/L`, sub: data.conditions.oxygen < 4 ? 'Below safe threshold' : 'Normal range' },
        { icon: 'pH', label: 'pH Level', value: data.conditions.ph, sub: data.conditions.ph < 8 ? 'Acidification risk' : 'Normal range' }
    ] : []

    return (
        <aside className="ref-panel">
            <button onClick={onClose} className="ref-close">✕</button>
            <h2 className="ref-title">{zoneTitle || 'LOADING ZONE'}</h2>

            {loading && <p className="ref-loading">Fetching ocean conditions...</p>}

            {!loading && data && (
                <>
                    {data.coral_bleaching_alert && (
                        <div className="ref-alert">
                            <p className="ref-alert-title">CORAL BLEACHING ALERT</p>
                            <p className="ref-alert-sub">Temperature {data.conditions.temperature_anomaly}°C above seasonal average</p>
                        </div>
                    )}

                    <div className="ref-score-card">
                        <p>OCEAN STRESS SCORE</p>
                        <h3>{data.stress_score}</h3>
                        <span>{data.stress_level}</span>
                    </div>

                    <p className="ref-section">CURRENT CONDITIONS</p>
                    <div className="ref-rows">
                        {rows.map((item) => (
                            <div key={item.label} className="ref-row">
                                <div>
                                    <p className="ref-row-title">{item.icon} {item.label}</p>
                                    <p className="ref-row-sub">{item.sub}</p>
                                </div>
                                <strong>{item.value}</strong>
                            </div>
                        ))}
                    </div>

                    <p className="ref-section">SPECIES AT RISK</p>
                    <div className="ref-species-list">
                        {data.species_at_risk.map((species) => (
                            <div key={species.name} className="ref-species">
                                <div className="ref-species-top">
                                    <p className="ref-species-name">{species.name}</p>
                                    <span className="ref-badge" style={{ background: riskColors[species.risk] || '#a855f7' }}>
                                        {(species.risk || 'high').toUpperCase()}
                                    </span>
                                </div>
                                <p className="ref-species-note">{species.note}</p>
                                <p className="ref-species-ngo">{species.ngo}</p>
                            </div>
                        ))}
                    </div>

                    <div className="ref-footer">
                        <span>Data updated: May 20, 2025 10:30 AM</span>
                        <span>Source: WatchTheBlue</span>
                    </div>
                </>
            )}
        </aside>
    )
}