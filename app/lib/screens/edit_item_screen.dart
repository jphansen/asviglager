import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../models/item.dart';
import '../models/photo.dart';
import '../services/auth_service.dart';
import '../services/item_service.dart';
import '../services/photo_service.dart';
import '../services/category_service.dart';
import '../services/api_client.dart';
import '../widgets/container_selector.dart';
import '../utils/container_memory.dart';

class EditItemScreen extends StatefulWidget {
  final Item item;

  const EditItemScreen({super.key, required this.item});

  @override
  State<EditItemScreen> createState() => _EditItemScreenState();
}

class _EditItemScreenState extends State<EditItemScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _refController;
  late final TextEditingController _nameController;
  late final TextEditingController _priceController;
  late final TextEditingController _barcodeController;
  late final TextEditingController _descriptionController;
  
  List<String> _existingPhotoIds = [];
  List<Photo> _existingPhotos = [];
  List<String> _categories = [];
  TextEditingController? _categoryFieldController;
  bool _isLoading = false;
  bool _isUploadingPhoto = false;
  String? _selectedContainerRef;

  @override
  void initState() {
    super.initState();
    _refController = TextEditingController(text: widget.item.ref);
    _nameController = TextEditingController(text: widget.item.label);
    _priceController = TextEditingController(
      text: widget.item.price > 0 ? widget.item.price.toString() : '',
    );
    _barcodeController = TextEditingController(text: widget.item.barcode ?? '');
    _descriptionController = TextEditingController(text: widget.item.description ?? '');
    
    if (widget.item.stockWarehouse != null && widget.item.stockWarehouse!.isNotEmpty) {
      _selectedContainerRef = widget.item.stockWarehouse!.keys.first;
    }
    
    if (widget.item.photos != null && widget.item.photos!.isNotEmpty) {
      _existingPhotoIds = List.from(widget.item.photos!);
      _loadExistingPhotos();
    }
    
    _loadCategories();
  }

  @override
  void dispose() {
    _refController.dispose();
    _nameController.dispose();
    _priceController.dispose();
    _barcodeController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _loadCategories() async {
    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final categoryService = CategoryService(apiClient);
      var categories = await categoryService.getCategories();
      
      if (categories.isEmpty) {
        final itemService = ItemService(apiClient);
        final items = await itemService.getItems(limit: 100);
        categories = await categoryService.extractCategoriesFromItems(items);
      }
      
      if (mounted) {
        setState(() {
          _categories = categories;
        });
      }
    } catch (e) {
      // Silently fail
    }
  }

  Future<void> _loadExistingPhotos() async {
    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final photoService = PhotoService(apiClient);
      
      final photos = <Photo>[];
      for (final photoId in _existingPhotoIds) {
        try {
          final photo = await photoService.getPhoto(photoId);
          photos.add(photo);
        } catch (e) {
          // Skip photos that fail to load
        }
      }
      
      if (mounted) {
        setState(() {
          _existingPhotos = photos;
        });
      }
    } catch (e) {
      // Silently handle error
    }
  }

  Future<void> _takePicture() async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? photo = await picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 800,
        maxHeight: 600,
        imageQuality: 60,
      );

      if (photo != null) {
        final imageFile = File(photo.path);
        setState(() {
          _isUploadingPhoto = true;
        });

        try {
          final authService = Provider.of<AuthService>(context, listen: false);
          final apiClient = ApiClient(authService);
          final photoService = PhotoService(apiClient);
          
          final bytes = await imageFile.readAsBytes();
          final base64Image = base64Encode(bytes);
          
          final sizeInMB = bytes.length / (1024 * 1024);
          if (sizeInMB > 2) {
            throw Exception('Image too large (${sizeInMB.toStringAsFixed(1)}MB). Please try again.');
          }
          
          final uploadedPhoto = await photoService.uploadPhoto(
            filename: photo.name,
            contentType: 'image/jpeg',
            base64Data: base64Image,
            description: 'Item photo',
          );
          
          await photoService.addPhotoToProduct(widget.item.id, uploadedPhoto.id);
          
          if (mounted) {
            setState(() {
              _existingPhotoIds.add(uploadedPhoto.id);
              _existingPhotos.add(uploadedPhoto);
              _isUploadingPhoto = false;
            });
            
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Photo uploaded and added to item'),
                backgroundColor: Colors.green,
                duration: Duration(seconds: 2),
              ),
            );
          }
        } catch (e) {
          if (mounted) {
            setState(() => _isUploadingPhoto = false);
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error uploading photo: $e'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error taking picture: $e')),
        );
      }
    }
  }

  Future<void> _showPhotoOptions(int index) async {
    final photoId = _existingPhotoIds[index];
    
    final action = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Photo Options'),
        content: const Text('Choose an action for this photo:'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, null),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, 'unlink'),
            child: const Text('Unlink from Item'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, 'delete'),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete Permanently'),
          ),
        ],
      ),
    );
    
    if (action == null) return;
    
    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final photoService = PhotoService(apiClient);
      
      if (action == 'delete') {
        await photoService.deletePhoto(photoId);
        
        if (mounted) {
          setState(() {
            _existingPhotoIds.removeAt(index);
            _existingPhotos.removeAt(index);
          });
          
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Photo deleted permanently'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else if (action == 'unlink') {
        await photoService.removePhotoFromProduct(widget.item.id, photoId);
        
        if (mounted) {
          setState(() {
            _existingPhotoIds.removeAt(index);
            _existingPhotos.removeAt(index);
          });
          
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Photo unlinked from item (photo kept in database)'),
              backgroundColor: Colors.green,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _scanBarcode() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const BarcodeScannerScreen(),
      ),
    );

    if (result != null && mounted) {
      setState(() {
        _barcodeController.text = result;
      });
    }
  }

  Future<void> _saveItem() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final apiClient = ApiClient(authService);
      final itemService = ItemService(apiClient);

      double? price;
      if (_priceController.text.isNotEmpty) {
        price = double.tryParse(_priceController.text);
        if (price == null) {
          throw Exception('Invalid price format');
        }
      }

      final category = _categoryFieldController?.text.trim() ?? '';
      if (category.isNotEmpty) {
        await CategoryService.addToCache(category);
      }

      final updatedItem = Item(
        id: widget.item.id,
        ref: _refController.text.trim(),
        label: _nameController.text.trim(),
        category: category.isNotEmpty ? category : null,
        price: price ?? 0.0,
        barcode: _barcodeController.text.trim().isEmpty ? null : _barcodeController.text.trim(),
        description: _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        type: widget.item.type,
        status: widget.item.status,
        statusBuy: widget.item.statusBuy,
        deleted: widget.item.deleted,
        dateCreation: widget.item.dateCreation,
        dateModification: DateTime.now(),
      );

      await itemService.updateItem(widget.item.id, updatedItem);

      if (_selectedContainerRef != null) {
        try {
          await itemService.updateStock(widget.item.id, _selectedContainerRef!, 1);
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Item updated but container association failed: $e'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Item updated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error updating item: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Uint8List _base64ToImage(String base64String) {
    return base64Decode(base64String);
  }

  Future<void> _deleteItem() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Item'),
        content: Text('Are you sure you want to delete "${widget.item.label}"? This action cannot be undone.'),
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
      
      await itemService.deleteItem(widget.item.id);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Item deleted successfully'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Item'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            onSelected: (value) async {
              if (value == 'delete') {
                await _deleteItem();
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
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_existingPhotos.isNotEmpty) ...[
                Row(
                  children: [
                    const Text(
                      'Item Photos',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '(${_existingPhotos.length})',
                      style: TextStyle(
                        fontSize: 14,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                SizedBox(
                  height: 120,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: _existingPhotos.length,
                    itemBuilder: (context, index) {
                      final photo = _existingPhotos[index];
                      return GestureDetector(
                        onLongPress: () => _showPhotoOptions(index),
                        child: Stack(
                          children: [
                            Container(
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
                            Positioned(
                              top: 4,
                              right: 12,
                              child: GestureDetector(
                                onTap: () => _showPhotoOptions(index),
                                child: Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(
                                    color: Colors.red,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.delete,
                                    color: Colors.white,
                                    size: 16,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 24),
              ],

              GestureDetector(
                onTap: _isUploadingPhoto ? null : _takePicture,
                child: Container(
                  height: 120,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                      width: 2,
                      style: BorderStyle.solid,
                    ),
                  ),
                  child: _isUploadingPhoto
                      ? Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const CircularProgressIndicator(),
                            const SizedBox(height: 12),
                            Text(
                              'Uploading photo...',
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                                fontSize: 14,
                              ),
                            ),
                          ],
                        )
                      : Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.add_a_photo_rounded,
                              size: 32,
                              color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Add New Photo',
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                ),
              ),
              const SizedBox(height: 24),

              TextFormField(
                controller: _refController,
                decoration: const InputDecoration(
                  labelText: 'Item ID / Reference',
                  prefixIcon: Icon(Icons.tag_rounded),
                ),
                enabled: false,
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Item Name *',
                  prefixIcon: Icon(Icons.inventory_2_rounded),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Item name is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              Autocomplete<String>(
                optionsBuilder: (TextEditingValue textEditingValue) {
                  if (textEditingValue.text.isEmpty) {
                    return const Iterable<String>.empty();
                  }
                  return _categories.where((String category) {
                    return category.toLowerCase().contains(textEditingValue.text.toLowerCase());
                  });
                },
                onSelected: (String selection) {
                  setState(() {
                    _categoryFieldController?.text = selection;
                  });
                },
                initialValue: TextEditingValue(text: widget.item.category ?? ''),
                fieldViewBuilder: (context, controller, focusNode, onFieldSubmitted) {
                  _categoryFieldController = controller;
                  return TextFormField(
                    controller: controller,
                    focusNode: focusNode,
                    decoration: const InputDecoration(
                      labelText: 'Category (optional)',
                      prefixIcon: Icon(Icons.category_rounded),
                      helperText: 'Select from list or type new category',
                    ),
                  );
                },
                optionsViewBuilder: (context, onSelected, options) {
                  return Align(
                    alignment: Alignment.topLeft,
                    child: Material(
                      elevation: 4,
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxHeight: 200),
                        child: ListView(
                          padding: EdgeInsets.zero,
                          shrinkWrap: true,
                          children: options.map((String category) {
                            return InkWell(
                              onTap: () => onSelected(category),
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Text(category),
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _barcodeController,
                decoration: InputDecoration(
                  labelText: 'Barcode',
                  prefixIcon: const Icon(Icons.qr_code_rounded),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.qr_code_scanner_rounded),
                    onPressed: _scanBarcode,
                    tooltip: 'Scan barcode',
                  ),
                ),
              ),
              const SizedBox(height: 16),

              ContainerSelector(
                value: _selectedContainerRef ?? ContainerMemory.lastContainerRef,
                onChanged: (value) {
                  setState(() => _selectedContainerRef = value);
                  ContainerMemory.lastContainerRef = value;
                },
                apiClient: ApiClient(Provider.of<AuthService>(context, listen: false)),
                labelText: 'Container (optional)',
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _priceController,
                decoration: const InputDecoration(
                  labelText: 'Selling Price',
                  prefixIcon: Icon(Icons.attach_money_rounded),
                  suffixText: 'DKK',
                ),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  prefixIcon: Icon(Icons.notes_rounded),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24),

              ElevatedButton(
                onPressed: _isLoading ? null : _saveItem,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF4CAF50),
                  foregroundColor: Colors.white,
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text('Update Item', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class BarcodeScannerScreen extends StatefulWidget {
  const BarcodeScannerScreen({super.key});

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  final MobileScannerController _controller = MobileScannerController();
  bool _hasScanned = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleBarcode(String barcode) {
    if (_hasScanned) return;
    _hasScanned = true;
    _controller.stop();
    Navigator.pop(context, barcode);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Barcode'),
        actions: [
          IconButton(
            icon: const Icon(Icons.flash_on),
            onPressed: () => _controller.toggleTorch(),
          ),
        ],
      ),
      body: MobileScanner(
        controller: _controller,
        onDetect: (capture) {
          final List<Barcode> barcodes = capture.barcodes;
          if (barcodes.isNotEmpty && !_hasScanned) {
            final barcode = barcodes.first.rawValue;
            if (barcode != null) {
              _handleBarcode(barcode);
            }
          }
        },
      ),
    );
  }
}
