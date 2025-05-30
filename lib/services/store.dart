import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/restaurant_model.dart';

class RestaurantStore {
  static List<Restaurant> _restaurants = [];

  static Future<List<Restaurant>> loadRestaurants() async {
    if (_restaurants.isNotEmpty) return _restaurants;

    try {
      print("\n🔍 === CSV 파일 로딩 시작 ===");
      final restaurantCsv = await rootBundle.loadString(
        'assets/restaurants.csv',
      );
      final menuCsv = await rootBundle.loadString(
        'assets/final_menus_data.csv',
      );

      print("✅ restaurants.csv 로딩 성공 (${restaurantCsv.length} 문자)");
      print("✅ final_menus_data.csv 로딩 성공 (${menuCsv.length} 문자)\n");

      final menuMap = _parseMenus(menuCsv); // Map<String, List<Menu>>
      _restaurants = _parseRestaurants(restaurantCsv, menuMap);

      print("\n🎉 === 최종 결과 ===");
      print("총 식당 수: ${_restaurants.length}\n");
      print("처음 3개 식당:");
      for (
        int i = 0;
        i < (_restaurants.length >= 3 ? 3 : _restaurants.length);
        i++
      ) {
        final r = _restaurants[i];
        print(
          "${i + 1}. ${r.name} (ID: ${r.id})\n   카테고리: ${r.category}\n   주소: ${r.address}\n   메뉴 수: ${r.menus.length}",
        );
      }

      return _restaurants;
    } catch (e) {
      print('🚨 Error loading CSVs: $e');
      return [];
    }
  }

  static Map<String, List<Menu>> _parseMenus(String csv) {
    print("🍴 === 메뉴 파싱 시작 ===");
    final lines = const LineSplitter().convert(csv);
    print("메뉴 CSV 라인 수: ${lines.length}");
    final menuMap = <String, List<Menu>>{};

    for (int i = 1; i < lines.length; i++) {
      final line = lines[i];
      final fields = line.split(',');

      if (fields.length < 8) continue;

      try {
        final restaurantId = fields[1].trim();
        final menu = Menu.fromCsv(fields);

        menuMap.putIfAbsent(restaurantId, () => []).add(menu);
        if (i <= 5)
          print("✅ 메뉴 ${i}: ${restaurantId} (레스토랑 ID: ${fields[0].trim()})");
      } catch (e) {
        print('❌ 메뉴 파싱 실패 (라인 $i): $e');
      }
    }

    print(
      "메뉴 파싱 완료: 성공 ${menuMap.values.fold(0, (sum, list) => sum + list.length)}개, 실패 0개",
    );
    print("파싱된 레스토랑 수: ${menuMap.length}");
    print("처음 5개 레스토랑 ID: ${menuMap.keys.take(5).toList()}\n");

    return menuMap;
  }

  static List<Restaurant> _parseRestaurants(
    String csv,
    Map<String, List<Menu>> menuMap,
  ) {
    print("🏪 === 레스토랑 파싱 시작 ===");
    final lines = const LineSplitter().convert(csv);
    print("CSV 라인 수: ${lines.length}");
    final restaurants = <Restaurant>[];

    for (int i = 1; i < lines.length; i++) {
      final fields = lineSafeSplit(lines[i]);

      if (fields.length < 11) continue;

      try {
        final id = fields[0].trim();
        final name = fields[1].trim();
        final address = fields[2].trim();
        final phone = fields[3].trim();
        final businessHour = fields[4].trim();
        final category = fields[5].trim();
        final notes = fields[6].trim();
        final placeId = fields[10].trim();

        final menus = menuMap[id] ?? [];

        restaurants.add(
          Restaurant(
            id: id,
            name: name,
            address: address,
            phone: phone,
            businessHour: businessHour,
            category: category,
            notes: notes,
            placeId: placeId,
            menus: menus,
          ),
        );

        if (i <= 5) {
          print(
            "✅ 성공 ${restaurants.length}: ${name} (ID: ${id})\n   카테고리: ${category}, 메뉴: ${menus.length}개",
          );
        }
      } catch (e) {
        print('❌ 레스토랑 파싱 실패 (라인 $i): $e');
      }
    }

    print("파싱 완료: 성공 ${restaurants.length}개, 실패 0개\n");
    return restaurants;
  }

  /// CSV 필드 내 쉼표를 고려한 split (예: "서울, 성북구" 같은 필드)
  static List<String> lineSafeSplit(String line) {
    final List<String> result = [];
    final buffer = StringBuffer();
    bool inQuotes = false;

    for (int i = 0; i < line.length; i++) {
      final char = line[i];

      if (char == '"') {
        inQuotes = !inQuotes;
      } else if (char == ',' && !inQuotes) {
        result.add(buffer.toString());
        buffer.clear();
      } else {
        buffer.write(char);
      }
    }

    result.add(buffer.toString());
    return result;
  }
}
