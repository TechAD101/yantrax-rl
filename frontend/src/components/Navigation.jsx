import React from 'react';

const Navigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'ai-firm', label: 'AI Firm' },
    { id: 'trading', label: 'Trading' },
    { id: 'risk', label: 'Risk' },
    { id: 'performance', label: 'Performance' }
  ];

  return (
    <nav className="bg-gray-900/50 border-b border-gray-700/30 backdrop-blur-md">
      <div className="px-6">
        <div className="flex space-x-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors duration-150
                ${
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;