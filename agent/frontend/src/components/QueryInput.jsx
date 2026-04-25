import React, { useState, useRef } from 'react'

const EXAMPLE_QUERIES = [
  'Latest trends in offshore wind energy',
  'Global solar panel manufacturing capacity 2024',
  'Nuclear energy renaissance: new reactor projects worldwide',
  'LNG market outlook and pricing trends',
  'Grid-scale battery storage developments',
]

export default function QueryInput({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('')
  const textareaRef = useRef(null)

  const handleSubmit = () => {
    const trimmed = query.trim()
    if (!trimmed || isLoading) return
    onSubmit(trimmed)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleExample = (example) => {
    setQuery(example)
    textareaRef.current?.focus()
  }

  return (
    <div style={styles.wrapper}>
      <div style={styles.inputCard}>
        <div style={styles.inputRow}>
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about the energy industry..."
            disabled={isLoading}
            rows={2}
            style={styles.textarea}
          />
          <button
            onClick={handleSubmit}
            disabled={isLoading || !query.trim()}
            style={{
              ...styles.button,
              opacity: isLoading || !query.trim() ? 0.5 : 1,
              cursor: isLoading || !query.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            {isLoading ? (
              <span style={styles.buttonSpinner} />
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>
        <p style={styles.hint}>Press Enter to search · Shift+Enter for new line</p>
      </div>

      <div style={styles.examples}>
        <span style={styles.examplesLabel}>Try:</span>
        {EXAMPLE_QUERIES.map((ex) => (
          <button
            key={ex}
            onClick={() => handleExample(ex)}
            disabled={isLoading}
            style={styles.exampleChip}
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  inputCard: {
    background: 'var(--bg-secondary)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '12px',
    boxShadow: 'var(--shadow)',
    transition: 'border-color 0.2s',
  },
  inputRow: {
    display: 'flex',
    gap: '10px',
    alignItems: 'flex-end',
  },
  textarea: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    outline: 'none',
    resize: 'none',
    fontFamily: 'var(--font-sans)',
    fontSize: '15px',
    color: 'var(--text-primary)',
    lineHeight: '1.6',
    padding: '4px 0',
  },
  button: {
    width: '44px',
    height: '44px',
    borderRadius: 'var(--radius-sm)',
    background: 'var(--accent)',
    border: 'none',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'background 0.2s, opacity 0.2s',
  },
  buttonSpinner: {
    width: '18px',
    height: '18px',
    border: '2px solid rgba(255,255,255,0.3)',
    borderTop: '2px solid #fff',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
    display: 'inline-block',
  },
  hint: {
    marginTop: '8px',
    fontSize: '12px',
    color: 'var(--text-muted)',
  },
  examples: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    alignItems: 'center',
  },
  examplesLabel: {
    fontSize: '12px',
    color: 'var(--text-muted)',
    fontWeight: 500,
  },
  exampleChip: {
    background: 'var(--bg-tertiary)',
    border: '1px solid var(--border)',
    borderRadius: '20px',
    padding: '4px 12px',
    fontSize: '12px',
    color: 'var(--text-secondary)',
    cursor: 'pointer',
    fontFamily: 'var(--font-sans)',
    transition: 'background 0.15s, color 0.15s',
    whiteSpace: 'nowrap',
  },
}
