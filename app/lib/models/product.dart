class Product {
  final String id;
  final String ref;
  final String label;
  final double price;
  final String? barcode;
  final double? costPrice;
  final String? description;
  final String type;
  final String status;
  final String statusBuy;
  final bool deleted;
  final Map<String, WarehouseStock>? stockWarehouse;
  final List<String>? photos;
  final DateTime dateCreation;
  final DateTime dateModification;

  Product({
    required this.id,
    required this.ref,
    required this.label,
    required this.price,
    this.barcode,
    this.costPrice,
    this.description,
    required this.type,
    required this.status,
    required this.statusBuy,
    required this.deleted,
    this.stockWarehouse,
    this.photos,
    required this.dateCreation,
    required this.dateModification,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    Map<String, WarehouseStock>? stockWarehouse;
    if (json['stock_warehouse'] != null && json['stock_warehouse'] is Map) {
      stockWarehouse = {};
      (json['stock_warehouse'] as Map<String, dynamic>).forEach((key, value) {
        if (value is Map<String, dynamic>) {
          stockWarehouse![key] = WarehouseStock.fromJson(value);
        }
      });
    }

    return Product(
      id: json['_id'] as String,
      ref: json['ref'] as String,
      label: json['label'] as String,
      price: _parseDouble(json['price']),
      barcode: json['barcode'] as String?,
      costPrice: json['cost_price'] != null ? _parseDouble(json['cost_price']) : null,
      description: json['description'] as String?,
      type: json['type'] as String,
      status: json['status'] as String,
      statusBuy: json['status_buy'] as String,
      deleted: json['deleted'] as bool,
      stockWarehouse: stockWarehouse,
      photos: json['photos'] != null ? List<String>.from(json['photos']) : null,
      dateCreation: DateTime.parse(json['date_creation'] as String),
      dateModification: DateTime.parse(json['date_modification'] as String),
    );
  }

  int getTotalStock() {
    if (stockWarehouse == null) return 0;
    return stockWarehouse!.values.fold(0, (sum, stock) => sum + stock.items.toInt());
  }

  Map<String, dynamic> toJson() {
    return {
      'ref': ref,
      'label': label,
      'price': price,
      if (barcode != null && barcode!.isNotEmpty) 'barcode': barcode,
      if (costPrice != null) 'cost_price': costPrice,
      if (description != null && description!.isNotEmpty) 'description': description,
      'type': type,
      'status': status,
      'status_buy': statusBuy,
    };
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }
}

class WarehouseStock {
  final double items;

  WarehouseStock({required this.items});

  factory WarehouseStock.fromJson(Map<String, dynamic> json) {
    return WarehouseStock(
      items: _parseDouble(json['items']),
    );
  }

  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  Map<String, dynamic> toJson() {
    return {
      'items': items,
    };
  }
}
