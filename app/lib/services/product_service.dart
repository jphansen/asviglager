import 'dart:convert';
import '../config/api_config.dart';
import '../models/product.dart';
import 'api_client.dart';

class ProductService {
  final ApiClient apiClient;

  ProductService(this.apiClient);

  Future<List<Product>> getProducts({int skip = 0, int limit = 50, String? search}) async {
    try {
      final queryParams = {
        'skip': skip.toString(),
        'limit': limit.toString(),
        if (search != null && search.isNotEmpty) 'search': search,
      };

      final url = '${ApiConfig.baseUrl}${ApiConfig.products}';
      final response = await apiClient.get(url, queryParams: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Product.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching products: $e');
    }
  }

  Future<Product> getProductByRef(String ref) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.productByRef}/$ref';
      final response = await apiClient.get(url);

      if (response.statusCode == 200) {
        return Product.fromJson(json.decode(response.body));
      } else {
        throw Exception('Product not found');
      }
    } catch (e) {
      throw Exception('Error fetching product: $e');
    }
  }

  Future<Product> createProduct(Product product) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}';
      final response = await apiClient.post(url, body: product.toJson());

      if (response.statusCode == 201) {
        return Product.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to create product');
      }
    } catch (e) {
      throw Exception('Error creating product: $e');
    }
  }

  Future<Product> updateProduct(String productId, Product product) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$productId';
      final response = await apiClient.put(url, body: product.toJson());

      if (response.statusCode == 200) {
        return Product.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to update product');
      }
    } catch (e) {
      throw Exception('Error updating product: $e');
    }
  }

  Future<Product> updateStock(String productId, String warehouseRef, double items) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$productId/stock/$warehouseRef';
      final response = await apiClient.put(url, body: {'items': items});

      if (response.statusCode == 200) {
        return Product.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to update stock');
      }
    } catch (e) {
      throw Exception('Error updating stock: $e');
    }
  }

  Future<Map<String, WarehouseStock>> getStock(String productId) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$productId/stock';
      final response = await apiClient.get(url);

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        Map<String, WarehouseStock> stock = {};
        data.forEach((key, value) {
          if (value is Map<String, dynamic>) {
            stock[key] = WarehouseStock.fromJson(value);
          }
        });
        return stock;
      } else {
        throw Exception('Failed to load stock');
      }
    } catch (e) {
      throw Exception('Error fetching stock: $e');
    }
  }

  Future<void> removeStock(String productId, String warehouseRef) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$productId/stock/$warehouseRef';
      final response = await apiClient.delete(url);

      if (response.statusCode != 204) {
        throw Exception('Failed to remove stock');
      }
    } catch (e) {
      throw Exception('Error removing stock: $e');
    }
  }

  Future<void> deleteProduct(String productId) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$productId';
      final response = await apiClient.delete(url);

      if (response.statusCode != 204) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to delete product');
      }
    } catch (e) {
      throw Exception('Error deleting product: $e');
    }
  }
}
