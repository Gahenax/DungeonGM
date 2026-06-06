import { renderHook, act } from '@testing-library/react';
import { useGameEngine } from './useGameEngine';
import { processAction, rollDice } from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
  processAction: vi.fn(),
  rollDice: vi.fn(),
}));

describe('useGameEngine', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useGameEngine());

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.gameState).toEqual({
      hp: 10,
      maxHp: 10,
      ac: 10,
      level: 1,
    });
  });

  describe('performAction', () => {
    it('should handle a successful action and update game state', async () => {
      const mockResult = {
        success: true,
        message: 'Action successful',
        narrative: 'You did a thing.',
        game_state: {
          hp: 8,
          room: { id: 'room_2', name: 'Dark Cave', description: 'It is dark.' }
        }
      };

      (processAction as any).mockResolvedValueOnce(mockResult);

      const { result } = renderHook(() => useGameEngine());

      let actionResult;
      await act(async () => {
        actionResult = await result.current.performAction('move', 'Go north');
      });

      expect(processAction).toHaveBeenCalledWith({
        action_type: 'move',
        description: 'Go north',
        character_id: 'player_1',
      });

      expect(actionResult).toEqual(mockResult);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      // Check that game state was updated and merged
      expect(result.current.gameState).toEqual({
        hp: 8,
        maxHp: 10,
        ac: 10,
        level: 1,
        room: { id: 'room_2', name: 'Dark Cave', description: 'It is dark.' }
      });
    });

    it('should handle a successful action without game state update', async () => {
      const mockResult = {
        success: true,
        message: 'Looked around',
        narrative: 'Nothing special.',
      };

      (processAction as any).mockResolvedValueOnce(mockResult);

      const { result } = renderHook(() => useGameEngine());

      let actionResult;
      await act(async () => {
        actionResult = await result.current.performAction('look', 'Look around');
      });

      expect(actionResult).toEqual(mockResult);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      // Check that game state remained the same
      expect(result.current.gameState).toEqual({
        hp: 10,
        maxHp: 10,
        ac: 10,
        level: 1,
      });
    });

    it('should handle action errors correctly', async () => {
      const errorMessage = 'Network error';
      (processAction as any).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useGameEngine());

      let actionResult;
      await act(async () => {
        actionResult = await result.current.performAction('attack', 'Attack goblin');
      });

      expect(actionResult).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(`Error: ${errorMessage}`);

      // Check that game state remained the same
      expect(result.current.gameState).toEqual({
        hp: 10,
        maxHp: 10,
        ac: 10,
        level: 1,
      });
    });
  });

  describe('roll', () => {
    it('should return result from rollDice', async () => {
      const mockResult = { total: 15, rolls: [15] };
      (rollDice as any).mockResolvedValueOnce(mockResult);

      const { result } = renderHook(() => useGameEngine());

      let rollResult;
      await act(async () => {
        rollResult = await result.current.roll('1d20');
      });

      expect(rollDice).toHaveBeenCalledWith('1d20');
      expect(rollResult).toEqual(mockResult);
      expect(result.current.error).toBeNull();
    });

    it('should handle roll errors correctly', async () => {
      const errorMessage = 'Invalid notation';
      (rollDice as any).mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useGameEngine());

      let rollResult;
      await act(async () => {
        rollResult = await result.current.roll('invalid');
      });

      expect(rollResult).toBeNull();
      expect(result.current.error).toBe(`Error: ${errorMessage}`);
    });
  });
});
