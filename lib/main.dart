import 'package:flutter/material.dart';
import 'pages/home_page.dart';

void main() {
  runApp(const YonggiRoadApp());
}

class YonggiRoadApp extends StatelessWidget {
  const YonggiRoadApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '용기있는길',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),
      debugShowCheckedModeBanner: false,
      home: const HomePage(),
    );
  }
}
