import api from './api';
import type { Warehouse, WarehouseCreate, WarehouseListParams } from '../types';

export const warehouseService = {
  async getWarehouses(params?: WarehouseListParams): Promise<Warehouse[]> {
    const response = await api.get<Warehouse[]>('/warehouses/', { params });
    return response.data;
  },

  async getWarehouse(id: string): Promise<Warehouse> {
    const response = await api.get<Warehouse>(`/warehouses/${id}`);
    return response.data;
  },

  async getWarehouseByRef(ref: string): Promise<Warehouse> {
    const response = await api.get<Warehouse>(`/warehouses/ref/${ref}`);
    return response.data;
  },

  async createWarehouse(warehouse: WarehouseCreate): Promise<Warehouse> {
    const response = await api.post<Warehouse>('/warehouses/', warehouse);
    return response.data;
  },

  async updateWarehouse(id: string, warehouse: Partial<Warehouse>): Promise<Warehouse> {
    const response = await api.put<Warehouse>(`/warehouses/${id}`, warehouse);
    return response.data;
  },

  async deleteWarehouse(id: string): Promise<Warehouse> {
    const response = await api.delete<Warehouse>(`/warehouses/${id}`);
    return response.data;
  },

  async getDeletedWarehouses(): Promise<Warehouse[]> {
    const response = await api.get<Warehouse[]>('/warehouses/deleted/');
    return response.data;
  },
};
