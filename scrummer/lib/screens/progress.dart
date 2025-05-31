import 'dart:io';
import 'package:flutter/material.dart';

class Progress extends StatefulWidget{
  final String folderPath;
  final Map<String, String> users;

  const Progress({
    super.key,
    required this.folderPath,
    required this.users
  });

  @override
  ProgressState createState() => ProgressState();
}

class ProgressState extends State<Progress> {

  

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Progress')),
      body: Center(
        child: Text('Omegalol')),
    );
  } 
}