import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../models/product.dart';
import '../services/auth_service.dart';
import '../services/product_service.dart';
import '../services/photo_service.dart';

class NewProductScreen extends StatefulWidget {
  const NewProductScreen({super.key});

  @override
  State<NewProductScreen> createState() => _NewProductScreenState();
}

class _NewProductScreenState extends State<NewProductScreen> {
  final _formKey = GlobalKey<FormState>();
  final _refController = TextEditingController();
  final _nameController = TextEditingController();
  final _priceController = TextEditingController();
  final _barcodeController = TextEditingController();
  final _descriptionController = TextEditingController();
  
  File? _imageFile;
  String? _uploadedPhotoId;
  bool _isLoading = false;
  bool _isGeneratingId = false;
  bool _isUploadingPhoto = false;

  @override
  void initState() {
    super.initState();
    _generateProductId();
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

  void _generateProductId() {
    setState(() => _isGeneratingId = true);
    
    try {
      // Get current year and month
      final now = DateTime.now();
      final yearMonth = '${now.year.toString().substring(2)}${now.month.toString().padLeft(2, '0')}';
      
      // Use timestamp-based counter (seconds + milliseconds for uniqueness)
      final counter = (now.second * 1000 + now.millisecond);
      
      // Generate product ID: AA-YYMM-XXXXXX
      final productId = 'AA-$yearMonth-${counter.toString().padLeft(6, '0')}';
      
      setState(() {
        _refController.text = productId;
      });
    } finally {
      setState(() => _isGeneratingId = false);
    }
  }

  Future<void> _takePicture() async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? photo = await picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (photo != null) {
        final imageFile = File(photo.path);
        setState(() {
          _imageFile = imageFile;
          _isUploadingPhoto = true;
        });

        // Upload photo to backend immediately
        try {
          final authService = Provider.of<AuthService>(context, listen: false);
          final photoService = PhotoService(authService.token!);
          
          // Convert image to base64
          final bytes = await imageFile.readAsBytes();
          final base64Image = base64Encode(bytes);
          
          // Upload to backend
          final uploadedPhoto = await photoService.uploadPhoto(
            filename: photo.name,
            contentType: 'image/jpeg',
            base64Data: base64Image,
            description: 'Product photo',
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

  Future<void> _saveProduct() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final authService = Provider.of<AuthService>(context, listen: false);
      final productService = ProductService(authService.token!);

      double? price;
      if (_priceController.text.isNotEmpty) {
        price = double.tryParse(_priceController.text);
        if (price == null) {
          throw Exception('Invalid price format');
        }
      }

      final product = Product(
        id: '',
        ref: _refController.text.trim(),
        label: _nameController.text.trim(),
        price: price ?? 0.0,
        barcode: _barcodeController.text.trim().isEmpty ? null : _barcodeController.text.trim(),
        description: _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        type: '0',
        status: '1',
        statusBuy: '1',
        deleted: false,
        dateCreation: DateTime.now(),
        dateModification: DateTime.now(),
      );

      final createdProduct = await productService.createProduct(product);

      // Link photo to product if one was uploaded
      if (_uploadedPhotoId != null) {
        final photoService = PhotoService(authService.token!);
        try {
          await photoService.addPhotoToProduct(createdProduct.id, _uploadedPhotoId!);
        } catch (e) {
          // Photo linking failed, but product was created
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Product created but photo link failed: $e'),
                backgroundColor: Colors.orange,
              ),
            );
          }
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Product created successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        String errorMessage = e.toString();
        
        // Check if it's a duplicate ID conflict
        if (errorMessage.contains('already exists') || errorMessage.contains('duplicate')) {
          errorMessage = 'Product ID already exists. Please use a different ID or click the refresh button to generate a new one.';
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
        title: const Text('New Product'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Product Image
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

              // Product Reference (ID)
              TextFormField(
                controller: _refController,
                decoration: InputDecoration(
                  labelText: 'Product ID / Reference *',
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
                          onPressed: _generateProductId,
                          tooltip: 'Regenerate ID',
                        ),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Product ID is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Product Name
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Product Name *',
                  prefixIcon: Icon(Icons.inventory_2_rounded),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Product name is required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Barcode
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

              // Price
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

              // Description
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description (optional)',
                  prefixIcon: Icon(Icons.notes_rounded),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24),

              // Save Button
              ElevatedButton(
                onPressed: _isLoading ? null : _saveProduct,
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
                    : const Text('Save Product', style: TextStyle(fontSize: 16)),
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
