import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../config/api_config.dart';

class AuthService extends ChangeNotifier {
  String? _token;
  String? _refreshToken;
  bool _isLoading = true;
  String? _username;

  bool get isAuthenticated => _token != null;
  bool get isLoading => _isLoading;
  String? get token => _token;
  String? get refreshToken => _refreshToken;
  String? get username => _username;

  AuthService() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString('auth_token');
      _refreshToken = prefs.getString('refresh_token');
      _username = prefs.getString('username');
    } catch (e) {
      debugPrint('Error loading token: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.login}'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': username,
          'password': password,
        },
      ).timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['access_token'];
        _refreshToken = data['refresh_token'];
        _username = username;

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', _token!);
        if (_refreshToken != null) {
          await prefs.setString('refresh_token', _refreshToken!);
        }
        await prefs.setString('username', username);

        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Login error: $e');
      return false;
    }
  }

  Future<void> logout() async {
    _token = null;
    _refreshToken = null;
    _username = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('refresh_token');
    await prefs.remove('username');

    notifyListeners();
  }

  /// Refresh the access token using the refresh token
  Future<bool> refreshAccessToken() async {
    if (_refreshToken == null) {
      debugPrint('No refresh token available');
      return false;
    }

    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}${ApiConfig.refreshToken}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'refresh_token': _refreshToken,
        }),
      ).timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['access_token'];

        // Save new access token
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', _token!);

        notifyListeners();
        debugPrint('Access token refreshed successfully');
        return true;
      } else {
        debugPrint('Token refresh failed with status: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('Error refreshing token: $e');
      return false;
    }
  }
}
