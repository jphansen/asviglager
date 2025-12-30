import api from './api';
import type { 
  Product, 
  ProductCreate, 
  ProductUpdate, 
  ProductListParams,
  StockUpdate 
} from '../types';

export const productService = {
  async getProducts(params?: ProductListParams): Promise<Product[]> {
    const response = await api.get<Product[]>('/products/', { params });
    return response.data;
  },

  async getProduct(id: string): Promise<Product> {
    const response = await api.get<Product>(`/products/${id}`);
    return response.data;
  },

  async getProductByRef(ref: string): Promise<Product> {
    const response = await api.get<Product>(`/products/ref/${ref}`);
    return response.data;
  },

  async getProductByBarcode(barcode: string): Promise<Product> {
    const response = await api.get<Product>(`/products/barcode/${barcode}`);
    return response.data;
  },

  async createProduct(product: ProductCreate): Promise<Product> {
    const response = await api.post<Product>('/products/', product);
    return response.data;
  },

  async updateProduct(id: string, product: ProductUpdate): Promise<Product> {
    const response = await api.put<Product>(`/products/${id}`, product);
    return response.data;
  },

  async deleteProduct(id: string): Promise<Product> {
    const response = await api.delete<Product>(`/products/${id}`);
    return response.data;
  },

  async getDeletedProducts(): Promise<Product[]> {
    const response = await api.get<Product[]>('/products/deleted/');
    return response.data;
  },

  async updateStock(id: string, stockUpdate: StockUpdate): Promise<Product> {
    const response = await api.put<Product>(`/products/${id}/stock`, stockUpdate);
    return response.data;
  },

  async getStock(id: string): Promise<Record<string, number>> {
    const response = await api.get<Record<string, number>>(`/products/${id}/stock`);
    return response.data;
  },

  async getStockForWarehouse(id: string, warehouseId: string): Promise<number> {
    const response = await api.get<number>(`/products/${id}/stock/${warehouseId}`);
    return response.data;
  },

  async removeStock(id: string, warehouseId: string): Promise<Product> {
    const response = await api.delete<Product>(`/products/${id}/stock/${warehouseId}`);
    return response.data;
  },

  async linkPhoto(id: string, photoId: string): Promise<Product> {
    const response = await api.post<Product>(`/products/${id}/photos/${photoId}`);
    return response.data;
  },

  async unlinkPhoto(id: string, photoId: string): Promise<Product> {
    const response = await api.delete<Product>(`/products/${id}/photos/${photoId}`);
    return response.data;
  },

  async getProductPhotos(id: string): Promise<string[]> {
    const response = await api.get<string[]>(`/products/${id}/photos`);
    return response.data;
  },
};
