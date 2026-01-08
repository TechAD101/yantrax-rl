// src/components/wizard/PortfolioWizard.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StepGoals from './StepGoals';
import StepMarkets from './StepMarkets';
import StepStrategy from './StepStrategy';
import StepCapital from './StepCapital';
import StepRisk from './StepRisk';
import ProgressBar from './ProgressBar';
import { createPortfolio } from '../../api/api';

const PortfolioWizard = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [config, setConfig] = useState({
        goals: [],
        markets: [],
        strategy: 'ai_managed',
        capital: 100000,
        risk: 'moderate'
    });

    const nextStep = () => setStep(s => Math.min(s + 1, 5));
    const prevStep = () => setStep(s => Math.max(s - 1, 1));

    const handleSubmit = async () => {
            setIsSubmitting(true);
        console.log('Submitting Portfolio Config:', config);

        try {
            // Call backend API to create portfolio
            const result = await createPortfolio(config);

            if (result && result.portfolio) {
                alert('🚀 AI Firm Initialized! Welcome CEO.');
                navigate('/dashboard');
            } else {
                throw new Error('Invalid response from server');
            }
        } catch (error) {
            console.error('Setup failed:', error);
            alert('Failed to initialize firm. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const renderStep = () => {
        switch (step) {
            case 1: return <StepGoals config={config} setConfig={setConfig} />;
            case 2: return <StepMarkets config={config} setConfig={setConfig} />;
            case 3: return <StepStrategy config={config} setConfig={setConfig} />;
            case 4: return <StepCapital config={config} setConfig={setConfig} />;
            case 5: return <StepRisk config={config} setConfig={setConfig} />;
            default: return <StepGoals />;
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto p-6 bg-gray-900/90 backdrop-blur-xl rounded-xl shadow-2xl border border-gray-800 ring-1 ring-white/10">
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 mb-6 text-center">
                Initialize Your AI Trading Firm
            </h1>
            <ProgressBar currentStep={step} totalSteps={5} />
            <div className="mt-8 min-h-[400px]">
                {renderStep()}
            </div>
            <div className="flex justify-between mt-8 pt-6 border-t border-gray-800">
                <button
                    onClick={prevStep}
                    disabled={step === 1 || isSubmitting}
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${step === 1 ? 'text-gray-600 cursor-not-allowed' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                >
                    Back
                </button>
                <button
                    onClick={step === 5 ? handleSubmit : nextStep}
                    disabled={isSubmitting}
                    className={`px-8 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white rounded-lg font-semibold shadow-lg shadow-blue-500/20 transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-wait
                        ${isSubmitting ? 'animate-pulse' : ''}`}
                >
                    {isSubmitting ? 'Initializing...' : (step === 5 ? 'Launch Firm 🚀' : 'Next Step')}
                </button>
            </div>
        </div>
    );
};
export default PortfolioWizard;
