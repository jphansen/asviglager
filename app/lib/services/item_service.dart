import 'dart:convert';
import '../config/api_config.dart';
import '../models/item.dart';
import 'api_client.dart';

class ItemService {
  final ApiClient apiClient;

  ItemService(this.apiClient);

  Future<List<Item>> getItems({int skip = 0, int limit = 50, String? search}) async {
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
        return data.map((json) => Item.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load items: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching items: $e');
    }
  }

  Future<Item> getItemByRef(String ref) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.productByRef}/$ref';
      final response = await apiClient.get(url);

      if (response.statusCode == 200) {
        return Item.fromJson(json.decode(response.body));
      } else {
        throw Exception('Item not found');
      }
    } catch (e) {
      throw Exception('Error fetching item: $e');
    }
  }

  Future<Item> createItem(Item item) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}';
      final response = await apiClient.post(url, body: item.toJson());

      if (response.statusCode == 201) {
        return Item.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to create item');
      }
    } catch (e) {
      throw Exception('Error creating item: $e');
    }
  }

  Future<Item> updateItem(String itemId, Item item) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$itemId';
      final response = await apiClient.put(url, body: item.toJson());

      if (response.statusCode == 200) {
        return Item.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to update item');
      }
    } catch (e) {
      throw Exception('Error updating item: $e');
    }
  }

  Future<Item> updateStock(String itemId, String warehouseRef, double items) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$itemId/stock/$warehouseRef';
      final response = await apiClient.put(url, body: {'items': items});

      if (response.statusCode == 200) {
        return Item.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to update stock');
      }
    } catch (e) {
      throw Exception('Error updating stock: $e');
    }
  }

  Future<Map<String, WarehouseStock>> getStock(String itemId) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$itemId/stock';
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

  Future<void> removeStock(String itemId, String warehouseRef) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$itemId/stock/$warehouseRef';
      final response = await apiClient.delete(url);

      if (response.statusCode != 204) {
        throw Exception('Failed to remove stock');
      }
    } catch (e) {
      throw Exception('Error removing stock: $e');
    }
  }

  Future<void> deleteItem(String itemId) async {
    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.products}/$itemId';
      final response = await apiClient.delete(url);

      if (response.statusCode != 204) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to delete item');
      }
    } catch (e) {
      throw Exception('Error deleting item: $e');
    }
  }
}
