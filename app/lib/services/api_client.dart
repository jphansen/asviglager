import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'auth_service.dart';
import '../config/api_config.dart';

/// API client wrapper that handles authentication, token refresh, and error handling
class ApiClient {
  final AuthService authService;
  bool _isRefreshing = false;
  final List<Function> _pendingRequests = [];

  ApiClient(this.authService);

  Map<String, String> get _headers => {
        'Authorization': 'Bearer ${authService.token}',
        'Content-Type': 'application/json',
      };

  /// Make a GET request with automatic token refresh on 401
  Future<http.Response> get(String url, {Map<String, String>? queryParams}) async {
    Uri uri = Uri.parse(url);
    if (queryParams != null && queryParams.isNotEmpty) {
      uri = uri.replace(queryParameters: queryParams);
    }

    try {
      final response = await http.get(uri, headers: _headers).timeout(ApiConfig.timeout);
      return await _handleResponse(response, () => get(url, queryParams: queryParams));
    } catch (e) {
      debugPrint('GET request error: $e');
      rethrow;
    }
  }

  /// Make a POST request with automatic token refresh on 401
  Future<http.Response> post(String url, {Map<String, dynamic>? body}) async {
    try {
      final response = await http
          .post(
            Uri.parse(url),
            headers: _headers,
            body: body != null ? json.encode(body) : null,
          )
          .timeout(ApiConfig.timeout);
      return await _handleResponse(response, () => post(url, body: body));
    } catch (e) {
      debugPrint('POST request error: $e');
      rethrow;
    }
  }

  /// Make a PUT request with automatic token refresh on 401
  Future<http.Response> put(String url, {Map<String, dynamic>? body}) async {
    try {
      final response = await http
          .put(
            Uri.parse(url),
            headers: _headers,
            body: body != null ? json.encode(body) : null,
          )
          .timeout(ApiConfig.timeout);
      return await _handleResponse(response, () => put(url, body: body));
    } catch (e) {
      debugPrint('PUT request error: $e');
      rethrow;
    }
  }

  /// Make a DELETE request with automatic token refresh on 401
  Future<http.Response> delete(String url) async {
    try {
      final response = await http.delete(Uri.parse(url), headers: _headers).timeout(ApiConfig.timeout);
      return await _handleResponse(response, () => delete(url));
    } catch (e) {
      debugPrint('DELETE request error: $e');
      rethrow;
    }
  }

  /// Handle response and automatically refresh token on 401
  Future<http.Response> _handleResponse(
    http.Response response,
    Future<http.Response> Function() retryRequest,
  ) async {
    // If 401 Unauthorized, try to refresh token and retry
    if (response.statusCode == 401) {
      debugPrint('Received 401, attempting token refresh');

      // If already refreshing, queue this request
      if (_isRefreshing) {
        return await _queueRequest(retryRequest);
      }

      _isRefreshing = true;

      try {
        // Attempt to refresh the token
        final refreshed = await authService.refreshAccessToken();

        if (refreshed) {
          // Token refreshed successfully, retry all pending requests
          debugPrint('Token refreshed successfully, retrying request');
          _isRefreshing = false;
          
          // Process queued requests
          final pendingCopy = List<Function>.from(_pendingRequests);
          _pendingRequests.clear();
          for (var request in pendingCopy) {
            request();
          }

          // Retry the original request
          return await retryRequest();
        } else {
          // Refresh failed, log user out
          debugPrint('Token refresh failed, logging out');
          _isRefreshing = false;
          _pendingRequests.clear();
          await authService.logout();
          throw Exception('Session expired. Please log in again.');
        }
      } catch (e) {
        debugPrint('Error during token refresh: $e');
        _isRefreshing = false;
        _pendingRequests.clear();
        await authService.logout();
        throw Exception('Session expired. Please log in again.');
      }
    }

    return response;
  }

  /// Queue a request while token is being refreshed
  Future<http.Response> _queueRequest(Future<http.Response> Function() request) async {
    final completer = Future<http.Response>.delayed(Duration.zero);
    _pendingRequests.add(() async {
      return await request();
    });
    
    // Wait a bit and retry (simple approach)
    await Future.delayed(const Duration(milliseconds: 100));
    return await request();
  }
}
