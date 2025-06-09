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

class Meeting{
  final String datetime;
  final String channel;
  final List<String> users;

  const Meeting({
    required this.datetime,
    required this.channel,
    required this.users
  });
}

class MeetingsState extends State<Meetings> {
  List<Meeting> meetings = [];

  @override
  void initState(){
    super.initState();
    loadMeetings();
  }

  Future<void> loadMeetings() async{
    List<Meeting> loadedMeetings = [];
    final file = File('${widget.folderPath}/meeting.txt');
    final lines = await file.readAsLines();

    for(var line in lines){
      final parts = line.split(",");
      String datetime = '${parts[0].trim()} ${parts[1].trim()}';
      String channel = '${parts[2].trim()}';
      List<String> users = [];
      for(int i = 3; i < parts.length; i++){
        users.add(parts[i].trim());
      }
      Meeting meeting = Meeting(datetime: datetime, channel: channel, users: users);
      loadedMeetings.add(meeting);
    }

    setState(() {
      meetings = loadedMeetings;
    });
  }

  @override
  Widget build(BuildContext context) {
   return Scaffold(
     appBar: AppBar(title: const Text('Meetings')),
     body: Center(  // centers the whole list horizontally
        child: ConstrainedBox(
         constraints: const BoxConstraints(maxWidth: 600), // max width for content
         child: Padding(
           padding: const EdgeInsets.all(16),
           child: ListView.builder(
             itemCount: meetings.length,
             itemBuilder: (context, index) {
               final meeting = meetings[index];
               final usersString = meeting.users.join(', ');

               return Card(
                 margin: const EdgeInsets.only(bottom: 16),
                 child: Padding(
                   padding: const EdgeInsets.all(12),
                    child: Column(
                     crossAxisAlignment: CrossAxisAlignment.center, // center horizontally inside card
                      children: [
                       Text(
                         'Datetime: ${meeting.datetime}',
                         style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                         textAlign: TextAlign.center, // center text inside Text widget
                       ),
                       const SizedBox(height: 6),
                       Text(
                         'Channel: ${meeting.channel}',
                         style: const TextStyle(fontSize: 18),
                         textAlign: TextAlign.center,
                       ),
                       const SizedBox(height: 6),
                       Text(
                          'Users: $usersString',
                         style: const TextStyle(fontSize: 18),
                         softWrap: true,
                          textAlign: TextAlign.center,
                       ),
                     ],
                   ),
                 ),
               );
             },
           ),
         ),
       ),
     ),
   );
  }
}