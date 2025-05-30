import 'package:flutter/material.dart';

class Progress extends StatelessWidget {

  final String folderPath;

  const Progress({
    super.key,
    required this.folderPath
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Progress')),
      body: Center(
        child: Text('Folder path: $folderPath')),
    );
  }
}