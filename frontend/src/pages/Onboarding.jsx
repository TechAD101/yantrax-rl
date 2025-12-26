// src/pages/Onboarding.jsx
import React from 'react';
import PortfolioWizard from '../components/wizard/PortfolioWizard';

const Onboarding = () => {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4 bg-grid-pattern">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 to-purple-900/20 pointer-events-none" />
      <div className="relative z-10 w-full max-w-4xl">
        <PortfolioWizard />
      </div>
    </div>
  );
};

export default Onboarding;
