import React, { useState, useEffect } from 'react';

/**
 * WisdomOracle - God Mode Vision
 * Displays the "Divine Whisper" from the Gemini-powered Oracle service.
 * Features a high-end, mystical yet surgical aesthetic.
 */
const WisdomOracle = ({ wisdom = null, loading = false }) => {
  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (wisdom?.text) {
      setIsTyping(true);
      setDisplayText('');
      let i = 0;
      const text = wisdom.text;
      const interval = setInterval(() => {
        setDisplayText(prev => prev + text[i]);
        i++;
        if (i >= text.length) {
          clearInterval(interval);
          setIsTyping(false);
        }
      }, 30);
      return () => clearInterval(interval);
    }
  }, [wisdom]);

  return (
    <div className="surgical-panel p-8 relative overflow-hidden min-h-[220px] flex flex-col justify-center">
      {/* Mystical Background Aura */}
      <div className="absolute -top-24 -right-24 w-64 h-64 bg-[var(--color-aura-blue)] opacity-[0.03] blur-[100px] rounded-full pointer-events-none"></div>
      
      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-1 h-5 bg-[var(--border-gold)] shadow-[0_0_10px_rgba(212,175,55,0.3)]"></div>
          <h4 className="text-[11px] font-mono font-bold text-[var(--border-gold)] uppercase tracking-[0.4em]">
            Divine Whisper // Gemini Oracle
          </h4>
          {loading && (
            <div className="ml-auto flex gap-1">
              <div className="w-1 h-1 bg-[var(--border-gold)] animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-1 h-1 bg-[var(--border-gold)] animate-bounce" style={{ animationDelay: '200ms' }}></div>
              <div className="w-1 h-1 bg-[var(--border-gold)] animate-bounce" style={{ animationDelay: '400ms' }}></div>
            </div>
          )}
        </div>

        {!loading && wisdom ? (
          <div className="space-y-6">
            <div className="relative">
              <span className="absolute -left-6 top-0 text-4xl text-white/5 font-serif">"</span>
              <p className="text-2xl text-[var(--text-primary)] leading-tight font-serif italic tracking-tight">
                {displayText}
                {isTyping && <span className="inline-block w-1.5 h-6 ml-1 bg-[var(--color-aura-blue)] animate-pulse align-middle"></span>}
              </p>
            </div>
            
            <div className="flex items-center justify-between mt-8 pt-4 border-t border-white/[0.03]">
              <div className="flex flex-col">
                <span className="text-[9px] text-[var(--text-muted)] uppercase tracking-widest mb-1">Source Matrix</span>
                <span className="text-[11px] font-mono text-[var(--text-secondary)]">
                  {wisdom.metadata?.source || "Core Intelligence Nexus"}
                </span>
              </div>
              <div className="flex flex-col text-right">
                <span className="text-[9px] text-[var(--text-muted)] uppercase tracking-widest mb-1">Strategic Alignment</span>
                <span className="text-[11px] font-mono text-[var(--color-precision-green)] uppercase">
                  {(wisdom.metadata?.confidence || 0.98 * 100).toFixed(0)}% Synchronized
                </span>
              </div>
            </div>
          </div>
        ) : !loading && (
          <div className="text-[var(--text-muted)] font-mono italic text-sm animate-pulse">
            Awaiting divine intervention from the latent space...
          </div>
        )}
      </div>

      {/* Decorative Gold Corner */}
      <div className="absolute top-0 right-0 w-16 h-16 pointer-events-none">
        <div className="absolute top-0 right-0 w-[1px] h-8 bg-[var(--border-gold)] opacity-30"></div>
        <div className="absolute top-0 right-0 w-8 h-[1px] bg-[var(--border-gold)] opacity-30"></div>
      </div>
    </div>
  );
};

export default WisdomOracle;
