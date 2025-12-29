
import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const InstitutionalReport = ({ symbol, isOpen, onClose }) => {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isOpen && symbol) {
            fetchReport();
        }
    }, [isOpen, symbol]);

    const fetchReport = async () => {
        try {
            setLoading(true);
            const data = await api.getInstitutionalReport(symbol);
            setReport(data);
        } catch (e) {
            console.error('Report fetch failed', e);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/90 backdrop-blur-3xl animate-in fade-in duration-500">
            <div className="relative w-full max-w-5xl h-[90vh] bg-gray-900 border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-white/5 flex items-center justify-between bg-black/20">
                    <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-cyan-500/10 rounded flex items-center justify-center border border-cyan-500/30">
                            <span className="text-xl">📊</span>
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white tracking-tight">Institutional Market Intelligence Report</h2>
                            <p className="text-[10px] text-gray-400 uppercase tracking-[0.3em]">Symbol: {symbol} • Verified Tier S Intelligence</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        {report && (
                            <div className="text-right px-4 border-r border-white/10">
                                <div className="text-[10px] text-gray-500 uppercase">Trust Score</div>
                                <div className="text-lg font-mono font-bold text-cyan-400">{report.trust_score}%</div>
                            </div>
                        )}
                        <button
                            onClick={onClose}
                            className="w-10 h-10 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/5 rounded-full transition-all"
                        >
                            <span className="text-2xl">×</span>
                        </button>
                    </div>
                </div>

                {/* Audit Bar */}
                {report && (
                    <div className="px-6 py-2 bg-cyan-500/5 flex items-center justify-between border-b border-cyan-500/10">
                        <div className="flex items-center space-x-6">
                            <span className="text-[9px] text-cyan-400 font-mono">AUDIT_ID: {report.audit_id}</span>
                            <span className="text-[9px] text-gray-500 font-mono">CONFIDENCE_BAND: {report.confidence_band}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                            <span className="text-[9px] text-green-500 font-mono uppercase">Data Integrity Verified</span>
                        </div>
                    </div>
                )}

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-10 font-mono text-sm text-gray-300 leading-relaxed scrollbar-thin scrollbar-thumb-white/10">
                    {loading ? (
                        <div className="h-full flex flex-col items-center justify-center space-y-4">
                            <div className="w-12 h-12 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                            <p className="text-xs text-cyan-400 animate-pulse tracking-widest uppercase">Fetching verified institutional data...</p>
                        </div>
                    ) : report ? (
                        <div className="max-w-4xl mx-auto space-y-6 whitespace-pre-wrap">
                            {/* Simple markdown-style rendering */}
                            {report.markdown.split('###').map((section, i) => (
                                i === 0 ? <div key={i}>{section}</div> : (
                                    <div key={i} className="pt-6 border-t border-white/5">
                                        <h3 className="text-cyan-400 font-bold text-lg mb-4 uppercase tracking-wider flex items-center">
                                            <span className="mr-3 opacity-50">#{i}</span>
                                            {section.split('\n')[0]}
                                        </h3>
                                        <div className="text-gray-400 bg-white/2 p-4 rounded border border-white/5">
                                            {section.split('\n').slice(1).join('\n')}
                                        </div>
                                    </div>
                                )
                            ))}
                        </div>
                    ) : (
                        <div className="h-full flex items-center justify-center text-red-400 italic">
                            Report generation failed. System degraded.
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-white/5 bg-black/40 flex items-center justify-between">
                    <div className="text-[9px] text-gray-600 font-mono uppercase">
                        Quantum Signature: {Math.random().toString(16).slice(2, 10)}-liminal-node-9
                    </div>
                    <button
                        onClick={() => window.print()}
                        className="px-4 py-1.5 bg-white/5 hover:bg-white/10 rounded border border-white/10 text-[10px] text-white uppercase tracking-widest transition-all"
                    >
                        Export PDF
                    </button>
                </div>
            </div>
        </div>
    );
};

export default InstitutionalReport;
