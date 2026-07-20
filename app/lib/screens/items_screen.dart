import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/item.dart';
import '../models/photo.dart';
import '../services/auth_service.dart';
import '../services/item_service.dart';
import '../services/photo_service.dart';
import '../services/warehouse_service.dart';
import '../services/api_client.dart';
import 'edit_item_screen.dart';

class ItemsScreen extends StatefulWidget {
  const ItemsScreen({super.key});

  @override
  State<ItemsScreen> createState() => _ItemsScreenState();
}

class _ItemsScreenState extends State<ItemsScreen> {
  List<Item> _items = [];
  List<Item> _filteredItems = [];
  bool _isLoading = true;
  String? _error;
  final TextEditingController _searchController = TextEditingController();
  Map<String, String> _containerPaths = {};

  @override
  void initState() {
    super.initState();
    _loadItems();
    _searchController.addListener(_filterItems);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadItems({String? search}) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final itemService = ItemService(apiClient);
      final items = await itemService.getItems(limit: 100, search: search);

      if (mounted) {
        setState(() {
          _items = items;
          _filteredItems = items;
          _isLoading = false;
        });
        _loadContainerPaths(items);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  void _filterItems() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      if (query.isEmpty) {
        _filteredItems = _items;
      } else {
        _filteredItems = _items.where((item) {
          if (item.ref.toLowerCase().contains(query)) return true;
          if (item.label.toLowerCase().contains(query)) return true;
          if (item.barcode?.toLowerCase().contains(query) ?? false) return true;
          if (item.category?.toLowerCase().contains(query) ?? false) return true;
          
          final stock = item.stockWarehouse;
          if (stock != null && stock.isNotEmpty) {
            for (final containerRef in stock.keys) {
              if (containerRef.toLowerCase().contains(query)) return true;
              if (_containerPaths[containerRef]?.toLowerCase().contains(query) ?? false) {
                return true;
              }
            }
          }
          return false;
        }).toList();
      }
    });
  }

  Future<void> _loadContainerPaths(List<Item> items) async {
    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final allWarehouses = await WarehouseService.getWarehouses(apiClient);

      final paths = <String, String>{};
      
      for (final item in items) {
        final stock = item.stockWarehouse;
        if (stock == null || stock.isEmpty) continue;
        for (final containerRef in stock.keys) {
          if (paths.containsKey(containerRef)) continue;
          try {
            final container = allWarehouses.firstWhere(
              (w) => w.ref == containerRef,
              orElse: () => throw Exception('Container not found'),
            );
            final hierarchyPath = await WarehouseService.getHierarchyPath(
              apiClient,
              container.id,
            );
            paths[containerRef] = hierarchyPath.map((w) => w.label).join(' > ');
          } catch (_) {
            paths[containerRef] = containerRef;
          }
        }
      }

      if (mounted) {
        setState(() {
          _containerPaths = paths;
        });
        _filterItems();
      }
    } catch (_) {}
  }

  Future<void> _deleteItem(Item item) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Item'),
        content: Text('Are you sure you want to delete "${item.label}"? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final itemService = ItemService(apiClient);
      
      await itemService.deleteItem(item.id);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Item deleted successfully'),
            backgroundColor: Colors.green,
          ),
        );
        _loadItems();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error deleting item: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  String _getContainerLabel(Item item) {
    final stock = item.stockWarehouse;
    if (stock == null || stock.isEmpty) return '';
    final ref = stock.keys.first;
    return _containerPaths[ref] ?? ref;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Items'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search items, containers, locations...',
                prefixIcon: Icon(
                  Icons.search_rounded,
                  color: Theme.of(context).colorScheme.primary,
                ),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear_rounded),
                        onPressed: () {
                          _searchController.clear();
                          _filterItems();
                        },
                      )
                    : null,
              ),
            ),
          ),
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text('Error: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadItems,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_filteredItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.inventory_2_outlined,
              size: 64,
              color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
            ),
            const SizedBox(height: 16),
            Text(
              'No items found',
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadItems,
      child: ListView.builder(
        itemCount: _filteredItems.length,
        itemBuilder: (context, index) {
          final item = _filteredItems[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              leading: _buildLeadingThumbnail(item),
              title: Text(
                item.label,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              subtitle: Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Row(
                  children: [
                    Expanded(
                      child: (() {
                        final containerLabel = _getContainerLabel(item);
                        final containerPart = containerLabel.isNotEmpty ? ' • $containerLabel' : '';
                        final categoryPart = item.category != null && item.category!.isNotEmpty ? ' • ${item.category}' : '';
                        return Text(
                          '${item.ref}$containerPart$categoryPart • ${item.price.toStringAsFixed(2)} DKK',
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                          ),
                        );
                      })(),
                    ),
                    if (item.photos != null && item.photos!.isNotEmpty)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.secondary.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.photo_library,
                              size: 12,
                              color: Theme.of(context).colorScheme.secondary,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '${item.photos!.length}',
                              style: TextStyle(
                                fontSize: 11,
                                color: Theme.of(context).colorScheme.secondary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (item.barcode != null)
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.qr_code_rounded,
                        size: 20,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  const SizedBox(width: 8),
                  PopupMenuButton<String>(
                    icon: const Icon(Icons.more_vert),
                    onSelected: (value) async {
                      if (value == 'delete') {
                        await _deleteItem(item);
                      }
                    },
                    itemBuilder: (BuildContext context) => [
                      const PopupMenuItem<String>(
                        value: 'delete',
                        child: Row(
                          children: [
                            Icon(Icons.delete, color: Colors.red),
                            SizedBox(width: 8),
                            Text('Delete Item', style: TextStyle(color: Colors.red)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              onTap: () => _showItemDetails(item),
            ),
          );
        },
      ),
    );
  }

  Widget _buildLeadingThumbnail(Item item) {
    if (item.photos != null && item.photos!.isNotEmpty) {
      return FutureBuilder<Photo>(
        future: _loadPhoto(item.photos!.first),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            );
          }

          if (snapshot.hasError || !snapshot.hasData) {
            return _buildFallbackIcon(item);
          }

          final photo = snapshot.data!;
          return ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.memory(
              _base64ToImage(photo.data),
              width: 48,
              height: 48,
              fit: BoxFit.cover,
            ),
          );
        },
      );
    }

    return _buildFallbackIcon(item);
  }

  Widget _buildFallbackIcon(Item item) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primary,
            Theme.of(context).colorScheme.secondary,
          ],
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        item.ref.substring(0, 2),
        style: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: 16,
        ),
      ),
    );
  }

  Future<Photo> _loadPhoto(String photoId) async {
    final authService = Provider.of<AuthService>(context, listen: false);
    final apiClient = ApiClient(authService);
    final photoService = PhotoService(apiClient);
    return await photoService.getPhoto(photoId);
  }

  Uint8List _base64ToImage(String base64String) {
    return base64Decode(base64String);
  }

  void _showItemDetails(Item item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(item.label),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (item.photos != null && item.photos!.isNotEmpty)
                _buildPhotoGallery(item.photos!),
              _DetailRow('Reference:', item.ref),
              if (item.category != null && item.category!.isNotEmpty)
                _DetailRow('Category:', item.category!),
              () {
                final containerLabel = _getContainerLabel(item);
                if (containerLabel.isNotEmpty) {
                  return _DetailRow('Container:', containerLabel);
                }
                return const SizedBox.shrink();
              }(),
              _DetailRow('Price:', '${item.price.toStringAsFixed(2)} DKK'),
              if (item.barcode != null)
                _DetailRow('Barcode:', item.barcode!),
              if (item.costPrice != null)
                _DetailRow('Cost:', '${item.costPrice!.toStringAsFixed(2)} DKK'),
              if (item.description != null && item.description!.isNotEmpty)
                _DetailRow('Description:', item.description!),
              _DetailRow('Status:', item.status == '1' ? 'Active' : 'Inactive'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton.icon(
            onPressed: () async {
              Navigator.pop(context);
              final result = await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => EditItemScreen(item: item),
                ),
              );
              if (result == true) {
                _loadItems();
              }
            },
            icon: const Icon(Icons.edit),
            label: const Text('Edit'),
          ),
        ],
      ),
    );
  }

  Widget _buildPhotoGallery(List<String> photoIds) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Photos:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 120,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: photoIds.map((photoId) => _buildPhotoThumbnail(photoId)).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPhotoThumbnail(String photoId) {
    return FutureBuilder<Photo>(
      future: _loadPhoto(photoId),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Container(
            width: 120,
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        if (snapshot.hasError || !snapshot.hasData) {
          return Container(
            width: 120,
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.broken_image_outlined,
              color: Colors.grey[400],
            ),
          );
        }

        final photo = snapshot.data!;
        return GestureDetector(
          onTap: () => _showFullPhoto(photo),
          child: Container(
            width: 120,
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              image: DecorationImage(
                image: MemoryImage(_base64ToImage(photo.data)),
                fit: BoxFit.cover,
              ),
            ),
          ),
        );
      },
    );
  }

  void _showFullPhoto(Photo photo) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Stack(
              children: [
                InteractiveViewer(
                  child: Image.memory(
                    _base64ToImage(photo.data),
                    fit: BoxFit.contain,
                  ),
                ),
                Positioned(
                  top: 8,
                  right: 8,
                  child: IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.black54,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
            if (photo.description != null && photo.description!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  photo.description!,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
