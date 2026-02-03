import React, { useMemo } from 'react';

/**
 * NeuralSpine Component
 * Aesthetic: Industrial Neon / Cyber-Neural
 * Description: An animated SVG element that pulses with data-flow colors.
 * It serves as the "visual anchor" for the dashboard.
 */
const NeuralSpine = ({ painLevel = 0, isPanic = false }) => {
    // Generate random data nodes along the spine
    const nodes = useMemo(() => {
        return Array.from({ length: 40 }).map((_, i) => ({
            y: i * 2.5,
            delay: i * 0.1,
            size: Math.random() * 2 + 1,
        }));
    }, []);

    const spineColor = isPanic ? '#ef4444' : painLevel > 60 ? '#f59e0b' : '#3b82f6';
    const pulseClass = isPanic ? 'animate-pulse-fast' : 'animate-pulse-slow';

    return (
        <div className="neural-spine-container h-full w-8 bg-black/40 border-r border-white/5 relative flex flex-col items-center py-4 overflow-hidden">
            {/* Background Rail */}
            <div
                className="absolute h-full w-[1px] bg-white/10"
                style={{ left: '50%', transform: 'translateX(-50%)' }}
            ></div>

            {/* Glow Backbone */}
            <div
                className={`absolute h-full w-1 blur-[8px] opacity-30 ${pulseClass}`}
                style={{ left: '50%', transform: 'translateX(-50%)', backgroundColor: spineColor }}
            ></div>

            {/* Logic Gates / Nodes */}
            <svg className="w-full h-full relative z-10" viewBox="0 0 40 100" preserveAspectRatio="none">
                {nodes.map((node, i) => (
                    <g key={i}>
                        {/* The Synapse Point */}
                        <circle
                            cx="20"
                            cy={node.y}
                            r={node.size}
                            fill={spineColor}
                            className={`opacity-60 ${pulseClass}`}
                            style={{ animationDelay: `${node.delay}s` }}
                        >
                            <animate
                                attributeName="opacity"
                                values="0.2;0.8;0.2"
                                dur={`${2 + Math.random() * 2}s`}
                                repeatCount="indefinite"
                                begin={`${node.delay}s`}
                            />
                        </circle>

                        {/* Micro-connections */}
                        <line
                            x1="20" y1={node.y} x2={20 + (i % 2 === 0 ? 8 : -8)} y2={node.y}
                            stroke={spineColor} strokeWidth="0.5" className="opacity-20"
                        />
                    </g>
                ))}

                {/* The Flowing Pulse (Neural Wave) */}
                <rect width="40" height="2" fill={`url(#spineGradient)`} className="neural-wave" />

                <defs>
                    <linearGradient id="spineGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="transparent" />
                        <stop offset="50%" stopColor={spineColor} stopOpacity="0.8" />
                        <stop offset="100%" stopColor="transparent" />
                    </linearGradient>
                </defs>
            </svg>

            {/* Aesthetic Label */}
            <div className="absolute bottom-4 rotate-90 origin-bottom-left text-[8px] font-mono text-white/20 whitespace-nowrap tracking-[0.4em] translate-x-3">
                SYNAPTIC_SPINE_v4.7 // STATUS: {isPanic ? 'PANIC_LOCK' : 'STABLE'}
            </div>

            <style jsx>{`
        .neural-wave {
          animation: flow 4s linear infinite;
        }
        @keyframes flow {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }
        .animate-pulse-fast {
          animation: pulse 0.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .animate-pulse-slow {
          animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
      `}</style>
        </div>
    );
};

export default NeuralSpine;
