import 'dart:convert';
import '../config/api_config.dart';
import '../models/warehouse.dart';
import 'api_client.dart';

class WarehouseService {
  static Future<List<Warehouse>> getWarehouses(ApiClient apiClient) async {
    final url = '${ApiConfig.baseUrl}/warehouses/';
    final response = await apiClient.get(url);

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Warehouse.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load warehouses: ${response.statusCode}');
    }
  }

  static Future<Warehouse> getWarehouse(ApiClient apiClient, String id) async {
    final url = '${ApiConfig.baseUrl}/warehouses/$id';
    final response = await apiClient.get(url);

    if (response.statusCode == 200) {
      return Warehouse.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to load warehouse: ${response.statusCode}');
    }
  }
}
