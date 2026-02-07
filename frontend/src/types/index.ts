// API Response types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Hotel {
  id: number;
  name: string;
  description: string | null;
  address: string | null;
  city: string | null;
  country: string | null;
  phone: string | null;
  email: string | null;
  images: string[];
  status: 'active' | 'inactive' | 'maintenance';
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface RoomType {
  id: number;
  hotel_id: number;
  name: string;
  description: string | null;
  base_rate: string;
  max_occupancy: number;
  size_sqm: number | null;
  images: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  effective_rate: string | null;
}

export interface RateAdjustment {
  id: number;
  room_type_id: number;
  adjustment_amount: string;
  effective_date: string;
  reason: string;
  created_by: string | null;
  created_at: string;
}

// Form input types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface HotelFormData {
  name: string;
  description?: string;
  address?: string;
  city?: string;
  country?: string;
  phone?: string;
  email?: string;
  images?: File[];
}

export interface RoomTypeFormData {
  hotel_id: number;
  name: string;
  description?: string;
  base_rate: number;
  max_occupancy?: number;
  size_sqm?: number;
  images?: File[];
}

export interface RateAdjustmentFormData {
  room_type_id: number;
  adjustment_amount: number;
  effective_date: string;
  reason: string;
}

// API Response wrappers
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
  detail?: string;
}

export interface ErrorResponse {
  detail: string;
}
