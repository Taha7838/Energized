// agent/frontend/src/Landing.jsx

import React from 'react'
import { useNavigate } from 'react-router-dom'

const TOOLS = [
    {
        path: '/researcher',
        icon: '🔬',
        title: 'Energy Researcher',
        subtitle: 'Autonomous AI Research Agent',
        description:
            'Ask anything about the energy industry. The agent searches the web in real time, synthesizes findings from multiple sources, and returns a structured report with streaming progress.',
        accent: 'var(--accent)',
    },
    {
        path: '/rag',
        icon: '📄',
        title: 'EnergyRAG',
        subtitle: 'Document Q&A with Citations',
        description:
            'Upload your own energy industry PDFs. Ask questions and get answers grounded strictly in your documents — with exact page-level citations, no hallucinations.',
        accent: 'var(--success)',
    },
]

export default function Landing() {
    const navigate = useNavigate()

    return (
        <div style={styles.page}>
            <div style={styles.hero}>
                <div style={styles.heroIcon}>⚡</div>
                <h1 style={styles.heroTitle}>Energized</h1>
                <p style={styles.heroSub}>
                    AI-powered research tools for the energy industry
                </p>
            </div>

            <div style={styles.cards}>
                {TOOLS.map(tool => (
                    <button
                        key={tool.path}
                        onClick={() => navigate(tool.path)}
                        style={styles.card}
                    >
                        <div style={styles.cardIcon}>{tool.icon}</div>
                        <div style={{ ...styles.cardAccentBar, background: tool.accent }} />
                        <div style={styles.cardTitle}>{tool.title}</div>
                        <div style={styles.cardSubtitle}>{tool.subtitle}</div>
                        <p style={styles.cardDesc}>{tool.description}</p>
                        <div style={{ ...styles.cardCta, color: tool.accent }}>
                            Open →
                        </div>
                    </button>
                ))}
            </div>
        </div>
    )
}

const styles = {
    page: {
        minHeight: '100vh',
        background: 'var(--bg-primary)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 24px',
        gap: '48px',
    },
    hero: {
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '12px',
    },
    heroIcon: {
        fontSize: '56px',
        lineHeight: 1,
    },
    heroTitle: {
        fontSize: '40px',
        fontWeight: 800,
        color: 'var(--text-primary)',
        margin: 0,
        letterSpacing: '-0.02em',
    },
    heroSub: {
        fontSize: '16px',
        color: 'var(--text-muted)',
        margin: 0,
        maxWidth: '400px',
        lineHeight: '1.6',
    },
    cards: {
        display: 'flex',
        gap: '24px',
        flexWrap: 'wrap',
        justifyContent: 'center',
        width: '100%',
        maxWidth: '800px',
    },
    card: {
        flex: '1 1 320px',
        maxWidth: '360px',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        borderRadius: '16px',
        padding: '32px',
        cursor: 'pointer',
        textAlign: 'left',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        transition: 'transform 0.15s, box-shadow 0.15s',
        boxShadow: 'var(--shadow)',
        position: 'relative',
        overflow: 'hidden',
    },
    cardIcon: {
        fontSize: '36px',
        lineHeight: 1,
        marginBottom: '4px',
    },
    cardAccentBar: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        borderRadius: '16px 16px 0 0',
    },
    cardTitle: {
        fontSize: '18px',
        fontWeight: 700,
        color: 'var(--text-primary)',
    },
    cardSubtitle: {
        fontSize: '12px',
        color: 'var(--text-muted)',
        fontWeight: 500,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
    },
    cardDesc: {
        fontSize: '14px',
        color: 'var(--text-secondary)',
        lineHeight: '1.7',
        margin: '8px 0 0',
        flex: 1,
    },
    cardCta: {
        fontSize: '14px',
        fontWeight: 600,
        marginTop: '16px',
    },
}