class ApiConfig {
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';  // Android emulator localhost
  // For physical device use: 'http://YOUR_COMPUTER_IP:8000/api/v1'
  
  static const Duration timeout = Duration(seconds: 30);
  
  // Endpoints
  static const String login = '/auth/login';
  static const String products = '/products';
  static const String productById = '/products';
  static const String productByRef = '/products/ref';
}
