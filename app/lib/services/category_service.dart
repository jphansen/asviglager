import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';
import '../models/item.dart';
import 'api_client.dart';

class CategoryService {
  final ApiClient apiClient;
  static const String _prefsKey = 'cached_categories';
  static List<String>? _cachedCategories;

  CategoryService(this.apiClient);

  Future<List<String>> getCategories() async {
    if (_cachedCategories != null && _cachedCategories!.isNotEmpty) {
      return _cachedCategories!;
    }

    await _loadFromPrefs();

    try {
      final url = '${ApiConfig.baseUrl}${ApiConfig.categories}';
      final response = await apiClient.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        _cachedCategories = data.cast<String>();
        await _saveToPrefs();
        return _cachedCategories!;
      }
    } catch (e) {
    }

    if (_cachedCategories == null || _cachedCategories!.isEmpty) {
      _cachedCategories = [];
    }

    return _cachedCategories!;
  }

  Future<List<String>> extractCategoriesFromItems(List<Item> items) async {
    final categories = <String>{};
    for (final item in items) {
      if (item.category != null && item.category!.isNotEmpty) {
        categories.add(item.category!);
      }
    }

    if (categories.isNotEmpty) {
      if (_cachedCategories == null) {
        await _loadFromPrefs();
      }
      for (final category in categories) {
        if (!_cachedCategories!.contains(category)) {
          _cachedCategories!.add(category);
        }
      }
      _cachedCategories!.sort();
      await _saveToPrefs();
    }

    return _cachedCategories ?? [];
  }

  static Future<void> addToCache(String category) async {
    if (category.isEmpty) return;

    if (_cachedCategories == null) {
      await _loadFromPrefs();
    }

    if (!_cachedCategories!.contains(category)) {
      _cachedCategories!.add(category);
      _cachedCategories!.sort();
      await _saveToPrefs();
    }
  }

  static Future<void> _loadFromPrefs() async {
    if (_cachedCategories != null) return;

    final prefs = await SharedPreferences.getInstance();
    final categoriesJson = prefs.getString(_prefsKey);
    if (categoriesJson != null) {
      _cachedCategories = List<String>.from(json.decode(categoriesJson));
    } else {
      _cachedCategories = [];
    }
  }

  static Future<void> _saveToPrefs() async {
    if (_cachedCategories == null) return;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, json.encode(_cachedCategories!));
  }
}
