import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  nombre: string;
  role: string;
}

// ── API functions ─────────────────────────────────────────────────────────────

export async function loginApi(email: string, password: string): Promise<TokenResponse> {
  const response = await axios.post<TokenResponse>(
    `${BASE_URL}/auth/login`,
    { email, password }
  );
  return response.data;
}

export async function registerApi(
  email: string,
  password: string,
  nombre: string
): Promise<TokenResponse> {
  const response = await axios.post<TokenResponse>(
    `${BASE_URL}/auth/register`,
    { email, password, nombre }
  );
  return response.data;
}

export async function getMeApi(token: string): Promise<UserResponse> {
  const response = await axios.get<UserResponse>(`${BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function logoutApi(token: string): Promise<void> {
  await axios.post(
    `${BASE_URL}/auth/logout`,
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
}
