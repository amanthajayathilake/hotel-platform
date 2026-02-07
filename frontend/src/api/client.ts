import axios, { AxiosError } from 'axios';
import type {
  AuthResponse,
  User,
  Hotel,
  RoomType,
  RateAdjustment,
  LoginCredentials,
  MessageResponse,
} from '@/types';

// Base API URL - will use Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Hotels API
export const hotelsAPI = {
  getAll: async (params?: { status?: string; city?: string }): Promise<Hotel[]> => {
    const response = await api.get<Hotel[]>('/hotels', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Hotel> => {
    const response = await api.get<Hotel>(`/hotels/${id}`);
    return response.data;
  },

  create: async (formData: FormData): Promise<Hotel> => {
    const response = await api.post<Hotel>('/hotels', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  update: async (id: number, formData: FormData): Promise<Hotel> => {
    const response = await api.put<Hotel>(`/hotels/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (id: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/hotels/${id}`);
    return response.data;
  },
};

// Room Types API
export const roomTypesAPI = {
  getAll: async (hotelId?: number): Promise<RoomType[]> => {
    const params = hotelId ? { hotel_id: hotelId } : {};
    const response = await api.get<RoomType[]>('/room-types', { params });
    return response.data;
  },

  getById: async (id: number): Promise<RoomType> => {
    const response = await api.get<RoomType>(`/room-types/${id}`);
    return response.data;
  },

  create: async (formData: FormData): Promise<RoomType> => {
    const response = await api.post<RoomType>('/room-types', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  update: async (id: number, formData: FormData): Promise<RoomType> => {
    const response = await api.put<RoomType>(`/room-types/${id}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (id: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/room-types/${id}`);
    return response.data;
  },
};

// Rate Adjustments API
export const rateAdjustmentsAPI = {
  getAll: async (roomTypeId?: number): Promise<RateAdjustment[]> => {
    const params = roomTypeId ? { room_type_id: roomTypeId } : {};
    const response = await api.get<RateAdjustment[]>('/rate-adjustments', { params });
    return response.data;
  },

  getById: async (id: number): Promise<RateAdjustment> => {
    const response = await api.get<RateAdjustment>(`/rate-adjustments/${id}`);
    return response.data;
  },

  create: async (data: {
    room_type_id: number;
    adjustment_amount: number;
    effective_date: string;
    reason: string;
  }): Promise<RateAdjustment> => {
    const response = await api.post<RateAdjustment>('/rate-adjustments', data);
    return response.data;
  },

  delete: async (id: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/rate-adjustments/${id}`);
    return response.data;
  },

  getHistory: async (roomTypeId: number): Promise<RateAdjustment[]> => {
    const response = await api.get<RateAdjustment[]>(
      `/rate-adjustments/room-type/${roomTypeId}/history`
    );
    return response.data;
  },
};

export default api;
