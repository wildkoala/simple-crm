// API client for backend communication

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ApiError {
  detail: string;
}

// Auth token management
export function getAuthToken(): string | null {
  return localStorage.getItem('auth_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('auth_token', token);
}

export function clearAuthToken(): void {
  localStorage.removeItem('auth_token');
}

// Generic fetch wrapper with auth
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken();
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'An error occurred');
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// Auth API
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreateByAdmin {
  email: string;
  name: string;
  password: string;
  role: 'admin' | 'user';
}

export interface UserUpdate {
  name?: string;
  email?: string;
  role?: 'admin' | 'user';
  is_active?: boolean;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordReset {
  token: string;
  new_password: string;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

export async function login(credentials: LoginCredentials): Promise<AuthToken> {
  return fetchApi<AuthToken>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

export async function getCurrentUser(): Promise<User> {
  return fetchApi<User>('/auth/me');
}

// Contacts API
export interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  organization: string;
  contact_type: 'individual' | 'commercial' | 'government';
  status: 'cold' | 'warm' | 'hot';
  needs_follow_up: boolean;
  follow_up_date?: string;
  notes: string;
  created_at: string;
  last_contacted_at?: string;
  assigned_user_id: string;
  assigned_user?: User;
}

export interface ContactCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  organization: string;
  contact_type: 'individual' | 'commercial' | 'government';
  status: 'cold' | 'warm' | 'hot';
  needs_follow_up: boolean;
  follow_up_date?: string;
  notes: string;
  assigned_user_id?: string;
}

export async function getContacts(): Promise<Contact[]> {
  return fetchApi<Contact[]>('/contacts');
}

export async function getContact(id: string): Promise<Contact> {
  return fetchApi<Contact>(`/contacts/${id}`);
}

export async function createContact(contact: ContactCreate): Promise<Contact> {
  return fetchApi<Contact>('/contacts', {
    method: 'POST',
    body: JSON.stringify(contact),
  });
}

export async function updateContact(id: string, contact: ContactCreate): Promise<Contact> {
  return fetchApi<Contact>(`/contacts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(contact),
  });
}

export async function patchContact(id: string, updates: Partial<ContactCreate>): Promise<Contact> {
  return fetchApi<Contact>(`/contacts/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function deleteContact(id: string): Promise<void> {
  return fetchApi<void>(`/contacts/${id}`, {
    method: 'DELETE',
  });
}

// Communications API
export interface Communication {
  id: string;
  contact_id: string;
  date: string;
  type: 'email' | 'phone' | 'meeting' | 'other';
  notes: string;
  created_at: string;
}

export interface CommunicationCreate {
  contact_id: string;
  date: string;
  type: 'email' | 'phone' | 'meeting' | 'other';
  notes: string;
}

export async function getCommunications(contactId?: string): Promise<Communication[]> {
  const query = contactId ? `?contact_id=${contactId}` : '';
  return fetchApi<Communication[]>(`/communications${query}`);
}

export async function createCommunication(communication: CommunicationCreate): Promise<Communication> {
  return fetchApi<Communication>('/communications', {
    method: 'POST',
    body: JSON.stringify(communication),
  });
}

export async function deleteCommunication(id: string): Promise<void> {
  return fetchApi<void>(`/communications/${id}`, {
    method: 'DELETE',
  });
}

// Contracts API
export interface ContactBrief {
  id: string;
  first_name: string;
  last_name: string;
}

export interface Contract {
  id: string;
  title: string;
  description: string;
  source: string;
  deadline: string;
  status: 'prospective' | 'in progress' | 'submitted' | 'not a good fit';
  submission_link?: string;
  notes: string;
  created_at: string;
  assigned_contact_ids: string[];
  assigned_contacts: ContactBrief[];
}

export interface ContractCreate {
  title: string;
  description: string;
  source: string;
  deadline: string;
  status: 'prospective' | 'in progress' | 'submitted' | 'not a good fit';
  submission_link?: string;
  notes: string;
  assigned_contact_ids: string[];
}

export async function getContracts(): Promise<Contract[]> {
  return fetchApi<Contract[]>('/contracts');
}

export async function getContract(id: string): Promise<Contract> {
  return fetchApi<Contract>(`/contracts/${id}`);
}

export async function createContract(contract: ContractCreate): Promise<Contract> {
  return fetchApi<Contract>('/contracts', {
    method: 'POST',
    body: JSON.stringify(contract),
  });
}

export async function updateContract(id: string, contract: ContractCreate): Promise<Contract> {
  return fetchApi<Contract>(`/contracts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(contract),
  });
}

export async function patchContract(id: string, updates: Partial<ContractCreate>): Promise<Contract> {
  return fetchApi<Contract>(`/contracts/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function deleteContract(id: string): Promise<void> {
  return fetchApi<void>(`/contracts/${id}`, {
    method: 'DELETE',
  });
}

// Follow-up specific endpoints
export async function getDueFollowUps(daysAhead: number = 7): Promise<Contact[]> {
  return fetchApi<Contact[]>(`/contacts/follow-ups/due?days_ahead=${daysAhead}`);
}

export async function getOverdueFollowUps(): Promise<Contact[]> {
  return fetchApi<Contact[]>('/contacts/follow-ups/overdue');
}

// Users API
export async function getUsers(): Promise<User[]> {
  return fetchApi<User[]>('/users');
}

export async function getUser(userId: string): Promise<User> {
  return fetchApi<User>(`/users/${userId}`);
}

export async function createUser(user: UserCreateByAdmin): Promise<User> {
  return fetchApi<User>('/users', {
    method: 'POST',
    body: JSON.stringify(user),
  });
}

export async function updateUser(userId: string, updates: UserUpdate): Promise<User> {
  return fetchApi<User>(`/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

export async function deleteUser(userId: string): Promise<{ message: string }> {
  return fetchApi<{ message: string }>(`/users/${userId}`, {
    method: 'DELETE',
  });
}

// Password reset API
export async function requestPasswordReset(email: string): Promise<{ message: string }> {
  return fetchApi<{ message: string }>('/auth/password-reset-request', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(data: PasswordReset): Promise<{ message: string }> {
  return fetchApi<{ message: string }>('/auth/password-reset', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function changePassword(data: PasswordChange): Promise<{ message: string }> {
  return fetchApi<{ message: string }>('/auth/password-change', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// API Key Management
export interface ApiKeyResponse {
  api_key: string;
  message: string;
}

export interface ApiKeyStatus {
  has_api_key: boolean;
  api_key_prefix: string | null;
}

export async function generateApiKey(): Promise<ApiKeyResponse> {
  return fetchApi<ApiKeyResponse>('/users/me/api-key/generate', {
    method: 'POST',
  });
}

export async function revokeApiKey(): Promise<{ message: string }> {
  return fetchApi<{ message: string }>('/users/me/api-key', {
    method: 'DELETE',
  });
}

export async function getApiKeyStatus(): Promise<ApiKeyStatus> {
  return fetchApi<ApiKeyStatus>('/users/me/api-key/status');
}
