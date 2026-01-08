import React from 'react';
import { vi, describe, it, expect } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import StrategyHub from '../pages/StrategyHub';

// Mock the api module
vi.mock('../api/api', async () => {
  const actual = await vi.importActual('../api/api');
  return {
    ...actual,
    listStrategies: vi.fn().mockImplementation(async (opts) => {
      const total = 7;
      const per_page = Number(opts.per_page || 6);
      const page = Number(opts.page || 1);
      const strategies = Array.from({ length: total }).map((_, i) => ({ id: i + 1, name: `S${i + 1}`, archetype: 'quant', metrics: { sharpe: 0.5 + i * 0.1 } }));
      const start = (page - 1) * per_page;
      return {
        strategies: strategies.slice(start, start + per_page),
        page,
        per_page,
        total,
        total_pages: Math.ceil(total / per_page)
      };
    })
  };
});

describe('StrategyHub', () => {
  it('renders and paginates', async () => {
    render(<StrategyHub />);

    // Should show loading then content
    await waitFor(() => expect(screen.queryByText(/Loading/i)).toBeNull());

    // First page should show S1
    expect(screen.getByText('S1')).toBeTruthy();

    // Click next page
    const next = screen.getByText(/Next/i);
    fireEvent.click(next);

    // After page change, should show S7 (last page with per_page default 6)
    await waitFor(() => expect(screen.getByText('S7')).toBeTruthy());
  });
});
