# Flutter Integration Guide - YOLOv11 Damage Detection API

**Last Updated**: May 9, 2026  
**Status**: ✅ Complete Integration Package

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Dart/Flutter SDK](#dartflutter-sdk)
4. [Flutter App Architecture](#flutter-app-architecture)
5. [Implementation Examples](#implementation-examples)
6. [UI Components](#ui-components)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Flutter SDK 3.0+
- Dart 3.0+
- API running locally or on server
- Android Studio / Xcode

### 3 Steps to Integrate

**Step 1: Add Dependencies to `pubspec.yaml`**
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.0
  image: ^4.0.0
  provider: ^6.0.0
  dio: ^5.3.0
  cached_network_image: ^3.3.0
```

**Step 2: Create API Service**
```dart
// services/damage_detection_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class DamageDetectionService {
  final String baseUrl = "http://localhost:8000";
  
  Future<Map> detectDamage(File imageFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/detect'),
    )..files.add(await http.MultipartFile.fromPath('file', imageFile.path));
    
    var response = await request.send();
    return jsonDecode(await response.stream.bytesToString());
  }
}
```

**Step 3: Use in Widget**
```dart
// widgets/damage_detector.dart
class DamageDetector extends StatefulWidget {
  @override
  _DamageDetectorState createState() => _DamageDetectorState();
}

class _DamageDetectorState extends State<DamageDetector> {
  File? _selectedImage;
  Map? _detectionResult;
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Car Damage Detection')),
      body: Column(
        children: [
          if (_selectedImage != null)
            Image.file(_selectedImage!),
          if (_detectionResult != null)
            Text('Damages: ${_detectionResult!['total_damages']}'),
          ElevatedButton(
            onPressed: _pickImage,
            child: Text('Pick Image'),
          ),
          if (_isLoading)
            CircularProgressIndicator(),
        ],
      ),
    );
  }

  void _pickImage() async {
    // Image picker implementation
  }
}
```

---

## 📦 Installation

### Step 1: Set Up Flutter Project

```bash
flutter create car_damage_app
cd car_damage_app
```

### Step 2: Add Dependencies

```bash
flutter pub add http image_picker image provider dio
```

Or manually add to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.0
  image: ^4.0.0
  provider: ^6.0.0
  dio: ^5.3.0
  cached_network_image: ^3.3.0
  connectivity_plus: ^5.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
```

### Step 3: Get Dependencies

```bash
flutter pub get
```

### Step 4: Configure Platforms

#### Android (android/app/build.gradle)
```gradle
android {
    compileSdkVersion 33
    
    defaultConfig {
        targetSdkVersion 33
    }
}
```

#### iOS (ios/Podfile)
```
post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
  end
end
```

---

## 💻 Dart/Flutter SDK

### API Service Class

Create `lib/services/damage_detection_service.dart`:

```dart
import 'package:http/http.dart' as http;
import 'package:dio/dio.dart';
import 'dart:convert';
import 'dart:io';

class DamageDetectionService {
  final String _baseUrl;
  late Dio _dio;
  
  DamageDetectionService({String baseUrl = "http://localhost:8000"})
      : _baseUrl = baseUrl {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));
  }

  /// Detect damage in a single image
  Future<DamageDetectionResult> detectDamage({
    required File imageFile,
    double confidence = 0.25,
    double iou = 0.45,
    bool returnImage = true,
  }) async {
    try {
      FormData formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(imageFile.path),
        'confidence': confidence,
        'iou': iou,
        'return_image': returnImage,
      });

      Response response = await _dio.post(
        '/api/detect',
        data: formData,
      );

      return DamageDetectionResult.fromJson(response.data);
    } on DioException catch (e) {
      throw 'Detection failed: ${e.message}';
    }
  }

  /// Batch detect damage in multiple images
  Future<BatchDetectionResult> batchDetect({
    required List<File> imageFiles,
    double confidence = 0.25,
  }) async {
    try {
      FormData formData = FormData.fromMap({
        'files': imageFiles
            .map((file) => MultipartFile.fromFileSync(file.path))
            .toList(),
        'confidence': confidence,
      });

      Response response = await _dio.post(
        '/api/detect/batch',
        data: formData,
      );

      return BatchDetectionResult.fromJson(response.data);
    } on DioException catch (e) {
      throw 'Batch detection failed: ${e.message}';
    }
  }

  /// Check API health
  Future<bool> healthCheck() async {
    try {
      Response response = await _dio.get('/api/health');
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Get available models
  Future<List<String>> getAvailableModels() async {
    try {
      Response response = await _dio.get('/api/models');
      List models = response.data['available_models'];
      return models.cast<String>();
    } catch (e) {
      throw 'Failed to fetch models: $e';
    }
  }

  /// Switch to different model
  Future<bool> switchModel(String modelName) async {
    try {
      Response response = await _dio.post(
        '/api/model/switch',
        queryParameters: {'model_name': modelName},
      );
      return response.statusCode == 200;
    } catch (e) {
      throw 'Failed to switch model: $e';
    }
  }

  /// Get API configuration
  Future<Map> getConfig() async {
    try {
      Response response = await _dio.get('/api/config');
      return response.data;
    } catch (e) {
      throw 'Failed to get config: $e';
    }
  }
}

// ============================================================================
// MODELS
// ============================================================================

class DamageDetectionResult {
  final String timestamp;
  final String filename;
  final int totalDamages;
  final List<Damage> detections;
  final Statistics? statistics;
  final VehicleAssessment? vehicleAssessment;

  DamageDetectionResult({
    required this.timestamp,
    required this.filename,
    required this.totalDamages,
    required this.detections,
    this.statistics,
    this.vehicleAssessment,
  });

  factory DamageDetectionResult.fromJson(Map<String, dynamic> json) {
    return DamageDetectionResult(
      timestamp: json['timestamp'],
      filename: json['filename'],
      totalDamages: json['total_damages'],
      detections: (json['detections'] as List)
          .map((d) => Damage.fromJson(d))
          .toList(),
      statistics: json['statistics'] != null
          ? Statistics.fromJson(json['statistics'])
          : null,
      vehicleAssessment: json['vehicle_assessment'] != null
          ? VehicleAssessment.fromJson(json['vehicle_assessment'])
          : null,
    );
  }
}

class Damage {
  final String className;
  final double confidence;
  final double combinedSeverity;
  final String severityLevel;
  final double areaPercent;
  final List<int> bbox;

  Damage({
    required this.className,
    required this.confidence,
    required this.combinedSeverity,
    required this.severityLevel,
    required this.areaPercent,
    required this.bbox,
  });

  factory Damage.fromJson(Map<String, dynamic> json) {
    return Damage(
      className: json['class'],
      confidence: (json['confidence'] as num).toDouble(),
      combinedSeverity: (json['combined_severity'] as num).toDouble(),
      severityLevel: json['severity_level'],
      areaPercent: (json['area_percent'] as num).toDouble(),
      bbox: List<int>.from(json['bbox']),
    );
  }

  /// Get severity color
  Color getSeverityColor() {
    switch (severityLevel) {
      case 'LOW':
        return Colors.green;
      case 'MEDIUM':
        return Colors.yellow;
      case 'HIGH':
        return Colors.orange;
      case 'CRITICAL':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

class Statistics {
  final double averageSeverity;
  final double maxSeverity;
  final double minSeverity;
  final SeverityBreakdown breakdown;

  Statistics({
    required this.averageSeverity,
    required this.maxSeverity,
    required this.minSeverity,
    required this.breakdown,
  });

  factory Statistics.fromJson(Map<String, dynamic> json) {
    return Statistics(
      averageSeverity: (json['average_severity'] as num).toDouble(),
      maxSeverity: (json['max_severity'] as num).toDouble(),
      minSeverity: (json['min_severity'] as num).toDouble(),
      breakdown: SeverityBreakdown.fromJson(json['severity_breakdown']),
    );
  }
}

class SeverityBreakdown {
  final int low;
  final int medium;
  final int high;
  final int critical;

  SeverityBreakdown({
    required this.low,
    required this.medium,
    required this.high,
    required this.critical,
  });

  factory SeverityBreakdown.fromJson(Map<String, dynamic> json) {
    return SeverityBreakdown(
      low: json['LOW'] ?? 0,
      medium: json['MEDIUM'] ?? 0,
      high: json['HIGH'] ?? 0,
      critical: json['CRITICAL'] ?? 0,
    );
  }
}

class VehicleAssessment {
  final double averageSeverity;
  final String assessmentLevel;

  VehicleAssessment({
    required this.averageSeverity,
    required this.assessmentLevel,
  });

  factory VehicleAssessment.fromJson(Map<String, dynamic> json) {
    return VehicleAssessment(
      averageSeverity: (json['average_severity'] as num).toDouble(),
      assessmentLevel: json['assessment_level'],
    );
  }
}

class BatchDetectionResult {
  final int batchSize;
  final int successful;
  final int failed;
  final List<BatchItemResult> results;

  BatchDetectionResult({
    required this.batchSize,
    required this.successful,
    required this.failed,
    required this.results,
  });

  factory BatchDetectionResult.fromJson(Map<String, dynamic> json) {
    return BatchDetectionResult(
      batchSize: json['batch_size'],
      successful: json['successful'],
      failed: json['failed'],
      results: (json['results'] as List)
          .map((r) => BatchItemResult.fromJson(r))
          .toList(),
    );
  }
}

class BatchItemResult {
  final String filename;
  final String status;
  final int totalDamages;
  final double? averageSeverity;

  BatchItemResult({
    required this.filename,
    required this.status,
    required this.totalDamages,
    this.averageSeverity,
  });

  factory BatchItemResult.fromJson(Map<String, dynamic> json) {
    return BatchItemResult(
      filename: json['filename'],
      status: json['status'],
      totalDamages: json['total_damages'],
      averageSeverity:
          json['average_severity'] != null
              ? (json['average_severity'] as num).toDouble()
              : null,
    );
  }
}
```

---

## 🎨 Flutter App Architecture

### Project Structure

```
lib/
├── main.dart                          # App entry point
├── models/
│   ├── damage_model.dart              # Data models
│   └── api_response.dart              # API response models
├── services/
│   ├── damage_detection_service.dart  # API service
│   └── image_service.dart             # Image handling
├── providers/
│   └── damage_detection_provider.dart # State management
├── screens/
│   ├── home_screen.dart               # Main screen
│   ├── detection_screen.dart          # Detection screen
│   ├── batch_detection_screen.dart    # Batch processing
│   └── results_screen.dart            # Results display
├── widgets/
│   ├── damage_card.dart               # Damage display card
│   ├── severity_badge.dart            # Severity indicator
│   ├── image_preview.dart             # Image preview
│   └── results_list.dart              # Results list
└── utils/
    ├── constants.dart                 # App constants
    └── theme.dart                     # UI theme
```

### State Management with Provider

Create `lib/providers/damage_detection_provider.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/damage_detection_service.dart';
import 'dart:io';

class DamageDetectionProvider extends ChangeNotifier {
  final DamageDetectionService _service;
  
  DamageDetectionResult? _latestResult;
  bool _isLoading = false;
  String? _error;
  
  DamageDetectionProvider(this._service);
  
  // Getters
  DamageDetectionResult? get latestResult => _latestResult;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Detect damage
  Future<void> detectDamage(File imageFile) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      _latestResult = await _service.detectDamage(imageFile: imageFile);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Batch detection
  Future<void> batchDetect(List<File> imageFiles) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      await _service.batchDetect(imageFiles: imageFiles);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Clear results
  void clearResults() {
    _latestResult = null;
    _error = null;
    notifyListeners();
  }
}
```

---

## 💻 Implementation Examples

### Example 1: Simple Detection Screen

Create `lib/screens/detection_screen.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../providers/damage_detection_provider.dart';
import '../widgets/damage_card.dart';
import 'dart:io';

class DetectionScreen extends StatefulWidget {
  @override
  _DetectionScreenState createState() => _DetectionScreenState();
}

class _DetectionScreenState extends State<DetectionScreen> {
  File? _selectedImage;
  final ImagePicker _picker = ImagePicker();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Car Damage Detection'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview
            Container(
              height: 300,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(8),
              ),
              child: _selectedImage != null
                  ? Image.file(_selectedImage!, fit: BoxFit.cover)
                  : Center(
                      child: Icon(Icons.image, size: 80, color: Colors.grey),
                    ),
            ),
            SizedBox(height: 20),

            // Pick Image Button
            ElevatedButton.icon(
              onPressed: _pickImage,
              icon: Icon(Icons.camera_alt),
              label: Text('Pick Image from Gallery'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 15),
              ),
            ),

            SizedBox(height: 10),

            // Camera Button
            ElevatedButton.icon(
              onPressed: _takePhoto,
              icon: Icon(Icons.camera),
              label: Text('Take Photo'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 15),
              ),
            ),

            SizedBox(height: 20),

            // Detect Button
            Consumer<DamageDetectionProvider>(
              builder: (context, provider, child) {
                return ElevatedButton.icon(
                  onPressed: _selectedImage != null && !provider.isLoading
                      ? () => _detectDamage(context)
                      : null,
                  icon: provider.isLoading
                      ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Icon(Icons.search),
                  label: Text(provider.isLoading
                      ? 'Detecting...'
                      : 'Detect Damage'),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 15),
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                  ),
                );
              },
            ),

            SizedBox(height: 30),

            // Results
            Consumer<DamageDetectionProvider>(
              builder: (context, provider, child) {
                if (provider.error != null) {
                  return Card(
                    color: Colors.red[50],
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Icon(Icons.error, color: Colors.red, size: 40),
                          SizedBox(height: 10),
                          Text(
                            'Error: ${provider.error}',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.red),
                          ),
                        ],
                      ),
                    ),
                  );
                }

                if (provider.latestResult == null) {
                  return SizedBox.shrink();
                }

                final result = provider.latestResult!;
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Vehicle Assessment
                    if (result.vehicleAssessment != null)
                      Card(
                        elevation: 2,
                        child: Padding(
                          padding: EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Vehicle Assessment',
                                style: Theme.of(context).textTheme.headline6,
                              ),
                              SizedBox(height: 10),
                              Text(
                                '${result.vehicleAssessment!.assessmentLevel}',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: _getAssessmentColor(
                                    result.vehicleAssessment!.assessmentLevel,
                                  ),
                                ),
                              ),
                              SizedBox(height: 5),
                              Text(
                                'Average Severity: ${result.vehicleAssessment!.averageSeverity.toStringAsFixed(1)}/100',
                              ),
                            ],
                          ),
                        ),
                      ),

                    SizedBox(height: 20),

                    // Statistics
                    if (result.statistics != null)
                      Card(
                        elevation: 2,
                        child: Padding(
                          padding: EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Detection Statistics',
                                style: Theme.of(context).textTheme.headline6,
                              ),
                              SizedBox(height: 10),
                              _buildStatRow(
                                'Total Damages',
                                result.totalDamages.toString(),
                              ),
                              _buildStatRow(
                                'Average Severity',
                                result.statistics!.averageSeverity
                                    .toStringAsFixed(1),
                              ),
                              _buildStatRow(
                                'Max Severity',
                                result.statistics!.maxSeverity
                                    .toStringAsFixed(1),
                              ),
                            ],
                          ),
                        ),
                      ),

                    SizedBox(height: 20),

                    // Damages List
                    Text(
                      'Detected Damages',
                      style: Theme.of(context).textTheme.headline6,
                    ),
                    SizedBox(height: 10),
                    ...result.detections.map((damage) => DamageCard(
                          damage: damage,
                        )),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(value, style: TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() => _selectedImage = File(pickedFile.path));
    }
  }

  Future<void> _takePhoto() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() => _selectedImage = File(pickedFile.path));
    }
  }

  void _detectDamage(BuildContext context) {
    if (_selectedImage != null) {
      context.read<DamageDetectionProvider>().detectDamage(_selectedImage!);
    }
  }

  Color _getAssessmentColor(String assessment) {
    switch (assessment) {
      case 'MINIMAL':
        return Colors.green;
      case 'MODERATE':
        return Colors.yellow[700]!;
      case 'SUBSTANTIAL':
        return Colors.orange;
      case 'SEVERE':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
```

### Example 2: Damage Card Widget

Create `lib/widgets/damage_card.dart`:

```dart
import 'package:flutter/material.dart';
import '../services/damage_detection_service.dart';

class DamageCard extends StatelessWidget {
  final Damage damage;

  const DamageCard({Key? key, required this.damage}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with damage type and severity badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    damage.className.toUpperCase(),
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: damage.getSeverityColor(),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    damage.severityLevel,
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),

            SizedBox(height: 12),

            // Severity Bar
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Severity Score'),
                SizedBox(height: 5),
                Row(
                  children: [
                    Expanded(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: damage.combinedSeverity / 100,
                          minHeight: 8,
                          valueColor: AlwaysStoppedAnimation(
                            damage.getSeverityColor(),
                          ),
                          backgroundColor: Colors.grey[300],
                        ),
                      ),
                    ),
                    SizedBox(width: 10),
                    Text(
                      '${damage.combinedSeverity.toStringAsFixed(1)}/100',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ],
            ),

            SizedBox(height: 12),

            // Details Grid
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              childAspectRatio: 2.5,
              children: [
                _buildDetailItem('Confidence', 
                  '${(damage.confidence * 100).toStringAsFixed(1)}%'),
                _buildDetailItem('Area', 
                  '${damage.areaPercent.toStringAsFixed(2)}%'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
        Text(
          value,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}
```

### Example 3: Batch Processing Screen

Create `lib/screens/batch_detection_screen.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../providers/damage_detection_provider.dart';
import 'dart:io';

class BatchDetectionScreen extends StatefulWidget {
  @override
  _BatchDetectionScreenState createState() => _BatchDetectionScreenState();
}

class _BatchDetectionScreenState extends State<BatchDetectionScreen> {
  List<File> _selectedImages = [];
  final ImagePicker _picker = ImagePicker();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Batch Damage Detection'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Count
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text(
                      '${_selectedImages.length} Images Selected',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Maximum: 100 images',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 20),

            // Selected Images Grid
            if (_selectedImages.isNotEmpty)
              GridView.builder(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                ),
                itemCount: _selectedImages.length,
                itemBuilder: (context, index) {
                  return Stack(
                    children: [
                      Image.file(
                        _selectedImages[index],
                        fit: BoxFit.cover,
                      ),
                      Positioned(
                        top: 0,
                        right: 0,
                        child: GestureDetector(
                          onTap: () {
                            setState(() =>
                                _selectedImages.removeAt(index));
                          },
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.red,
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              Icons.close,
                              color: Colors.white,
                              size: 16,
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),

            SizedBox(height: 20),

            // Add Images Buttons
            ElevatedButton.icon(
              onPressed: _selectedImages.length < 100 ? _addImages : null,
              icon: Icon(Icons.add_photo_alternate),
              label: Text('Add Images from Gallery'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 15),
              ),
            ),

            SizedBox(height: 10),

            // Detect Batch Button
            Consumer<DamageDetectionProvider>(
              builder: (context, provider, child) {
                return ElevatedButton.icon(
                  onPressed: _selectedImages.isNotEmpty && !provider.isLoading
                      ? () => _detectBatch(context)
                      : null,
                  icon: provider.isLoading
                      ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Icon(Icons.search_outlined),
                  label: Text(provider.isLoading
                      ? 'Processing...'
                      : 'Detect Damage in All'),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 15),
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _addImages() async {
    final pickedFiles = await _picker.pickMultiImage();
    if (pickedFiles.isNotEmpty) {
      setState(() {
        _selectedImages.addAll(
          pickedFiles.map((file) => File(file.path)),
        );
      });
    }
  }

  void _detectBatch(BuildContext context) {
    if (_selectedImages.isNotEmpty) {
      context
          .read<DamageDetectionProvider>()
          .batchDetect(_selectedImages);
    }
  }
}
```

### Example 4: Main App Setup

Create `lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/damage_detection_service.dart';
import 'providers/damage_detection_provider.dart';
import 'screens/detection_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<DamageDetectionService>(
          create: (_) => DamageDetectionService(
            baseUrl: 'http://localhost:8000', // Change to your API URL
          ),
        ),
        ChangeNotifierProvider<DamageDetectionProvider>(
          create: (context) => DamageDetectionProvider(
            context.read<DamageDetectionService>(),
          ),
        ),
      ],
      child: MaterialApp(
        title: 'Car Damage Detection',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: DetectionScreen(),
      ),
    );
  }
}
```

---

## 🎨 UI Components

### Severity Badge Widget

```dart
class SeverityBadge extends StatelessWidget {
  final String level;
  final double severity;

  const SeverityBadge({
    Key? key,
    required this.level,
    required this.severity,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getColor(),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getIcon(), size: 16, color: Colors.white),
          SizedBox(width: 6),
          Text(
            '$level (${severity.toStringAsFixed(1)})',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getColor() {
    switch (level) {
      case 'LOW':
        return Colors.green;
      case 'MEDIUM':
        return Colors.yellow[700]!;
      case 'HIGH':
        return Colors.orange;
      case 'CRITICAL':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getIcon() {
    switch (level) {
      case 'LOW':
        return Icons.check_circle;
      case 'MEDIUM':
        return Icons.warning;
      case 'HIGH':
        return Icons.error_outline;
      case 'CRITICAL':
        return Icons.dangerous;
      default:
        return Icons.help;
    }
  }
}
```

---

## 🔧 Troubleshooting

### Issue: Cannot connect to API

**Solution:**
```dart
// Use your server's IP if running on physical device
// For localhost on Android emulator, use: http://10.0.2.2:8000
DamageDetectionService(baseUrl: 'http://10.0.2.2:8000')

// For iOS simulator
// Use: http://localhost:8000

// For physical device
// Use: http://<your-computer-ip>:8000
```

### Issue: Image permissions on Android/iOS

**Android (android/app/src/main/AndroidManifest.xml):**
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

**iOS (ios/Runner/Info.plist):**
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to take photos</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>We need photo library access</string>
```

### Issue: Large image uploads fail

**Solution:**
```dart
// Compress image before upload
import 'package:image/image.dart' as img;

Future<File> compressImage(File imageFile) async {
  var image = img.decodeImage(imageFile.readAsBytesSync())!;
  var compressed = img.encodeJpg(image, quality: 85);
  return File(imageFile.path)..writeAsBytesSync(compressed);
}
```

### Issue: Timeout errors

**Solution:**
```dart
DamageDetectionService(baseUrl: 'http://your-api.com')
  // Service already has 30-second timeout
  // For longer processing, increase in DamageDetectionService:
  // connectTimeout: const Duration(seconds: 60),
  // receiveTimeout: const Duration(seconds: 60),
```

---

## 📚 Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Dart Documentation](https://dart.dev/guides)
- [image_picker Package](https://pub.dev/packages/image_picker)
- [Dio Package](https://pub.dev/packages/dio)
- [Provider Package](https://pub.dev/packages/provider)

---

## ✅ Checklist

- [ ] Flutter SDK installed
- [ ] pubspec.yaml dependencies added
- [ ] API service created
- [ ] Models created
- [ ] Provider setup
- [ ] Screens created
- [ ] Permissions configured (Android/iOS)
- [ ] API URL configured
- [ ] Testing on device/emulator
- [ ] Error handling implemented

---

**Status**: ✅ Complete Flutter Integration Package

All code ready for copy-paste and customization!

