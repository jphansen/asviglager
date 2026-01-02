enum WarehouseType {
  warehouse,
  location,
  container;

  String toJson() => name;
  
  static WarehouseType fromJson(String value) {
    return WarehouseType.values.firstWhere(
      (e) => e.name == value,
      orElse: () => WarehouseType.container,
    );
  }
}

enum ContainerType {
  box,
  case_,  // 'case' is reserved keyword in Dart
  suitcase,
  ikea_box,
  wrap,
  storage_bin,
  pallet,
  shelf,
  drawer,
  other;

  String toJson() {
    if (this == ContainerType.case_) return 'case';
    return name;
  }
  
  static ContainerType? fromJson(String? value) {
    if (value == null) return null;
    if (value == 'case') return ContainerType.case_;
    return ContainerType.values.firstWhere(
      (e) => e.name == value,
      orElse: () => ContainerType.other,
    );
  }

  String get displayName {
    if (this == ContainerType.case_) return 'Case';
    return name.replaceAll('_', ' ').split(' ').map((word) => 
      word.isEmpty ? '' : word[0].toUpperCase() + word.substring(1)
    ).join(' ');
  }
}

class Warehouse {
  final String id;
  final String ref;
  final String label;
  final String? description;
  final String? short;
  final String? address;
  final String? zip;
  final String? town;
  final String? phone;
  final String? fax;
  final bool status;
  final bool deleted;
  final DateTime dateCreation;
  final DateTime dateModification;
  final WarehouseType type;
  final ContainerType? containerType;
  final String? fkParent;

  Warehouse({
    required this.id,
    required this.ref,
    required this.label,
    this.description,
    this.short,
    this.address,
    this.zip,
    this.town,
    this.phone,
    this.fax,
    required this.status,
    required this.deleted,
    required this.dateCreation,
    required this.dateModification,
    this.type = WarehouseType.container,
    this.containerType,
    this.fkParent,
  });

  factory Warehouse.fromJson(Map<String, dynamic> json) {
    return Warehouse(
      id: json['_id'] as String,
      ref: json['ref'] as String,
      label: json['label'] as String,
      description: json['description'] as String?,
      short: json['short'] as String?,
      address: json['address'] as String?,
      zip: json['zip'] as String?,
      town: json['town'] as String?,
      phone: json['phone'] as String?,
      fax: json['fax'] as String?,
      status: json['status'] as bool,
      deleted: json['deleted'] as bool,
      dateCreation: DateTime.parse(json['date_creation'] as String),
      dateModification: DateTime.parse(json['date_modification'] as String),
      type: json['type'] != null 
        ? WarehouseType.fromJson(json['type'] as String)
        : WarehouseType.container,
      containerType: ContainerType.fromJson(json['container_type'] as String?),
      fkParent: json['fk_parent'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      '_id': id,
      'ref': ref,
      'label': label,
      'description': description,
      'short': short,
      'address': address,
      'zip': zip,
      'town': town,
      'phone': phone,
      'fax': fax,
      'status': status,
      'deleted': deleted,
      'date_creation': dateCreation.toIso8601String(),
      'date_modification': dateModification.toIso8601String(),
      'type': type.toJson(),
      'container_type': containerType?.toJson(),
      'fk_parent': fkParent,
    };
  }
}
