import type { AuthResponse, User, Plant, PlantSearchResponse, DashboardSummary, DemoStore } from '../types';

const rawBase = import.meta.env.VITE_API_BASE_URL || '/api';
const API_BASE = rawBase.replace(/\/+$/, '');

function getStoredToken(): string | null {
  return localStorage.getItem('cropguard_token') || localStorage.getItem('cropshield_token');
}

function clearStoredAuth(): void {
  localStorage.removeItem('cropguard_token');
  localStorage.removeItem('cropguard_user');
  localStorage.removeItem('cropshield_token');
  localStorage.removeItem('cropshield_user');
}

function getAuthHeader(): Record<string, string> {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearStoredAuth();
    window.dispatchEvent(new Event('auth:unauthorized'));
    throw new Error('Your session has expired. Please log in again.');
  }

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred.';
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' 
          ? errJson.detail 
          : JSON.stringify(errJson.detail);
      }
    } catch {
      errorDetail = `Request failed with status ${response.status}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Auth
  register: (data: { full_name: string; email: string; password: string; confirm_password: string }): Promise<AuthResponse> =>
    request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }): Promise<AuthResponse> =>
    request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: async (): Promise<void> => {
    try {
      await request('/auth/logout', { method: 'POST' });
    } finally {
      localStorage.removeItem('cropshield_token');
      localStorage.removeItem('cropshield_user');
    }
  },

  getMe: (): Promise<User> => request<User>('/auth/me'),

  // Dashboard
  getDashboardSummary: (): Promise<DashboardSummary> =>
    request<DashboardSummary>('/dashboard/summary'),

  // Plantopedia
  searchPlants: (query?: string): Promise<PlantSearchResponse> => {
    const q = query ? `?q=${encodeURIComponent(query)}` : '';
    return request<PlantSearchResponse>(`/plants${q}`);
  },

  getPlantDetail: (plantId: number): Promise<Plant> =>
    request<Plant>(`/plants/${plantId}`),

  getBookmarks: (): Promise<Plant[]> =>
    request<Plant[]>('/plants/bookmarks'),

  addBookmark: (plantId: number): Promise<{ message: string; bookmarked: boolean }> =>
    request(`/plants/${plantId}/bookmark`, { method: 'POST' }),

  removeBookmark: (plantId: number): Promise<{ message: string; bookmarked: boolean }> =>
    request(`/plants/${plantId}/bookmark`, { method: 'DELETE' }),

  // Nearby Stores
  getDemoStores: (search?: string, category?: string): Promise<DemoStore[]> => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (category && category !== 'All') params.append('category', category);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return request<DemoStore[]>(`/stores/demo${queryString}`);
  },

  // Disease Detection
  getModelStatus: (): Promise<import('../types').DiseaseModelStatus> =>
    request<import('../types').DiseaseModelStatus>('/disease/status'),

  detectDisease: async (crop: string, file: File): Promise<import('../types').DiseaseDetectionResult> => {
    const formData = new FormData();
    formData.append('crop', crop);
    formData.append('file', file);

    const token = getStoredToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

    const response = await fetch(`${API_BASE}/disease/detect`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (response.status === 401) {
      clearStoredAuth();
      window.dispatchEvent(new Event('auth:unauthorized'));
      throw new Error('Your session has expired. Please log in again.');
    }

    if (!response.ok) {
      let errorDetail = 'Inference request failed.';
      try {
        const errJson = await response.json();
        if (errJson && errJson.detail) {
          errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch {
        errorDetail = `Request failed with status ${response.status}`;
      }
      throw new Error(errorDetail);
    }

    return response.json();
  },

  getDetectionHistory: (limit = 20, offset = 0): Promise<import('../types').DiseaseHistoryItem[]> =>
    request<import('../types').DiseaseHistoryItem[]>(`/disease/history?limit=${limit}&offset=${offset}`),

  getDetectionDetail: (recordId: number): Promise<import('../types').DiseaseDetectionResult> =>
    request<import('../types').DiseaseDetectionResult>(`/disease/history/${recordId}`),

  deleteDetectionRecord: (recordId: number): Promise<{ message: string; id: number }> =>
    request<{ message: string; id: number }>(`/disease/history/${recordId}`, { method: 'DELETE' }),

  // Plant Assistant AI
  sendChatMessage: (data: {
    message: string;
    plant_id?: number;
    conversation_id?: number;
    language?: string;
  }): Promise<import('../types').ChatResponse> =>
    request<import('../types').ChatResponse>('/plant-assistant/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getConversations: (limit = 30, offset = 0): Promise<import('../types').ConversationSummary[]> =>
    request<import('../types').ConversationSummary[]>(`/plant-assistant/conversations?limit=${limit}&offset=${offset}`),

  getConversationDetail: (conversationId: number): Promise<import('../types').ConversationDetail> =>
    request<import('../types').ConversationDetail>(`/plant-assistant/conversations/${conversationId}`),

  deleteConversation: (conversationId: number): Promise<{ message: string; id: number }> =>
    request<{ message: string; id: number }>(`/plant-assistant/conversations/${conversationId}`, {
      method: 'DELETE',
    }),
};
