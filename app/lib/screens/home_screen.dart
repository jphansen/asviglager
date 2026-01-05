import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:package_info_plus/package_info_plus.dart';
import '../services/auth_service.dart';
import '../services/api_client.dart';
import '../config/api_config.dart';
import 'products_screen.dart';
import 'new_product_screen.dart';
import 'stock_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? _buildNumber;

  @override
  void initState() {
    super.initState();
    _loadBuildNumber();
  }

  Future<void> _loadBuildNumber() async {
    final info = await PackageInfo.fromPlatform();
    setState(() {
      _buildNumber = info.buildNumber;
    });
  }

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Asviglager'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _showLogoutDialog(context),
            tooltip: 'Logout',
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Clickable User Info Card
                Card(
                  elevation: 2,
                  child: InkWell(
                    onTap: () => _showUserInfoDialog(context, authService),
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      width: double.infinity,
                      constraints: const BoxConstraints(maxWidth: 500),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        gradient: LinearGradient(
                          colors: [
                            Theme.of(context).colorScheme.primary.withOpacity(0.1),
                            Theme.of(context).colorScheme.secondary.withOpacity(0.1),
                          ],
                        ),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                              ),
                              child: Icon(
                                Icons.person_rounded,
                                size: 24,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        'Welcome back!',
                                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                                            ),
                                      ),
                                      if (_buildNumber != null) ...[
                                        const SizedBox(width: 6),
                                        Text(
                                          'Build #$_buildNumber',
                                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                                color: Theme.of(context).colorScheme.primary.withOpacity(0.6),
                                                fontSize: 10,
                                              ),
                                        ),
                                      ],
                                    ],
                                  ),
                                  Text(
                                    authService.username ?? 'User',
                                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                  ),
                                ],
                              ),
                            ),
                            Icon(
                              Icons.info_outline,
                              size: 20,
                              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 40),
                // Menu Buttons - Centered and smaller
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 500),
                  child: Column(
                    children: [
                      _MenuButton(
                        icon: Icons.inventory_2_rounded,
                        title: 'Products',
                        subtitle: 'View all products',
                        color: const Color(0xFF00BCD4),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const ProductsScreen(),
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 16),
                      _MenuButton(
                        icon: Icons.add_circle_rounded,
                        title: 'New Product',
                        subtitle: 'Create new product',
                        color: const Color(0xFF4CAF50),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const NewProductScreen(),
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 16),
                      _MenuButton(
                        icon: Icons.warehouse_rounded,
                        title: 'Stock Management',
                        subtitle: 'Manage inventory',
                        color: const Color(0xFFFF9800),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const StockScreen(),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showUserInfoDialog(BuildContext context, AuthService authService) {
    showDialog(
      context: context,
      builder: (context) => _UserInfoDialog(authService: authService),
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Provider.of<AuthService>(context, listen: false).logout();
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}

// New button-style menu item (smaller and centered)
class _MenuButton extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _MenuButton({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          height: 100,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                color.withOpacity(0.1),
                color.withOpacity(0.05),
              ],
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color.withOpacity(0.2),
                  ),
                  child: Icon(icon, size: 28, color: color),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        title,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                            ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios,
                  size: 18,
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// User Info Dialog with Server Health
class _UserInfoDialog extends StatefulWidget {
  final AuthService authService;

  const _UserInfoDialog({required this.authService});

  @override
  State<_UserInfoDialog> createState() => _UserInfoDialogState();
}

class _UserInfoDialogState extends State<_UserInfoDialog> {
  Map<String, dynamic>? _healthData;
  bool _loadingHealth = true;
  String? _healthError;
  PackageInfo? _packageInfo;

  @override
  void initState() {
    super.initState();
    _loadServerHealth();
    _loadPackageInfo();
  }

  Future<void> _loadPackageInfo() async {
    final info = await PackageInfo.fromPlatform();
    setState(() {
      _packageInfo = info;
    });
  }

  Future<void> _loadServerHealth() async {
    setState(() {
      _loadingHealth = true;
      _healthError = null;
    });

    try {
      final apiClient = ApiClient(widget.authService);
      // Health endpoint is at root level, not under /api/v1
      final baseUrlRoot = ApiConfig.baseUrl.replaceFirst('/api/v1', '');
      final url = '$baseUrlRoot${ApiConfig.health}';
      final response = await apiClient.get(url);

      if (response.statusCode == 200) {
        setState(() {
          _healthData = json.decode(response.body);
          _loadingHealth = false;
        });
      } else {
        setState(() {
          _healthError = 'Server returned ${response.statusCode}';
          _loadingHealth = false;
        });
      }
    } catch (e) {
      setState(() {
        _healthError = e.toString();
        _loadingHealth = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(
            Icons.person,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(width: 8),
          const Text('User Information'),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // User Information Section
            _InfoSection(
              title: 'Account Details',
              items: [
                _InfoItem(
                  icon: Icons.account_circle,
                  label: 'Username',
                  value: widget.authService.username ?? 'Unknown',
                ),
                _InfoItem(
                  icon: Icons.verified_user,
                  label: 'Status',
                  value: 'Authenticated',
                  valueColor: Colors.green,
                ),
              ],
            ),
            const SizedBox(height: 24),
            // App Information Section
            if (_packageInfo != null) ...[
              _InfoSection(
                title: 'App Information',
                items: [
                  _InfoItem(
                    icon: Icons.apps,
                    label: 'Version',
                    value: _packageInfo!.version,
                  ),
                  _InfoItem(
                    icon: Icons.build,
                    label: 'Build Number',
                    value: _packageInfo!.buildNumber,
                    valueColor: Theme.of(context).colorScheme.primary,
                  ),
                ],
              ),
              const SizedBox(height: 24),
            ],
            // Server Health Section
            _InfoSection(
              title: 'Server Status',
              items: _buildHealthItems(),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _loadingHealth ? null : _loadServerHealth,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.refresh, size: 18),
              const SizedBox(width: 4),
              const Text('Refresh'),
            ],
          ),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Close'),
        ),
      ],
    );
  }

  List<Widget> _buildHealthItems() {
    if (_loadingHealth) {
      return [
        const Center(
          child: Padding(
            padding: EdgeInsets.all(16.0),
            child: CircularProgressIndicator(),
          ),
        ),
      ];
    }

    if (_healthError != null) {
      return [
        _InfoItem(
          icon: Icons.error_outline,
          label: 'Error',
          value: _healthError!,
          valueColor: Colors.red,
        ),
      ];
    }

    if (_healthData == null) {
      return [
        _InfoItem(
          icon: Icons.help_outline,
          label: 'Status',
          value: 'Unknown',
          valueColor: Colors.grey,
        ),
      ];
    }

    final status = _healthData!['status'] ?? 'unknown';
    final database = _healthData!['database'] ?? 'unknown';
    final environment = _healthData!['environment'] ?? 'unknown';

    return [
      _InfoItem(
        icon: status == 'healthy' ? Icons.check_circle : Icons.cancel,
        label: 'Health',
        value: status.toString().toUpperCase(),
        valueColor: status == 'healthy' ? Colors.green : Colors.red,
      ),
      _InfoItem(
        icon: database == 'connected' ? Icons.storage : Icons.storage_outlined,
        label: 'Database',
        value: database.toString().toUpperCase(),
        valueColor: database == 'connected' ? Colors.green : Colors.orange,
      ),
      _InfoItem(
        icon: Icons.cloud,
        label: 'Environment',
        value: environment.toString().toUpperCase(),
      ),
    ];
  }
}

class _InfoSection extends StatelessWidget {
  final String title;
  final List<Widget> items;

  const _InfoSection({
    required this.title,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Theme.of(context).colorScheme.primary,
              ),
        ),
        const SizedBox(height: 12),
        ...items,
      ],
    );
  }
}

class _InfoItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoItem({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: valueColor,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
