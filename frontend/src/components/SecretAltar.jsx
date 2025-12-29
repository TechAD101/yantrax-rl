import React, { useState, useEffect } from 'react';
import { BASE_URL } from '../api/api';

const SecretAltar = ({ isOpen, onClose }) => {
    const [wisdom, setWisdom] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isOpen) {
            fetchWisdom();
        }
    }, [isOpen]);

    const fetchWisdom = async () => {
        try {
            setLoading(true);
            const resp = await fetch(`${BASE_URL}/api/knowledge/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: 'legendary', max_results: 10 })
            });
            if (resp.ok) {
                const data = await resp.json();
                setWisdom(data.wisdom || []);
            }
        } catch (e) {
            console.error('Altar fetch failed', e);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-2xl animate-in fade-in duration-700">
            <div className="relative w-full max-w-4xl max-h-[80vh] overflow-hidden bg-gray-900/50 border border-purple-500/30 rounded-3xl shadow-[0_0_50px_rgba(168,85,247,0.2)] p-8">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>

                <button
                    onClick={onClose}
                    className="absolute top-4 right-6 text-gray-500 hover:text-white transition-colors text-2xl"
                >
                    ×
                </button>

                <div className="flex flex-col items-center text-center mb-12">
                    <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mb-4 border border-purple-500/50 animate-pulse">
                        <span className="text-3xl">👁️</span>
                    </div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent uppercase tracking-[0.5em]">
                        Akasha Node
                    </h2>
                    <p className="text-xs text-purple-400 font-mono mt-2">ACCESSING INSTITUTIONAL QUANTUM MEMORY</p>
                </div>

                <div className="overflow-y-auto pr-4 space-y-8 max-h-[50vh] scrollbar-thin scrollbar-thumb-purple-500/20">
                    {loading ? (
                        <div className="flex justify-center py-20">
                            <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : wisdom.length > 0 ? (
                        wisdom.map((item, i) => (
                            <div key={i} className="group relative">
                                <div className="absolute -left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500/50 to-transparent group-hover:from-purple-400 transition-all"></div>
                                <div className="text-xs text-purple-500 font-mono mb-2">FRAGMENT #{i.toString().padStart(3, '0')} • {item.metadata?.archetype?.toUpperCase() || 'LORE'}</div>
                                <p className="text-xl text-gray-200 font-serif italic leading-relaxed">
                                    "{item.text}"
                                </p>
                                <div className="mt-2 text-[10px] text-gray-500 uppercase tracking-widest">— Source: {item.metadata?.source || 'The Void'}</div>
                            </div>
                        ))
                    ) : (
                        <p className="text-center text-gray-500 italic">No lore fragments found in this sector.</p>
                    )}
                </div>

                <div className="mt-12 pt-6 border-t border-white/5 flex justify-between items-center text-[10px] text-gray-600 font-mono uppercase tracking-widest">
                    <span>Connection: Secure</span>
                    <span>Divine Doubt Registry: ACTIVE</span>
                    <span>Ghost Protocol: SILENT</span>
                </div>
            </div>
        </div>
    );
};

export default SecretAltar;
