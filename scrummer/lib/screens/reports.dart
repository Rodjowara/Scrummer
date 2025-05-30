import 'package:flutter/material.dart';

class Reports extends StatelessWidget {

  final String folderPath;

  const Reports({
    super.key,
    required this.folderPath
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Reports')),
      body: Center(
        child: Text('Folder path: $folderPath')),
    );
  }
}