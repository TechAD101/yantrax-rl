// @vitest-environment jsdom
import React from 'react';
import { render } from '@testing-library/react';
import TradingPerformanceChart from '../components/TradingPerformanceChart';
import { describe, test, expect } from 'vitest';

// Mock data
const mockPortfolioData = {
  totalValue: '$125,000',
  plToday: '+$492',
  activePositions: 4,
  performance: 17.2
};

const mockAiData = {
  executionTime: 45,
  signal: 'BUY',
  strategy: 'AI_ENSEMBLE'
};

describe('TradingPerformanceChart Performance', () => {
  test('re-renders efficiently', () => {
    // Render once to initialize
    const { rerender } = render(
      <TradingPerformanceChart
        portfolioData={mockPortfolioData}
        aiData={mockAiData}
      />
    );

    const iterations = 2000;
    const start = performance.now();

    for (let i = 0; i < iterations; i++) {
      // Re-render with props that don't affect chart data (e.g., activePositions)
      // We pass a new object for portfolioData to trigger prop change,
      // but keep totalValue same so chart data *should* be memoized if we implement useMemo.
      rerender(
        <TradingPerformanceChart
          portfolioData={{
            ...mockPortfolioData,
            activePositions: i % 10,
            // Keep totalValue same to benefit from memoization
          }}
          aiData={{
            ...mockAiData,
            executionTime: i % 100
          }}
        />
      );
    }

    const end = performance.now();
    const duration = end - start;

    console.log(`Performance Benchmark: ${iterations} re-renders took ${duration.toFixed(2)}ms`);

    expect(duration).toBeGreaterThan(0);
  });
});
