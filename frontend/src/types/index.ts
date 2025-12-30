// API Types matching backend models

export interface User {
  username: string;
  email: string;
  full_name?: string;
  disabled?: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Product {
  id?: string;
  _id?: string; // MongoDB ID field
  ref: string;
  label: string;
  price: number;
  price_ttc?: number;
  type: '0' | '1'; // 0=product, 1=service
  barcode?: string;
  description?: string;
  status: '0' | '1'; // 0=disabled, 1=enabled
  tobuy?: string;
  deleted?: boolean;
  stock?: Record<string, number>; // warehouse_id -> quantity
  photos?: string[]; // photo IDs
  date_creation?: string;
  date_modification?: string;
}

export interface ProductCreate {
  ref: string;
  label: string;
  price: number;
  type: '0' | '1';
  barcode?: string;
  description?: string;
  status?: '0' | '1';
  tobuy?: string;
}

export interface ProductUpdate {
  ref?: string;
  label?: string;
  price?: number;
  type?: '0' | '1';
  barcode?: string;
  description?: string;
  status?: '0' | '1';
  tobuy?: string;
}

export interface Warehouse {
  id?: string;
  _id?: string; // MongoDB ID field
  ref: string;
  label: string;
  description?: string;
  short?: string; // Short location code
  address?: string;
  zip?: string;
  town?: string;
  phone?: string;
  fax?: string;
  status: boolean; // true=enabled, false=disabled
  deleted?: boolean;
  date_creation?: string;
  date_modification?: string;
}

export interface WarehouseCreate {
  ref: string;
  label: string;
  description?: string;
  short?: string;
  address?: string;
  zip?: string;
  town?: string;
  phone?: string;
  fax?: string;
  status?: boolean;
}

export interface Photo {
  id?: string;
  filename: string;
  content_type: string;
  description?: string;
  file_size?: number;
  date_creation?: string;
  uploaded_by?: string;
  data?: string; // base64
}

export interface PhotoUpload {
  filename: string;
  data: string; // base64
  content_type: string;
  description?: string;
}

export interface StockUpdate {
  warehouse_id: string;
  quantity: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ProductListParams extends PaginationParams {
  search?: string;
  type?: '0' | '1';
}

export interface WarehouseListParams extends PaginationParams {
  search?: string;
  status?: '0' | '1';
}
