import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/warehouse.dart';

class WarehouseService {
  static Future<List<Warehouse>> getWarehouses(String token) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/warehouses/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Warehouse.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load warehouses: ${response.statusCode}');
    }
  }

  static Future<Warehouse> getWarehouse(String token, String id) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/warehouses/$id'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return Warehouse.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to load warehouse: ${response.statusCode}');
    }
  }
}
