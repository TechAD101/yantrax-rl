// src/components/wizard/ProgressBar.jsx
import React from 'react';

const ProgressBar = ({ currentStep, totalSteps }) => {
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;

    return (
        <div className="w-full">
            <div className="flex justify-between mb-2">
                {[...Array(totalSteps)].map((_, i) => (
                    <div key={i} className="flex flex-col items-center">
                        <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-500
                                ${i + 1 <= currentStep
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50 scale-110'
                                    : 'bg-gray-800 text-gray-500 border border-gray-700'}`}
                        >
                            {i + 1}
                        </div>
                        <span className={`text-xs mt-2 ${i + 1 <= currentStep ? 'text-blue-400' : 'text-gray-600'}`}>
                            {['Goals', 'Markets', 'Strategy', 'Capital', 'Risk'][i]}
                        </span>
                    </div>
                ))}
            </div>
            <div className="h-2 bg-gray-800 rounded-full mt-2 relative overflow-hidden">
                <div
                    className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-purple-500 transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>
        </div>
    );
};

export default ProgressBar;
