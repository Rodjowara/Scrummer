import 'package:flutter/material.dart';

class TasksDelays extends StatelessWidget {

  final String folderPath;

  const TasksDelays({
    super.key,
    required this.folderPath
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Tasks & Delays')),
      body: Center(
        child: Text('Folder path: $folderPath')),
    );
  }
}