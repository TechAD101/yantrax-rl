import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import RiskManagementDashboard from '../components/RiskManagementDashboard';

describe('RiskManagementDashboard', () => {
  it('renders loading state correctly', () => {
    render(<RiskManagementDashboard loading={true} />);
    expect(screen.getByText('Risk Management System')).toBeInTheDocument();
  });

  it('renders overview tab by default', () => {
    render(<RiskManagementDashboard loading={false} />);
    expect(screen.getByText('Risk Assessment Summary')).toBeInTheDocument();
    expect(screen.getByText('Risk Thresholds')).toBeInTheDocument();
  });

  it('switches to VaR Analysis tab', () => {
    render(<RiskManagementDashboard loading={false} />);
    const varTab = screen.getByText('VaR Analysis');
    fireEvent.click(varTab);
    expect(screen.getByText('Value at Risk (VaR)')).toBeInTheDocument();
    expect(screen.getByText('Risk Attribution')).toBeInTheDocument();
    expect(screen.getByText('VaR Distribution')).toBeInTheDocument();
  });

  it('switches to Portfolio Risk tab', () => {
    render(<RiskManagementDashboard loading={false} />);
    const portfolioTab = screen.getByText('Portfolio Risk');
    fireEvent.click(portfolioTab);
    expect(screen.getByText('Position Risk Analysis')).toBeInTheDocument();
    expect(screen.getByText('Correlation Analysis')).toBeInTheDocument();
  });

  it('switches to Risk Alerts tab', () => {
    render(<RiskManagementDashboard loading={false} />);
    const alertsTab = screen.getByText('Risk Alerts');
    fireEvent.click(alertsTab);
    expect(screen.getByText('Recent Risk Alerts')).toBeInTheDocument();
    expect(screen.getByText('Alert Thresholds')).toBeInTheDocument();
  });

  it('displays simulated risk alerts when data is provided', () => {
    render(<RiskManagementDashboard loading={false} riskData={{}} portfolioData={{}} />);

    // Switch to alerts tab to see the alerts
    const alertsTab = screen.getByText('Risk Alerts');
    fireEvent.click(alertsTab);

    expect(screen.getByText('Volatility Spike Detected')).toBeInTheDocument();
  });
});
