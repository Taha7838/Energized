// agent/frontend/src/pages/ResearcherPage.jsx

import React, { useState, useRef } from 'react'
import QueryInput from '../components/QueryInput'
import ResultDisplay from '../components/ResultDisplay'
import StreamingIndicator from '../components/StreamingIndicator'
import HistoryPanel from '../components/HistoryPanel'
import { streamQuery, postQuery } from '../api/client'

export default function ResearcherPage() {
    const [isLoading, setIsLoading] = useState(false)
    const [streamMessages, setStreamMessages] = useState([])
    const [isStreaming, setIsStreaming] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [currentQuery, setCurrentQuery] = useState('')

    const esRef = useRef(null)

    const handleSubmit = async (query) => {
        if (esRef.current) {
            esRef.current.close()
            esRef.current = null
        }

        setCurrentQuery(query)
        setIsLoading(true)
        setIsStreaming(true)
        setStreamMessages([])
        setResult(null)
        setError(null)

        try {
            const es = streamQuery(query, {
                onProgress: (msg) => {
                    setStreamMessages(prev => [...prev, msg])
                },
                onResult: (data) => {
                    setResult(data)
                },
                onError: (errMsg) => {
                    console.warn('[SSE] Error, falling back to POST:', errMsg)
                    setStreamMessages(prev => [...prev, '⚠️ Streaming failed. Falling back to standard request...'])
                    postQuery(query)
                        .then(data => setResult(data))
                        .catch(e => setError(`Request failed: ${e.message}`))
                        .finally(() => {
                            setIsLoading(false)
                            setIsStreaming(false)
                        })
                },
                onDone: () => {
                    setIsLoading(false)
                    setIsStreaming(false)
                    esRef.current = null
                },
            })
            esRef.current = es
        } catch (e) {
            setError(`Failed to connect: ${e.message}`)
            setIsLoading(false)
            setIsStreaming(false)
        }
    }

    const handleHistorySelect = (item) => {
        setCurrentQuery(item.query)
        setResult(item)
        setStreamMessages([])
        setIsStreaming(false)
        setError(null)
    }

    return (
        <div style={styles.page}>
            {/* Header */}
            <header style={styles.header}>
                <div style={styles.logo}>
                    <span style={styles.logoIcon}>⚡</span>
                    <div>
                        <div style={styles.logoTitle}>Energy Researcher</div>
                        <div style={styles.logoSub}>Autonomous AI Research Agent</div>
                    </div>
                </div>
                <div style={styles.statusDot} title="Backend connected" />
            </header>

            {/* Body */}
            <div style={styles.layout}>
                <aside style={styles.sidebar}>
                    <HistoryPanel onSelect={handleHistorySelect} currentQuery={currentQuery} />
                </aside>

                <main style={styles.main}>
                    <QueryInput onSubmit={handleSubmit} isLoading={isLoading} />

                    {error && (
                        <div style={styles.errorBanner}>
                            <strong>Error:</strong> {error}
                        </div>
                    )}

                    {(isStreaming || streamMessages.length > 0) && (
                        <div style={{ animation: 'slideIn 0.3s ease' }}>
                            <StreamingIndicator messages={streamMessages} isStreaming={isStreaming} />
                        </div>
                    )}

                    {result && !isStreaming && (
                        <div style={{ animation: 'slideIn 0.3s ease' }}>
                            <ResultDisplay result={result} />
                        </div>
                    )}

                    {!result && !isLoading && !error && (
                        <div style={styles.emptyState}>
                            <div style={styles.emptyIcon}>🔬</div>
                            <h3 style={styles.emptyTitle}>Ready to research</h3>
                            <p style={styles.emptyText}>
                                Ask anything about the energy industry. The agent will search the web,
                                synthesize findings from multiple sources, and return a structured report.
                                Results are cached so repeated queries return instantly.
                            </p>
                        </div>
                    )}
                </main>
            </div>
        </div>
    )
}

const styles = {
    page: {
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-primary)',
        overflow: 'hidden',
    },
    header: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        height: '60px',
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border)',
        flexShrink: 0,
        boxShadow: 'var(--shadow)',
        zIndex: 10,
    },
    logo: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    logoIcon: {
        fontSize: '24px',
    },
    logoTitle: {
        fontSize: '15px',
        fontWeight: 700,
        color: 'var(--text-primary)',
        lineHeight: '1.2',
    },
    logoSub: {
        fontSize: '11px',
        color: 'var(--text-muted)',
        fontWeight: 400,
    },
    statusDot: {
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        background: 'var(--success)',
    },
    layout: {
        flex: 1,
        display: 'flex',
        overflow: 'hidden',
    },
    sidebar: {
        width: '280px',
        flexShrink: 0,
        borderRight: '1px solid var(--border)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
    },
    main: {
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
    },
    errorBanner: {
        background: 'var(--error-light)',
        border: '1px solid var(--error)',
        borderRadius: 'var(--radius)',
        padding: '12px 16px',
        fontSize: '13px',
        color: 'var(--error)',
        animation: 'slideIn 0.3s ease',
    },
    emptyState: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '60px 40px',
        gap: '12px',
    },
    emptyIcon: {
        fontSize: '48px',
        marginBottom: '8px',
    },
    emptyTitle: {
        fontSize: '20px',
        fontWeight: 600,
        color: 'var(--text-primary)',
    },
    emptyText: {
        fontSize: '14px',
        color: 'var(--text-muted)',
        maxWidth: '480px',
        lineHeight: '1.7',
    },
}