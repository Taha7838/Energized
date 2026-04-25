import React, { useState } from 'react'

function Badge({ fromCache }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '5px',
      padding: '3px 10px',
      borderRadius: '20px',
      fontSize: '11px',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
      background: fromCache ? 'var(--cache-badge-light)' : 'var(--live-badge-light)',
      color: fromCache ? 'var(--cache-badge)' : 'var(--live-badge)',
    }}>
      {fromCache ? '⚡ Cached' : '🔴 Live'}
    </span>
  )
}

function MarkdownSection({ text }) {
  // Simple renderer: bold headers, bullet points, line breaks
  const lines = text.split('\n')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {lines.map((line, i) => {
        if (line.startsWith('## ')) {
          return <h3 key={i} style={styles.h3}>{line.replace('## ', '')}</h3>
        }
        if (line.startsWith('### ')) {
          return <h4 key={i} style={styles.h4}>{line.replace('### ', '')}</h4>
        }
        if (line.startsWith('# ')) {
          return <h2 key={i} style={styles.h2}>{line.replace('# ', '')}</h2>
        }
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return (
            <div key={i} style={styles.bullet}>
              <span style={styles.bulletDot}>•</span>
              <span>{line.replace(/^[-*] /, '')}</span>
            </div>
          )
        }
        if (/^\d+\.\s/.test(line)) {
          return (
            <div key={i} style={styles.bullet}>
              <span style={styles.bulletNum}>{line.match(/^(\d+)\./)[1]}.</span>
              <span>{line.replace(/^\d+\.\s/, '')}</span>
            </div>
          )
        }
        if (line.trim() === '') {
          return <div key={i} style={{ height: '8px' }} />
        }
        // Bold text **...** 
        const parts = line.split(/(\*\*[^*]+\*\*)/)
        return (
          <p key={i} style={styles.para}>
            {parts.map((part, j) =>
              part.startsWith('**') && part.endsWith('**')
                ? <strong key={j}>{part.slice(2, -2)}</strong>
                : part
            )}
          </p>
        )
      })}
    </div>
  )
}

export default function ResultDisplay({ result }) {
  const [sourcesExpanded, setSourcesExpanded] = useState(true)

  if (!result) return null

  const { query, summary, sources, timestamp, from_cache } = result
  const date = new Date(timestamp).toLocaleString()

  return (
    <div style={styles.card}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerTop}>
          <Badge fromCache={from_cache} />
          <span style={styles.timestamp}>{date}</span>
        </div>
        <h2 style={styles.query}>"{query}"</h2>
      </div>

      {/* Summary */}
      <div style={styles.body}>
        <MarkdownSection text={summary} />
      </div>

      {/* Sources */}
      {sources && sources.length > 0 && (
        <div style={styles.sourcesSection}>
          <button
            onClick={() => setSourcesExpanded(!sourcesExpanded)}
            style={styles.sourcesToggle}
          >
            <span>Sources ({sources.length})</span>
            <span style={{ transform: sourcesExpanded ? 'rotate(180deg)' : 'rotate(0)', transition: '0.2s', display: 'inline-block' }}>▾</span>
          </button>
          {sourcesExpanded && (
            <div style={styles.sourcesList}>
              {sources.map((src, i) => (
                <a
                  key={i}
                  href={src}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.sourceLink}
                >
                  <span style={styles.sourceNum}>[{i + 1}]</span>
                  <span style={styles.sourceUrl}>{src}</span>
                  <span style={styles.sourceArrow}>↗</span>
                </a>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const styles = {
  card: {
    background: 'var(--bg-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    boxShadow: 'var(--shadow)',
  },
  header: {
    padding: '20px 24px 16px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-tertiary)',
  },
  headerTop: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '10px',
  },
  timestamp: {
    fontSize: '12px',
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
  },
  query: {
    fontSize: '17px',
    fontWeight: 600,
    color: 'var(--text-primary)',
    lineHeight: '1.4',
  },
  body: {
    padding: '24px',
    color: 'var(--text-primary)',
    lineHeight: '1.7',
    fontSize: '14.5px',
  },
  h2: {
    fontSize: '20px',
    fontWeight: 700,
    color: 'var(--text-primary)',
    marginTop: '16px',
    marginBottom: '8px',
  },
  h3: {
    fontSize: '16px',
    fontWeight: 600,
    color: 'var(--text-primary)',
    marginTop: '16px',
    marginBottom: '6px',
    paddingBottom: '4px',
    borderBottom: '1px solid var(--border)',
  },
  h4: {
    fontSize: '14px',
    fontWeight: 600,
    color: 'var(--text-secondary)',
    marginTop: '12px',
    marginBottom: '4px',
  },
  para: {
    color: 'var(--text-primary)',
    lineHeight: '1.7',
  },
  bullet: {
    display: 'flex',
    gap: '8px',
    paddingLeft: '4px',
  },
  bulletDot: {
    color: 'var(--accent)',
    fontWeight: 700,
    flexShrink: 0,
    marginTop: '1px',
  },
  bulletNum: {
    color: 'var(--accent)',
    fontWeight: 700,
    flexShrink: 0,
    fontFamily: 'var(--font-mono)',
    fontSize: '13px',
    marginTop: '2px',
  },
  sourcesSection: {
    borderTop: '1px solid var(--border)',
    padding: '0',
  },
  sourcesToggle: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 24px',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--text-secondary)',
    fontFamily: 'var(--font-sans)',
    transition: 'background 0.15s',
  },
  sourcesList: {
    padding: '0 24px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  sourceLink: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '8px',
    textDecoration: 'none',
    padding: '6px 8px',
    borderRadius: 'var(--radius-sm)',
    transition: 'background 0.15s',
    background: 'var(--bg-tertiary)',
  },
  sourceNum: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    flexShrink: 0,
  },
  sourceUrl: {
    fontSize: '12px',
    color: 'var(--accent)',
    wordBreak: 'break-all',
    flex: 1,
  },
  sourceArrow: {
    fontSize: '11px',
    color: 'var(--text-muted)',
    flexShrink: 0,
  },
}
