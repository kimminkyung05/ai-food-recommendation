class AdvancedMenu {
  final String menuId;
  final String restaurantId;
  final String restaurantName;
  final String menuName;
  final String category;
  final int price;
  final double volumeUtilization;
  final String explanation;
  final String? placeId;

  AdvancedMenu({
    required this.menuId,
    required this.restaurantId,
    required this.restaurantName,
    required this.menuName,
    required this.category,
    required this.price,
    required this.volumeUtilization,
    required this.explanation,
    required this.placeId,
  });

  factory AdvancedMenu.fromJson(Map<String, dynamic> json) {
    return AdvancedMenu(
      menuId: json['menu_id'],
      restaurantId: json['restaurant_id'],
      restaurantName: json['restaurant_name'],
      menuName: json['menu_name'],
      category: json['category'],
      price: json['price'],
      volumeUtilization: (json['volume_utilization'] as num).toDouble(),
      explanation: json['explanation'],
      placeId: json['place_id'],
    );
  }
}
