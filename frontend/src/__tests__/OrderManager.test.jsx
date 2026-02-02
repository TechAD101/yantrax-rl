import React from 'react';
import { vi, describe, it, expect } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import OrderManager from '../pages/OrderManager';

vi.mock('../api/api', async () => {
  const actual = await vi.importActual('../api/api');
  return {
    ...actual,
    createOrder: vi.fn().mockResolvedValue({ order: { id: 1, symbol: 'TEST', usd: 50, quantity: 100, status: 'filled' } }),
    listOrders: vi.fn().mockResolvedValue({ orders: [{ id: 1, symbol: 'TEST', usd: 50, quantity: 100, status: 'filled' }] })
  };
});

describe('OrderManager', () => {
  it('creates and lists orders', async () => {
    render(<OrderManager />);

    const input = screen.getByPlaceholderText('Symbol');
    fireEvent.change(input, { target: { value: 'TEST' } });

    const createBtn = screen.getByText(/Create Order/i);
    fireEvent.click(createBtn);

    await waitFor(() => expect(screen.getByText(/Created order/)).toBeTruthy());
    expect(screen.getByText('TEST')).toBeTruthy();
  });
});
