import React from 'react';
import { vi, describe, it, expect } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MemecoinHub from '../pages/MemecoinHub';

vi.mock('../api/api', async () => {
  const actual = await vi.importActual('../api/api');
  return {
    ...actual,
    scanMemecoins: vi.fn().mockResolvedValue({ results: [{ symbol: 'TEST', degen_score: 10, social: 100, mentions: 5 }] }),
    getTopMemecoins: vi.fn().mockResolvedValue({ memecoins: [{ symbol: 'TEST', score: 10 }] }),
    simulateMemecoin: vi.fn().mockResolvedValue({ result: { symbol: 'TEST', price: 0.5, usd: 100, quantity: 200 } })
  };
});

describe('MemecoinHub', () => {
  it('scans and simulates', async () => {
    render(<MemecoinHub />);

    const scanBtn = screen.getByText(/Scan Market/i);
    fireEvent.click(scanBtn);

    await waitFor(() => expect(screen.getAllByText('TEST').length).toBeGreaterThan(0));

    // Simulate trade
    const sym = screen.getByPlaceholderText('Symbol');
    fireEvent.change(sym, { target: { value: 'TEST' } });
    const simBtn = screen.getByRole('button', { name: /Simulate/i });
    fireEvent.click(simBtn);

    await waitFor(() => expect(screen.getByText(/Purchased/)).toBeTruthy());
  });
});