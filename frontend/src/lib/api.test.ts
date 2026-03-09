import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getAuthToken,
  setAuthToken,
  clearAuthToken,
  login,
  getCurrentUser,
  deleteContact,
} from './api';

// We need to test the internal fetchApi behavior via the exported functions that use it.

const MOCK_USER = {
  id: 'u1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user' as const,
  is_active: true,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

describe('auth token helpers', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('getAuthToken returns null when no token set', () => {
    expect(getAuthToken()).toBeNull();
  });

  it('setAuthToken stores token, getAuthToken retrieves it', () => {
    setAuthToken('my-token');
    expect(getAuthToken()).toBe('my-token');
  });

  it('clearAuthToken removes token', () => {
    setAuthToken('my-token');
    clearAuthToken();
    expect(getAuthToken()).toBeNull();
  });
});

describe('fetchApi (via exported functions)', () => {
  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    localStorage.clear();
    fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('sends Authorization header when token is set', async () => {
    setAuthToken('test-token');
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(MOCK_USER),
    });

    await getCurrentUser();

    expect(fetchSpy).toHaveBeenCalledOnce();
    const [url, opts] = fetchSpy.mock.calls[0];
    expect(url).toContain('/auth/me');
    expect(opts.headers['Authorization']).toBe('Bearer test-token');
    expect(opts.headers['Content-Type']).toBe('application/json');
  });

  it('does not send Authorization header when no token', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(MOCK_USER),
    });

    await getCurrentUser();

    const [, opts] = fetchSpy.mock.calls[0];
    expect(opts.headers['Authorization']).toBeUndefined();
  });

  it('returns parsed JSON on success', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(MOCK_USER),
    });

    const result = await getCurrentUser();
    expect(result).toEqual(MOCK_USER);
  });

  it('returns undefined for 204 No Content', async () => {
    setAuthToken('test-token');
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 204,
    });

    const result = await deleteContact('c1');
    expect(result).toBeUndefined();
  });

  it('clears token and dispatches auth:unauthorized on 401', async () => {
    setAuthToken('test-token');
    const eventHandler = vi.fn();
    window.addEventListener('auth:unauthorized', eventHandler);

    fetchSpy.mockResolvedValue({
      ok: false,
      status: 401,
      text: () => Promise.resolve(JSON.stringify({ detail: 'Not authenticated' })),
    });

    await expect(getCurrentUser()).rejects.toThrow('Not authenticated');
    expect(getAuthToken()).toBeNull();
    expect(eventHandler).toHaveBeenCalledOnce();

    window.removeEventListener('auth:unauthorized', eventHandler);
  });

  it('parses JSON error with string detail', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 400,
      text: () => Promise.resolve(JSON.stringify({ detail: 'Bad request data' })),
    });

    await expect(getCurrentUser()).rejects.toThrow('Bad request data');
  });

  it('parses JSON error with array detail (validation errors)', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 422,
      text: () =>
        Promise.resolve(
          JSON.stringify({
            detail: [
              { msg: 'field required', loc: ['body', 'email'] },
              { msg: 'invalid value', loc: ['body', 'name'] },
            ],
          })
        ),
    });

    await expect(getCurrentUser()).rejects.toThrow('field required, invalid value');
  });

  it('falls back to plain text error when response is not JSON', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve('Internal Server Error'),
    });

    await expect(getCurrentUser()).rejects.toThrow('Internal Server Error');
  });

  it('falls back to status code message when body cannot be read', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 503,
      text: () => Promise.reject(new Error('cannot read body')),
    });

    await expect(getCurrentUser()).rejects.toThrow('Request failed (503)');
  });

  it('sends POST with JSON body for login', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ access_token: 'tok123', token_type: 'bearer' }),
    });

    const result = await login({ email: 'test@example.com', password: 'pass' });

    expect(result).toEqual({ access_token: 'tok123', token_type: 'bearer' });
    const [, opts] = fetchSpy.mock.calls[0];
    expect(opts.method).toBe('POST');
    expect(JSON.parse(opts.body)).toEqual({ email: 'test@example.com', password: 'pass' });
  });

  it('passes an AbortSignal to fetch for timeout support', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve(MOCK_USER),
    });

    await getCurrentUser();

    expect(fetchSpy).toHaveBeenCalledOnce();
    const [, opts] = fetchSpy.mock.calls[0];
    expect(opts.signal).toBeInstanceOf(AbortSignal);
  });
});
