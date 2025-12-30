import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/product_service.dart';
import '../services/warehouse_service.dart';
import '../models/product.dart';
import '../models/warehouse.dart';

class StockScreen extends StatefulWidget {
  const StockScreen({super.key});

  @override
  State<StockScreen> createState() => _StockScreenState();
}

class _StockScreenState extends State<StockScreen> {
  List<Product> _products = [];
  List<Warehouse> _warehouses = [];
  List<Product> _filteredProducts = [];
  bool _isLoading = true;
  String _error = '';
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
    _searchController.addListener(_filterProducts);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final token = authService.token!;

      final productService = ProductService(token);
      final products = await productService.getProducts(limit: 1000);
      final warehouses = await WarehouseService.getWarehouses(token);

      setState(() {
        _products = products;
        _warehouses = warehouses.where((w) => w.status && !w.deleted).toList();
        _filteredProducts = products;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _filterProducts() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      if (query.isEmpty) {
        _filteredProducts = _products;
      } else {
        _filteredProducts = _products.where((product) {
          return product.ref.toLowerCase().contains(query) ||
              product.label.toLowerCase().contains(query) ||
              (product.barcode?.toLowerCase().contains(query) ?? false);
        }).toList();
      }
    });
  }

  String _getWarehouseLabel(String warehouseRef) {
    final warehouse = _warehouses.firstWhere(
      (w) => w.ref == warehouseRef,
      orElse: () => Warehouse(
        id: '',
        ref: warehouseRef,
        label: warehouseRef,
        status: false,
        deleted: true,
        dateCreation: DateTime.now(),
        dateModification: DateTime.now(),
      ),
    );
    return warehouse.label;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Stock Management'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search by reference, name, or barcode...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                        },
                      )
                    : null,
              ),
            ),
          ),
          Expanded(
            child: _buildBody(),
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Error loading data',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              _error,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadData,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_filteredProducts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.inventory_2_outlined,
              size: 64,
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
            ),
            const SizedBox(height: 16),
            Text(
              _searchController.text.isEmpty
                  ? 'No products available'
                  : 'No products found',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                  ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: _filteredProducts.length,
        itemBuilder: (context, index) {
          final product = _filteredProducts[index];
          return _buildProductCard(product);
        },
      ),
    );
  }

  Widget _buildProductCard(Product product) {
    final totalStock = product.getTotalStock();
    final hasStock = product.stockWarehouse != null && product.stockWarehouse!.isNotEmpty;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showStockDialog(product),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          product.label,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          product.ref,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Theme.of(context).colorScheme.primary,
                              ),
                        ),
                        if (product.barcode != null) ...[
                          const SizedBox(height: 2),
                          Text(
                            product.barcode!,
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                                ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: totalStock > 0
                          ? Colors.green.withOpacity(0.2)
                          : Colors.grey.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '$totalStock',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: totalStock > 0 ? Colors.green : Colors.grey,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                ],
              ),
              if (hasStock) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: product.stockWarehouse!.entries.map((entry) {
                    return Chip(
                      label: Text(
                        '${_getWarehouseLabel(entry.key)}: ${entry.value.items.toInt()}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    );
                  }).toList(),
                ),
              ] else ...[
                const SizedBox(height: 8),
                Text(
                  'No stock locations',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                        fontStyle: FontStyle.italic,
                      ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showStockDialog(Product product) {
    showDialog(
      context: context,
      builder: (context) => _StockEditDialog(
        product: product,
        warehouses: _warehouses,
        onStockUpdated: _loadData,
      ),
    );
  }
}

class _StockEditDialog extends StatefulWidget {
  final Product product;
  final List<Warehouse> warehouses;
  final VoidCallback onStockUpdated;

  const _StockEditDialog({
    required this.product,
    required this.warehouses,
    required this.onStockUpdated,
  });

  @override
  State<_StockEditDialog> createState() => _StockEditDialogState();
}

class _StockEditDialogState extends State<_StockEditDialog> {
  String? _selectedWarehouse;
  final TextEditingController _stockController = TextEditingController();
  bool _isUpdating = false;
  String _error = '';

  @override
  void dispose() {
    _stockController.dispose();
    super.dispose();
  }

  Future<void> _updateStock() async {
    if (_selectedWarehouse == null) {
      setState(() => _error = 'Please select a warehouse');
      return;
    }

    final items = double.tryParse(_stockController.text);
    if (items == null || items < 0) {
      setState(() => _error = 'Please enter a valid stock amount (0 or greater)');
      return;
    }

    setState(() {
      _isUpdating = true;
      _error = '';
    });

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final productService = ProductService(authService.token!);

      await productService.updateStock(widget.product.id, _selectedWarehouse!, items);

      if (mounted) {
        widget.onStockUpdated();
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Stock updated successfully')),
        );
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isUpdating = false;
      });
    }
  }

  Future<void> _removeStock(String warehouseRef) async {
    setState(() {
      _isUpdating = true;
      _error = '';
    });

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final productService = ProductService(authService.token!);

      await productService.removeStock(widget.product.id, warehouseRef);

      if (mounted) {
        widget.onStockUpdated();
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Stock location removed')),
        );
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isUpdating = false;
      });
    }
  }

  String _getWarehouseLabel(String warehouseRef) {
    final warehouse = widget.warehouses.firstWhere(
      (w) => w.ref == warehouseRef,
      orElse: () => Warehouse(
        id: '',
        ref: warehouseRef,
        label: warehouseRef,
        status: false,
        deleted: true,
        dateCreation: DateTime.now(),
        dateModification: DateTime.now(),
      ),
    );
    return warehouse.label;
  }

  @override
  Widget build(BuildContext context) {
    final currentStock = widget.product.stockWarehouse ?? {};

    return AlertDialog(
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Manage Stock'),
          const SizedBox(height: 4),
          Text(
            widget.product.label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                  fontWeight: FontWeight.normal,
                ),
          ),
          Text(
            widget.product.ref,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                ),
          ),
        ],
      ),
      content: SingleChildScrollView(
        child: SizedBox(
          width: double.maxFinite,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_error.isNotEmpty) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.errorContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _error,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],
              Text(
                'Current Stock Locations',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              if (currentStock.isEmpty)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.info_outline),
                      SizedBox(width: 8),
                      Text('No stock locations configured'),
                    ],
                  ),
                )
              else
                ...currentStock.entries.map((entry) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _getWarehouseLabel(entry.key),
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                              Text(
                                'Ref: ${entry.key}',
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                                    ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Stock: ${entry.value.items.toInt()} items',
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: Theme.of(context).colorScheme.primary,
                                    ),
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.delete),
                          color: Theme.of(context).colorScheme.error,
                          onPressed: _isUpdating
                              ? null
                              : () async {
                                  final confirmed = await showDialog<bool>(
                                    context: context,
                                    builder: (context) => AlertDialog(
                                      title: const Text('Remove Stock Location'),
                                      content: Text(
                                        'Remove stock location: ${_getWarehouseLabel(entry.key)}?',
                                      ),
                                      actions: [
                                        TextButton(
                                          onPressed: () => Navigator.pop(context, false),
                                          child: const Text('Cancel'),
                                        ),
                                        TextButton(
                                          onPressed: () => Navigator.pop(context, true),
                                          child: const Text('Remove'),
                                        ),
                                      ],
                                    ),
                                  );
                                  if (confirmed == true) {
                                    _removeStock(entry.key);
                                  }
                                },
                        ),
                      ],
                    ),
                  );
                }),
              const SizedBox(height: 16),
              Text(
                'Add or Update Stock',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedWarehouse,
                decoration: const InputDecoration(
                  labelText: 'Warehouse',
                ),
                items: widget.warehouses.map((warehouse) {
                  return DropdownMenuItem(
                    value: warehouse.ref,
                    child: Text('${warehouse.label} (${warehouse.ref})'),
                  );
                }).toList(),
                onChanged: _isUpdating
                    ? null
                    : (value) {
                        setState(() => _selectedWarehouse = value);
                      },
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _stockController,
                decoration: const InputDecoration(
                  labelText: 'Stock Amount',
                ),
                keyboardType: TextInputType.number,
                enabled: !_isUpdating,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isUpdating ? null : () => Navigator.pop(context),
          child: const Text('Close'),
        ),
        ElevatedButton.icon(
          onPressed: _isUpdating ? null : _updateStock,
          icon: _isUpdating
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.add),
          label: Text(
            _selectedWarehouse != null && currentStock.containsKey(_selectedWarehouse)
                ? 'Update'
                : 'Add',
          ),
        ),
      ],
    );
  }
}
