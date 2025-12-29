import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';
import '../models/photo.dart';

class PhotoService {
  final String token;

  PhotoService(this.token);

  Map<String, String> get _headers => {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };

  Future<Photo> uploadPhoto({
    required String filename,
    required String contentType,
    required String base64Data,
    String? description,
  }) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/photos');

      final body = {
        'filename': filename,
        'content_type': contentType,
        'data': base64Data,
        if (description != null) 'description': description,
      };

      final response = await http
          .post(
            uri,
            headers: _headers,
            body: json.encode(body),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 201) {
        return Photo.fromJson(json.decode(response.body));
      } else {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to upload photo');
      }
    } catch (e) {
      throw Exception('Error uploading photo: $e');
    }
  }

  Future<List<PhotoMetadata>> listPhotos() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/photos');

      final response = await http
          .get(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => PhotoMetadata.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load photos: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching photos: $e');
    }
  }

  Future<Photo> getPhoto(String photoId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/photos/$photoId');

      final response = await http
          .get(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return Photo.fromJson(json.decode(response.body));
      } else {
        throw Exception('Photo not found');
      }
    } catch (e) {
      throw Exception('Error fetching photo: $e');
    }
  }

  Future<void> deletePhoto(String photoId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/photos/$photoId');

      final response = await http
          .delete(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

      if (response.statusCode != 204) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to delete photo');
      }
    } catch (e) {
      throw Exception('Error deleting photo: $e');
    }
  }

  Future<void> addPhotoToProduct(String productId, String photoId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/products/$productId/photos/$photoId');

      final response = await http
          .post(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

      if (response.statusCode != 204) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to add photo to product');
      }
    } catch (e) {
      throw Exception('Error adding photo to product: $e');
    }
  }

  Future<void> removePhotoFromProduct(String productId, String photoId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/products/$productId/photos/$photoId');

      final response = await http
          .delete(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

      if (response.statusCode != 204) {
        final error = json.decode(response.body);
        throw Exception(error['detail'] ?? 'Failed to remove photo from product');
      }
    } catch (e) {
      throw Exception('Error removing photo from product: $e');
    }
  }

  Future<List<String>> getProductPhotos(String productId) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}/products/$productId/photos');

      final response = await http
          .get(uri, headers: _headers)
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.cast<String>();
      } else {
        throw Exception('Failed to load product photos: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching product photos: $e');
    }
  }
}
