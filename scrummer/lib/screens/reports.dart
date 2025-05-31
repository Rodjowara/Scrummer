import 'dart:io';
import 'package:flutter/material.dart';

class Reports extends StatefulWidget{
  final String folderPath;
  final Map<String, String> users;

  const Reports({
    super.key,
    required this.folderPath,
    required this.users
  });

  @override
  ReportsState createState() => ReportsState();
}

class ReportsState extends State<Reports> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Reports')),
      body: Center(
        child: Text('Omegalol')),
    );
  }
}