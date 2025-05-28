class Menu {
  final String name;
  final int price;
  final int volume;

  Menu({required this.name, required this.price, required this.volume});

  /// CSV 필드 배열로부터 Menu 객체 생성
  factory Menu.fromCsv(List<String> fields) {
    final name = fields[2].trim();
    final price = int.tryParse(fields[4].trim().replaceAll(',', '')) ?? 0;
    final width = int.tryParse(fields[5].trim()) ?? 0;
    final length = int.tryParse(fields[6].trim()) ?? 0;
    final height = int.tryParse(fields[7].trim()) ?? 0;

    final volume = width * length * height;

    return Menu(name: name, price: price, volume: volume);
  }

  @override
  String toString() {
    return 'Menu{name: $name, price: $price, volume: $volume}';
  }
}

class Restaurant {
  final String id;
  final String name;
  final String address;
  final String phone;
  final String businessHour;
  final String category;
  final String notes;
  final String placeId;
  final List<Menu> menus;

  Restaurant({
    required this.id,
    required this.name,
    required this.address,
    required this.phone,
    required this.businessHour,
    required this.category,
    required this.notes,
    required this.placeId,
    required this.menus,
  });

  @override
  String toString() {
    return 'Restaurant{id: $id, name: $name, address: $address, phone: $phone, businessHour: $businessHour, category: $category, notes: $notes, menus: $menus}';
  }
}
