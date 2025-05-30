import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/advanced_menu_models.dart';

class RecommendationService {
  static Future<List<AdvancedMenu>> fetchRecommendations({
    required double width,
    required double length,
    required double height,
    String? category,
  }) async {
    final uri = Uri.parse('http://10.50.98.201:8000/recommend/advanced');

    // ✅ [1] 요청 파라미터 로그 출력
    print("🔍 [요청 파라미터]");
    print("width: $width");
    print("length: $length");
    print("height: $height");
    print("category: $category");

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'width': width,
        'length': length,
        'height': height,
        'category': category,
        'top_k': 5,
      }),
    );

    // ✅ [2] 응답 상태 확인
    print("🔁 [응답 상태 코드]: ${response.statusCode}");

    // ✅ [3] 응답 본문 출력
    print("📦 [응답 본문]: ${response.body}");

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body)['data'];
      return data
          .map<AdvancedMenu>((json) => AdvancedMenu.fromJson(json))
          .toList();
    } else {
      throw Exception("추천 실패: ${response.statusCode}");
    }
  }
}
