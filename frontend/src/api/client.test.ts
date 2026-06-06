import { describe, it, expect, vi, beforeEach } from 'vitest';
import { processAction } from './client';

describe('client API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('processAction', () => {
    it('should call fetch with correct parameters and return data on success', async () => {
      const mockResponse = { success: true, message: 'Action processed' };
      vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      }));

      const action = { action_type: 'combat', description: 'attack' };
      const result = await processAction(action);

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      });
      expect(result).toEqual(mockResponse);
    });

    it('should throw an error if the response is not ok', async () => {
      vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
      }));

      const action = { action_type: 'combat', description: 'attack' };
      await expect(processAction(action)).rejects.toThrow('HTTP 400');
    });
  });
});
