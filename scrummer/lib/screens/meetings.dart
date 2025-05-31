import 'dart:io';
import 'package:flutter/material.dart';

class Meetings extends StatefulWidget{
  final String folderPath;
  final Map<String, String> users;

  const Meetings({
    super.key,
    required this.folderPath,
    required this.users
  });

  @override
  MeetingsState createState() => MeetingsState();

}

class MeetingsState extends State<Meetings> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Meetings')),
      body: Center(
        child: Text('Omegalol')),
    );
  }
}