import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import '../models/product.dart';

class ProductService {
  final String token;

  ProductService(this.token);

  Map<String, String> get _headers => {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };

  Future<List<Product>> getProducts({int skip = 0, int limit = 50, String? search}) async {
    try {
      final queryParams = {
        'skip': skip.toString(),
        'limit': limit.toString(),
        if (search != null && search.isNotEmpty) 'search': search,
      };

      final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.products}')
          .replace(queryParameters: queryParams);

      final response = await http
          .get(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

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
      final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.productByRef}/$ref');

      final response = await http
          .get(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

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
      final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.products}');

      final response = await http
          .post(
            uri,
            headers: _headers,
            body: json.encode(product.toJson()),
          )
          .timeout(ApiConfig.timeout);

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
}
