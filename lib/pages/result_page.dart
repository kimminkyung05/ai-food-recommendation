import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/restaurant_model.dart';
import '../services/store.dart';

class ResultPage extends StatelessWidget {
  final String selectedCategory;
  final double containerVolume;

  const ResultPage({
    super.key,
    required this.selectedCategory,
    required this.containerVolume,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("🍱 추천 식당 결과")),
      body: FutureBuilder<List<Restaurant>>(
        future: RestaurantStore.loadRestaurants(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text("😥 불러올 식당 정보가 없습니다."));
          }

          final restaurants = snapshot.data!;
          final filteredList = restaurants.where((restaurant) {
            final hasFittableMenu = restaurant.menus.any(
              (menu) => menu.volume <= containerVolume,
            );
            final categoryOk =
                selectedCategory == '전체' ||
                restaurant.category == selectedCategory;
            return hasFittableMenu && categoryOk;
          }).toList()..sort((a, b) => a.name.compareTo(b.name));

          return ListView.builder(
            itemCount: filteredList.length,
            padding: const EdgeInsets.all(20),
            itemBuilder: (context, index) {
              final r = filteredList[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 16),
                child: ListTile(
                  onTap: () async {
                    final url = 'https://place.map.kakao.com/${r.placeId}';
                    final uri = Uri.parse(url);
                    if (await canLaunchUrl(uri)) {
                      await launchUrl(
                        uri,
                        mode: LaunchMode.externalApplication,
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text("링크를 열 수 없습니다.")),
                      );
                    }
                  },
                  title: Text("🍽️ ${r.name}"),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("📍 ${r.address}"),
                      Text("📞 ${r.phone}"),
                      Text("🗂️ 카테고리: ${r.category}"),
                      ...r.menus.map(
                        (m) => Text("- ${m.name} (${m.volume}ml, ${m.price}원)"),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
