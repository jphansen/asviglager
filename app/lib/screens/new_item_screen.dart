import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../models/item.dart';
import '../services/auth_service.dart';
import '../services/item_service.dart';
import '../services/photo_service.dart';
import '../services/category_service.dart';
import '../services/api_client.dart';
import '../widgets/container_selector.dart';
import '../utils/container_memory.dart';

class NewItemScreen extends StatefulWidget {
  const NewItemScreen({super.key});

  @override
  State<NewItemScreen> createState() => _NewItemScreenState();
}

class _NewItemScreenState extends State<NewItemScreen> {
  final _formKey = GlobalKey<FormState>();
  final _refController = TextEditingController();
  final _nameController = TextEditingController();
  final _priceController = TextEditingController();
  final _barcodeController = TextEditingController();
  final _descriptionController = TextEditingController();
  
  File? _imageFile;
  String? _uploadedPhotoId;
  String? _selectedContainerRef;
  List<String> _categories = [];
  TextEditingController? _categoryFieldController;
  bool _isLoading = false;
  bool _isGeneratingId = false;
  bool _isUploadingPhoto = false;

  @override
  void initState() {
    super.initState();
    _generateItemId();
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

  void _generateItemId() {
    setState(() => _isGeneratingId = true);
    
    try {
      final now = DateTime.now();
      final yearMonth = '${now.year.toString().substring(2)}${now.month.toString().padLeft(2, '0')}';
      final counter = (now.second * 1000 + now.millisecond);
      final itemId = 'AA-$yearMonth-${counter.toString().padLeft(6, '0')}';
      
      setState(() {
        _refController.text = itemId;
      });
    } finally {
      setState(() => _isGeneratingId = false);
    }
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
      // Silently fail - categories will be empty
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
          _imageFile = imageFile;
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
          
          if (mounted) {
            setState(() {
              _uploadedPhotoId = uploadedPhoto.id;
              _isUploadingPhoto = false;
            });
            
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Photo uploaded successfully'),
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

      final item = Item(
        id: '',
        ref: _refController.text.trim(),
        label: _nameController.text.trim(),
        category: category.isNotEmpty ? category : null,
        price: price ?? 0.0,
        barcode: _barcodeController.text.trim().isEmpty ? null : _barcodeController.text.trim(),
        description: _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        status: '1',
        statusBuy: '1',
        deleted: false,
        dateCreation: DateTime.now(),
        dateModification: DateTime.now(),
      );

      final createdItem = await itemService.createItem(item);

      if (_selectedContainerRef != null) {
        try {
          await itemService.updateStock(createdItem.id, _selectedContainerRef!, 1);
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Item created but container association failed: $e'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        }
      }

      if (_uploadedPhotoId != null) {
        final photoService = PhotoService(apiClient);
        try {
          await photoService.addPhotoToProduct(createdItem.id, _uploadedPhotoId!);
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Item created but photo link failed: $e'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Item created successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        String errorMessage = e.toString();
        
        if (errorMessage.contains('already exists') || errorMessage.contains('duplicate')) {
          errorMessage = 'Item ID already exists. Please use a different ID or click the refresh button to generate a new one.';
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Item'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              GestureDetector(
                onTap: _isUploadingPhoto ? null : _takePicture,
                child: Container(
                  height: 200,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
                      width: 2,
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
                                fontSize: 16,
                              ),
                            ),
                          ],
                        )
                      : _imageFile != null
                          ? Stack(
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(16),
                                  child: Image.file(_imageFile!, fit: BoxFit.cover, width: double.infinity),
                                ),
                                if (_uploadedPhotoId != null)
                                  Positioned(
                                    top: 8,
                                    right: 8,
                                    child: Container(
                                      padding: const EdgeInsets.all(6),
                                      decoration: BoxDecoration(
                                        color: Colors.green,
                                        shape: BoxShape.circle,
                                      ),
                                      child: const Icon(
                                        Icons.check,
                                        color: Colors.white,
                                        size: 20,
                                      ),
                                    ),
                                  ),
                              ],
                            )
                          : Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.camera_alt_rounded,
                                  size: 48,
                                  color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  'Tap to take photo',
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
                decoration: InputDecoration(
                  labelText: 'Item ID / Reference *',
                  prefixIcon: const Icon(Icons.tag_rounded),
                  suffixIcon: _isGeneratingId
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: Padding(
                            padding: EdgeInsets.all(12.0),
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        )
                      : IconButton(
                          icon: const Icon(Icons.refresh_rounded),
                          onPressed: _generateItemId,
                          tooltip: 'Regenerate ID',
                        ),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Item ID is required';
                  }
                  return null;
                },
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
                  labelText: 'Selling Price (optional)',
                  prefixIcon: Icon(Icons.attach_money_rounded),
                  suffixText: 'DKK',
                ),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description (optional)',
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
                    : const Text('Save Item', style: TextStyle(fontSize: 16)),
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
