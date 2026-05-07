import React, { useEffect, useState } from 'react'
import { getHistory } from '../api/client'

export default function HistoryPanel({ onSelect, currentQuery }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      const items = await getHistory()
      setHistory(items)
    } catch {
      setError('Failed to load history.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [currentQuery]) // refetch when a new query completes

  return (
    <div style={styles.panel}>
      <div style={styles.header}>
        <span style={styles.title}>History</span>
        <button onClick={fetchHistory} style={styles.refreshBtn} title="Refresh">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
        </button>
      </div>

      <div style={styles.list}>
        {loading && (
          <p style={styles.stateMsg}>Loading...</p>
        )}
        {error && (
          <p style={{ ...styles.stateMsg, color: 'var(--error)' }}>{error}</p>
        )}
        {!loading && !error && history.length === 0 && (
          <p style={styles.stateMsg}>No history yet. Run a query!</p>
        )}
        {!loading && history.map((item, i) => (
          <button
            key={i}
            onClick={() => onSelect(item)}
            style={{
              ...styles.item,
              background: currentQuery === item.query
                ? 'var(--accent-light)'
                : 'transparent',
              borderColor: currentQuery === item.query
                ? 'var(--accent)'
                : 'transparent',
            }}
          >
            <div style={styles.itemQuery}>{item.query}</div>
            <div style={styles.itemMeta}>
              <span style={{
                ...styles.badge,
                background: item.from_cache ? 'var(--cache-badge-light)' : 'var(--live-badge-light)',
                color: item.from_cache ? 'var(--cache-badge)' : 'var(--live-badge)',
              }}>
                {item.from_cache ? '⚡' : '🔴'}
              </span>
              <span style={styles.itemDate}>
                {new Date(item.timestamp).toLocaleDateString()}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

const styles = {
  panel: {
    background: 'var(--bg-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    boxShadow: 'var(--shadow)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 16px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-tertiary)',
  },
  title: {
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--text-secondary)',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  refreshBtn: {
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    color: 'var(--text-muted)',
    padding: '4px',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'color 0.15s',
  },
  list: {
    flex: 1,
    overflowY: 'auto',
    padding: '8px',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  stateMsg: {
    fontSize: '12px',
    color: 'var(--text-muted)',
    textAlign: 'center',
    padding: '24px 16px',
  },
  item: {
    width: '100%',
    textAlign: 'left',
    background: 'transparent',
    border: '1px solid transparent',
    borderRadius: 'var(--radius-sm)',
    padding: '10px 12px',
    cursor: 'pointer',
    fontFamily: 'var(--font-sans)',
    transition: 'background 0.15s, border-color 0.15s',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  itemQuery: {
    fontSize: '13px',
    color: 'var(--text-primary)',
    fontWeight: 500,
    lineHeight: '1.4',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  itemMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  badge: {
    fontSize: '10px',
    padding: '1px 6px',
    borderRadius: '10px',
    fontWeight: 600,
  },
  itemDate: {
    fontSize: '11px',
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
  },
}
