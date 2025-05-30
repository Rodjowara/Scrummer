import 'package:flutter/material.dart';

class Meetings extends StatelessWidget {

  final String folderPath;

  const Meetings({
    super.key,
    required this.folderPath
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Meetings')),
      body: Center(
        child: Text('Folder path: $folderPath')),
    );
  }
}