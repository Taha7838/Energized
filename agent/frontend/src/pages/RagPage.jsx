// agent/frontend/src/pages/RagPage.jsx

import React, { useState, useEffect } from 'react'

const RAG_BASE = '/rag/api'

async function uploadPDF(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${RAG_BASE}/upload`, { method: 'POST', body: formData })
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Upload failed')
    }
    return res.json()
}

async function fetchDocuments() {
    const res = await fetch(`${RAG_BASE}/documents`)
    if (!res.ok) throw new Error('Failed to fetch documents')
    return res.json()
}

async function deleteDocument(docName) {
    const res = await fetch(`${RAG_BASE}/documents/${encodeURIComponent(docName)}`, { method: 'DELETE' })
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Delete failed')
    }
    return res.json()
}

async function queryRAG(question, topK = 5) {
    const res = await fetch(`${RAG_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, top_k: topK }),
    })
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(err.detail || 'Query failed')
    }
    return res.json()
}

export default function RagPage() {
    const [documents, setDocuments] = useState([])
    const [docsLoading, setDocsLoading] = useState(true)
    const [docsError, setDocsError] = useState(null)

    const [uploading, setUploading] = useState(false)
    const [uploadMsg, setUploadMsg] = useState(null)  // { type: 'success'|'error', text: string }

    const [question, setQuestion] = useState('')
    const [querying, setQuerying] = useState(false)
    const [queryResult, setQueryResult] = useState(null)
    const [queryError, setQueryError] = useState(null)

    const [deletingDoc, setDeletingDoc] = useState(null)

    const loadDocuments = async () => {
        setDocsLoading(true)
        setDocsError(null)
        try {
            const data = await fetchDocuments()
            setDocuments(data.documents || [])
        } catch (e) {
            setDocsError(e.message)
        } finally {
            setDocsLoading(false)
        }
    }

    useEffect(() => {
        loadDocuments()
    }, [])

    const handleUpload = async (e) => {
        const file = e.target.files?.[0]
        if (!file) return
        // Reset input so same file can be re-uploaded after deletion
        e.target.value = ''

        setUploading(true)
        setUploadMsg(null)
        try {
            const result = await uploadPDF(file)
            setUploadMsg({
                type: 'success',
                text: `✅ Ingested "${result.doc_name}" — ${result.chunks_added} chunks added.`,
            })
            await loadDocuments()
        } catch (e) {
            setUploadMsg({ type: 'error', text: `❌ ${e.message}` })
        } finally {
            setUploading(false)
        }
    }

    const handleDelete = async (docName) => {
        setDeletingDoc(docName)
        try {
            await deleteDocument(docName)
            setDocuments(prev => prev.filter(d => d !== docName))
            // Clear results if they were from this doc
            setQueryResult(null)
        } catch (e) {
            alert(`Delete failed: ${e.message}`)
        } finally {
            setDeletingDoc(null)
        }
    }

    const handleQuery = async (e) => {
        e.preventDefault()
        const q = question.trim()
        if (!q) return

        setQuerying(true)
        setQueryResult(null)
        setQueryError(null)
        try {
            const data = await queryRAG(q)
            setQueryResult(data)
        } catch (e) {
            setQueryError(e.message)
        } finally {
            setQuerying(false)
        }
    }

    return (
        <div style={styles.page}>
            {/* Header */}
            <header style={styles.header}>
                <div style={styles.logo}>
                    <span style={styles.logoIcon}>📄</span>
                    <div>
                        <div style={styles.logoTitle}>EnergyRAG</div>
                        <div style={styles.logoSub}>Document Q&amp;A with Citations</div>
                    </div>
                </div>
                <div style={styles.statusDot} title="Backend connected" />
            </header>

            <div style={styles.layout}>
                {/* Sidebar — document list */}
                <aside style={styles.sidebar}>
                    <div style={styles.sidebarHeader}>
                        <span style={styles.sidebarTitle}>Indexed Documents</span>
                        <label style={styles.uploadBtn} title="Upload PDF">
                            {uploading ? '⏳' : '+ Upload'}
                            <input
                                type="file"
                                accept=".pdf"
                                onChange={handleUpload}
                                disabled={uploading}
                                style={{ display: 'none' }}
                            />
                        </label>
                    </div>

                    {uploadMsg && (
                        <div style={{
                            ...styles.uploadMsg,
                            borderColor: uploadMsg.type === 'success' ? 'var(--success)' : 'var(--error)',
                            color: uploadMsg.type === 'success' ? 'var(--success)' : 'var(--error)',
                        }}>
                            {uploadMsg.text}
                        </div>
                    )}

                    {docsError && (
                        <div style={{ ...styles.uploadMsg, borderColor: 'var(--error)', color: 'var(--error)' }}>
                            {docsError}
                        </div>
                    )}

                    <div style={styles.docList}>
                        {docsLoading ? (
                            <div style={styles.docEmpty}>Loading...</div>
                        ) : documents.length === 0 ? (
                            <div style={styles.docEmpty}>No documents indexed yet. Upload a PDF to get started.</div>
                        ) : (
                            documents.map(doc => (
                                <div key={doc} style={styles.docItem}>
                                    <span style={styles.docName} title={doc}>📄 {doc}</span>
                                    <button
                                        onClick={() => handleDelete(doc)}
                                        disabled={deletingDoc === doc}
                                        style={styles.deleteBtn}
                                        title="Delete document"
                                    >
                                        {deletingDoc === doc ? '...' : '✕'}
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </aside>

                {/* Main — query */}
                <main style={styles.main}>
                    <form onSubmit={handleQuery} style={styles.queryForm}>
                        <textarea
                            value={question}
                            onChange={e => setQuestion(e.target.value)}
                            placeholder="Ask a question about your uploaded documents..."
                            style={styles.textarea}
                            rows={3}
                            disabled={querying}
                            onKeyDown={e => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleQuery(e)
                                }
                            }}
                        />
                        <button
                            type="submit"
                            disabled={querying || !question.trim()}
                            style={styles.submitBtn}
                        >
                            {querying ? 'Searching...' : 'Ask'}
                        </button>
                    </form>

                    {queryError && (
                        <div style={styles.errorBanner}>
                            <strong>Error:</strong> {queryError}
                        </div>
                    )}

                    {queryResult && (
                        <div style={styles.resultCard}>
                            <div style={styles.answerText}>{queryResult.answer}</div>

                            {queryResult.sources?.length > 0 && (
                                <div style={styles.sourcesSection}>
                                    <div style={styles.sourcesTitle}>Sources</div>
                                    <div style={styles.sourcesList}>
                                        {queryResult.sources.map((src, i) => (
                                            <div key={i} style={styles.sourceTag}>
                                                📎 {src.doc_name} — Page {src.page_no}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {!queryResult && !querying && !queryError && (
                        <div style={styles.emptyState}>
                            <div style={styles.emptyIcon}>📚</div>
                            <h3 style={styles.emptyTitle}>Ask your documents</h3>
                            <p style={styles.emptyText}>
                                Upload one or more energy industry PDFs, then ask questions.
                                Answers are grounded strictly in your documents with page-level citations.
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
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-secondary)',
    },
    sidebarHeader: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
        borderBottom: '1px solid var(--border)',
    },
    sidebarTitle: {
        fontSize: '12px',
        fontWeight: 600,
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
    },
    uploadBtn: {
        fontSize: '12px',
        fontWeight: 600,
        color: 'var(--accent)',
        cursor: 'pointer',
        padding: '4px 10px',
        borderRadius: '6px',
        border: '1px solid var(--accent)',
        background: 'transparent',
        transition: 'background 0.15s',
        userSelect: 'none',
    },
    uploadMsg: {
        margin: '8px 12px',
        padding: '8px 12px',
        borderRadius: '6px',
        border: '1px solid',
        fontSize: '12px',
        lineHeight: '1.5',
    },
    docList: {
        flex: 1,
        overflowY: 'auto',
        padding: '8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
    },
    docEmpty: {
        fontSize: '13px',
        color: 'var(--text-muted)',
        padding: '16px',
        textAlign: 'center',
        lineHeight: '1.6',
    },
    docItem: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 10px',
        borderRadius: '6px',
        background: 'var(--bg-tertiary)',
        gap: '8px',
    },
    docName: {
        fontSize: '13px',
        color: 'var(--text-primary)',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        flex: 1,
    },
    deleteBtn: {
        background: 'transparent',
        border: 'none',
        color: 'var(--text-muted)',
        cursor: 'pointer',
        fontSize: '12px',
        padding: '2px 6px',
        borderRadius: '4px',
        flexShrink: 0,
    },
    main: {
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
    },
    queryForm: {
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-start',
    },
    textarea: {
        flex: 1,
        padding: '12px 16px',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
        background: 'var(--bg-secondary)',
        color: 'var(--text-primary)',
        fontSize: '14px',
        resize: 'vertical',
        fontFamily: 'inherit',
        lineHeight: '1.5',
        outline: 'none',
    },
    submitBtn: {
        padding: '12px 24px',
        borderRadius: 'var(--radius)',
        border: 'none',
        background: 'var(--accent)',
        color: '#fff',
        fontSize: '14px',
        fontWeight: 600,
        cursor: 'pointer',
        flexShrink: 0,
        alignSelf: 'flex-end',
    },
    errorBanner: {
        background: 'var(--error-light)',
        border: '1px solid var(--error)',
        borderRadius: 'var(--radius)',
        padding: '12px 16px',
        fontSize: '13px',
        color: 'var(--error)',
    },
    resultCard: {
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        animation: 'slideIn 0.3s ease',
    },
    answerText: {
        fontSize: '14px',
        color: 'var(--text-primary)',
        lineHeight: '1.8',
        whiteSpace: 'pre-wrap',
    },
    sourcesSection: {
        borderTop: '1px solid var(--border)',
        paddingTop: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    },
    sourcesTitle: {
        fontSize: '11px',
        fontWeight: 600,
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
    },
    sourcesList: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
    },
    sourceTag: {
        fontSize: '12px',
        color: 'var(--text-secondary)',
        background: 'var(--bg-tertiary)',
        padding: '4px 10px',
        borderRadius: '20px',
        border: '1px solid var(--border)',
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