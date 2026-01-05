import 'package:flutter/material.dart';
import '../models/warehouse.dart';
import '../services/api_client.dart';
import '../services/warehouse_service.dart';

/// A cascading selector widget for choosing Warehouse > Location > Container
class ContainerSelector extends StatefulWidget {
  final String? value; // Selected container ref
  final ValueChanged<String?>? onChanged;
  final ApiClient apiClient;
  final String? labelText;
  final bool enabled;

  const ContainerSelector({
    Key? key,
    this.value,
    this.onChanged,
    required this.apiClient,
    this.labelText = 'Select Container',
    this.enabled = true,
  }) : super(key: key);

  @override
  State<ContainerSelector> createState() => _ContainerSelectorState();
}

class _ContainerSelectorState extends State<ContainerSelector> {
  List<Warehouse> warehouses = [];
  List<Warehouse> locations = [];
  List<Warehouse> containers = [];
  
  String? selectedWarehouseId;
  String? selectedLocationId;
  String? selectedContainerRef;
  
  bool isLoadingWarehouses = false;
  bool isLoadingLocations = false;
  bool isLoadingContainers = false;
  
  String? error;

  @override
  void initState() {
    super.initState();
    _loadWarehouses();
    if (widget.value != null) {
      _initializeFromValue();
    }
  }

  Future<void> _initializeFromValue() async {
    if (widget.value == null) return;
    
    try {
      // Find the container with this ref
      final allWarehouses = await WarehouseService.getWarehouses(widget.apiClient);
      final container = allWarehouses.firstWhere(
        (w) => w.ref == widget.value,
        orElse: () => throw Exception('Container not found'),
      );
      
      // Get the hierarchy path
      final path = await WarehouseService.getHierarchyPath(
        widget.apiClient,
        container.id,
      );
      
      if (path.isNotEmpty) {
        final warehouse = path.first;
        selectedWarehouseId = warehouse.id;
        await _loadLocations(warehouse.id);
        
        if (path.length > 1) {
          final location = path[1];
          selectedLocationId = location.id;
          await _loadContainers(location.id);
          
          if (path.length > 2) {
            selectedContainerRef = path[2].ref;
          }
        }
      }
    } catch (e) {
      setState(() {
        error = 'Failed to initialize: $e';
      });
    }
  }

  Future<void> _loadWarehouses() async {
    setState(() {
      isLoadingWarehouses = true;
      error = null;
    });

    try {
      final result = await WarehouseService.getWarehousesByType(
        widget.apiClient,
        WarehouseType.warehouse,
      );
      setState(() {
        warehouses = result.where((w) => w.status && !w.deleted).toList();
        isLoadingWarehouses = false;
        
        // Auto-select if only one warehouse
        if (warehouses.length == 1 && selectedWarehouseId == null) {
          selectedWarehouseId = warehouses.first.id;
          _loadLocations(selectedWarehouseId!);
        }
      });
    } catch (e) {
      setState(() {
        error = 'Failed to load warehouses: $e';
        isLoadingWarehouses = false;
      });
    }
  }

  Future<void> _loadLocations(String warehouseId) async {
    setState(() {
      isLoadingLocations = true;
      locations = [];
      containers = [];
      selectedLocationId = null;
      selectedContainerRef = null;
      error = null;
    });

    try {
      final result = await WarehouseService.getChildren(
        widget.apiClient,
        warehouseId,
      );
      setState(() {
        locations = result.where((w) => w.status && !w.deleted).toList();
        isLoadingLocations = false;
        
        // Auto-select if only one location
        if (locations.length == 1 && selectedLocationId == null) {
          selectedLocationId = locations.first.id;
          _loadContainers(selectedLocationId!);
        }
      });
    } catch (e) {
      setState(() {
        error = 'Failed to load locations: $e';
        isLoadingLocations = false;
      });
    }
  }

  Future<void> _loadContainers(String locationId) async {
    setState(() {
      isLoadingContainers = true;
      containers = [];
      selectedContainerRef = null;
      error = null;
    });

    try {
      final result = await WarehouseService.getChildren(
        widget.apiClient,
        locationId,
      );
      setState(() {
        containers = result.where((w) => w.status && !w.deleted).toList();
        isLoadingContainers = false;
        
        // Auto-select if only one container
        if (containers.length == 1 && selectedContainerRef == null) {
          selectedContainerRef = containers.first.ref;
          widget.onChanged?.call(selectedContainerRef);
        }
      });
    } catch (e) {
      setState(() {
        error = 'Failed to load containers: $e';
        isLoadingContainers = false;
      });
    }
  }

  String _getFullPath() {
    final parts = <String>[];
    
    if (selectedWarehouseId != null) {
      final warehouse = warehouses.firstWhere(
        (w) => w.id == selectedWarehouseId,
        orElse: () => throw Exception('Warehouse not found'),
      );
      parts.add(warehouse.label);
    }
    
    if (selectedLocationId != null) {
      final location = locations.firstWhere(
        (l) => l.id == selectedLocationId,
        orElse: () => throw Exception('Location not found'),
      );
      parts.add(location.label);
    }
    
    if (selectedContainerRef != null) {
      final container = containers.firstWhere(
        (c) => c.ref == selectedContainerRef,
        orElse: () => throw Exception('Container not found'),
      );
      parts.add(container.label);
    }
    
    return parts.join(' > ');
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.labelText != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Text(
              widget.labelText!,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
        
        // Warehouse selector
        DropdownButtonFormField<String>(
          decoration: const InputDecoration(
            labelText: 'Warehouse',
            border: OutlineInputBorder(),
          ),
          value: selectedWarehouseId,
          items: warehouses.map((warehouse) {
            return DropdownMenuItem(
              value: warehouse.id,
              child: Text(warehouse.label),
            );
          }).toList(),
          onChanged: widget.enabled
              ? (value) {
                  if (value != null) {
                    setState(() {
                      selectedWarehouseId = value;
                    });
                    _loadLocations(value);
                  }
                }
              : null,
        ),
        
        const SizedBox(height: 12),
        
        // Location selector
        DropdownButtonFormField<String>(
          decoration: const InputDecoration(
            labelText: 'Location',
            border: OutlineInputBorder(),
          ),
          value: selectedLocationId,
          items: locations.map((location) {
            return DropdownMenuItem(
              value: location.id,
              child: Text(location.label),
            );
          }).toList(),
          onChanged: widget.enabled && selectedWarehouseId != null
              ? (value) {
                  if (value != null) {
                    setState(() {
                      selectedLocationId = value;
                    });
                    _loadContainers(value);
                  }
                }
              : null,
        ),
        
        const SizedBox(height: 12),
        
        // Container selector
        DropdownButtonFormField<String>(
          decoration: const InputDecoration(
            labelText: 'Container',
            border: OutlineInputBorder(),
          ),
          value: selectedContainerRef,
          items: containers.map((container) {
            return DropdownMenuItem(
              value: container.ref,
              child: Row(
                children: [
                  Text(container.label),
                  if (container.containerType != null) ...[
                    const SizedBox(width: 8),
                    Chip(
                      label: Text(
                        container.containerType!.displayName,
                        style: const TextStyle(fontSize: 10),
                      ),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ],
                ],
              ),
            );
          }).toList(),
          onChanged: widget.enabled && selectedLocationId != null
              ? (value) {
                  setState(() {
                    selectedContainerRef = value;
                  });
                  widget.onChanged?.call(value);
                }
              : null,
        ),
        
        // Full path display
        if (selectedContainerRef != null) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceVariant,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.location_on,
                  size: 16,
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _getFullPath(),
                    style: TextStyle(
                      fontSize: 12,
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
        
        // Error display
        if (error != null) ...[
          const SizedBox(height: 8),
          Text(
            error!,
            style: TextStyle(
              color: Theme.of(context).colorScheme.error,
              fontSize: 12,
            ),
          ),
        ],
        
        // Loading indicators
        if (isLoadingWarehouses || isLoadingLocations || isLoadingContainers) ...[
          const SizedBox(height: 8),
          const LinearProgressIndicator(),
        ],
      ],
    );
  }
}
