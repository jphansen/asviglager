class Photo {
  final String id;
  final String filename;
  final String contentType;
  final String data; // Base64 encoded
  final String? description;
  final int fileSize;
  final DateTime dateCreation;

  Photo({
    required this.id,
    required this.filename,
    required this.contentType,
    required this.data,
    this.description,
    required this.fileSize,
    required this.dateCreation,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    return Photo(
      id: json['_id'] ?? json['id'],
      filename: json['filename'],
      contentType: json['content_type'],
      data: json['data'],
      description: json['description'],
      fileSize: json['file_size'],
      dateCreation: DateTime.parse(json['date_creation']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'filename': filename,
      'content_type': contentType,
      'data': data,
      if (description != null) 'description': description,
    };
  }
}

class PhotoMetadata {
  final String id;
  final String filename;
  final String contentType;
  final String? description;
  final int fileSize;
  final DateTime dateCreation;

  PhotoMetadata({
    required this.id,
    required this.filename,
    required this.contentType,
    this.description,
    required this.fileSize,
    required this.dateCreation,
  });

  factory PhotoMetadata.fromJson(Map<String, dynamic> json) {
    return PhotoMetadata(
      id: json['_id'] ?? json['id'],
      filename: json['filename'],
      contentType: json['content_type'],
      description: json['description'],
      fileSize: json['file_size'],
      dateCreation: DateTime.parse(json['date_creation']),
    );
  }
}
