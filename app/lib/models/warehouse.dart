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
    );
  }
}
