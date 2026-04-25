import React, { useEffect, useRef } from 'react'

export default function StreamingIndicator({ messages, isStreaming }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!isStreaming && messages.length === 0) return null

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          {isStreaming && <span style={styles.pulse} />}
          <span style={styles.label}>
            {isStreaming ? 'Agent is working...' : 'Agent log'}
          </span>
        </div>
        <span style={styles.count}>{messages.length} steps</span>
      </div>
      <div style={styles.log}>
        {messages.map((msg, i) => (
          <div key={i} style={styles.logLine}>
            <span style={styles.lineNum}>{String(i + 1).padStart(2, '0')}</span>
            <span style={styles.lineText}>{msg}</span>
          </div>
        ))}
        {isStreaming && (
          <div style={styles.cursor}>
            <span style={styles.lineNum}>{'  '}</span>
            <span style={styles.blinkCursor}>▋</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

const styles = {
  container: {
    background: 'var(--stream-bg)',
    border: '1px solid var(--stream-border)',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    boxShadow: 'var(--shadow)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 14px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--bg-secondary)',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  pulse: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'var(--stream-border)',
    animation: 'pulse 1.2s ease-in-out infinite',
    display: 'inline-block',
  },
  label: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--stream-text)',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  count: {
    fontSize: '11px',
    color: 'var(--text-muted)',
    fontFamily: 'var(--font-mono)',
  },
  log: {
    padding: '12px 14px',
    maxHeight: '280px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  logLine: {
    display: 'flex',
    gap: '12px',
    alignItems: 'flex-start',
    animation: 'fadeIn 0.2s ease',
  },
  lineNum: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    flexShrink: 0,
    marginTop: '2px',
    minWidth: '20px',
  },
  lineText: {
    fontFamily: 'var(--font-mono)',
    fontSize: '12px',
    color: 'var(--stream-text)',
    lineHeight: '1.6',
    wordBreak: 'break-word',
  },
  cursor: {
    display: 'flex',
    gap: '12px',
  },
  blinkCursor: {
    fontFamily: 'var(--font-mono)',
    fontSize: '14px',
    color: 'var(--stream-border)',
    animation: 'blink 1s step-end infinite',
  },
}
