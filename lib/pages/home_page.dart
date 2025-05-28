import 'package:flutter/material.dart';
import 'result_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController widthController = TextEditingController();
  final TextEditingController lengthController = TextEditingController();
  final TextEditingController heightController = TextEditingController();

  String selectedCategory = '전체';

  final List<String> categories = ['전체', '한식', '중식', '양식', '기타'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("용기있는길")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: ListView(
          children: [
            const Text(
              "어떤 종류가 땡기세요?",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 10,
              children: categories.map((category) {
                return ChoiceChip(
                  label: Text(category),
                  selected: selectedCategory == category,
                  onSelected: (bool selected) {
                    setState(() {
                      selectedCategory = category;
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 30),
            _buildInput("가로 (cm)", widthController),
            _buildInput("세로 (cm)", lengthController),
            _buildInput("높이 (cm)", heightController),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {
                double width = double.tryParse(widthController.text) ?? 0;
                double length = double.tryParse(lengthController.text) ?? 0;
                double height = double.tryParse(heightController.text) ?? 0;
                double volume = width * length * height;

                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ResultPage(
                      selectedCategory: selectedCategory,
                      containerVolume: volume,
                    ),
                  ),
                );
              },
              child: const Text("추천받기"),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInput(String label, TextEditingController controller) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        keyboardType: TextInputType.number,
      ),
    );
  }
}
