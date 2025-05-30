import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/advanced_menu_models.dart';
import '../services/recommendation_service.dart';

class RecommendationPage extends StatefulWidget {
  final double width;
  final double length;
  final double height;
  final String? category; // '전체'일 경우 null로 받을 수 있음

  const RecommendationPage({
    super.key,
    required this.width,
    required this.length,
    required this.height,
    this.category,
  });

  @override
  State<RecommendationPage> createState() => _RecommendationPageState();
}

class _RecommendationPageState extends State<RecommendationPage> {
  List<AdvancedMenu> recommendations = [];
  bool isLoading = false;

  Future<void> _getRecommendations() async {
    setState(() {
      isLoading = true;
      recommendations = [];
    });

    try {
      final result = await RecommendationService.fetchRecommendations(
        width: widget.width,
        length: widget.length,
        height: widget.height,
        category: widget.category,
      );

      print("📦 추천 개수: ${result.length}");
      for (final r in result) {
        print("👉 ${r.menuName} (${r.restaurantName}) | placeId: ${r.placeId}");
      }

      setState(() {
        recommendations = result;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('추천 결과를 불러왔습니다!')));
    } catch (e) {
      print("❌ 추천 실패: $e");
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('추천 실패: $e')));
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _launchKakaoMap(String placeId) async {
    final url = 'https://place.map.kakao.com/$placeId';
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("카카오맵을 열 수 없습니다.")));
    }
  }

  @override
  void initState() {
    super.initState();
    _getRecommendations(); // 자동 실행
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("📋 추천 식당 결과")),
      body: Column(
        children: [
          if (isLoading)
            const Padding(
              padding: EdgeInsets.only(top: 24),
              child: CircularProgressIndicator(),
            )
          else
            Expanded(
              child: recommendations.isEmpty
                  ? const Center(child: Text("추천 결과가 없습니다."))
                  : ListView.builder(
                      itemCount: recommendations.length,
                      itemBuilder: (context, index) {
                        final menu = recommendations[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          elevation: 3,
                          child: ListTile(
                            onTap: () {
                              if (menu.placeId != null &&
                                  menu.placeId!.isNotEmpty) {
                                _launchKakaoMap(menu.placeId!);
                              } else {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text("placeId 정보가 없습니다."),
                                  ),
                                );
                              }
                            },
                            title: Text(menu.menuName),
                            subtitle: Text(
                              '${menu.restaurantName} · ${menu.price}원',
                            ),
                            trailing: Text(
                              '${menu.volumeUtilization.toStringAsFixed(1)}%',
                              style: const TextStyle(color: Colors.green),
                            ),
                          ),
                        );
                      },
                    ),
            ),
        ],
      ),
    );
  }
}
