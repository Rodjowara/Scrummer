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
  final List<String> log;

  const Meeting({
    required this.datetime,
    required this.channel,
    required this.users,
    required this.log
  });
}

class MeetingsState extends State<Meetings> {
  List<Meeting> meetings = [];

  @override
  void initState(){
    super.initState();
    loadMeetings();
  }

  Future<void> loadMeetings() async {
    final file = File('${widget.folderPath}/meeting.txt');

    if (!await file.exists()) return;

    final lines = await file.readAsLines();
    List<Meeting> loadedMeetings = [];

    Meeting? currentMeeting;
    List<String> currentLog = [];

    for (var line in lines) {
      // If the line has 4 or more comma-separated values, it's a metadata line
      final parts = line.split(",");

      // Check if this is a metadata line (date format and at least 4 parts)
      final isMetadata = parts.length >= 4 && RegExp(r'\d{2}\.\d{2}\.\d{4}').hasMatch(parts[0].trim());

      if (isMetadata) {
        // Save previous meeting
        if (currentMeeting != null) {
          loadedMeetings.add(Meeting(
            datetime: currentMeeting.datetime,
           channel: currentMeeting.channel,
           users: currentMeeting.users,
           log: List.from(currentLog),
         ));
        }

        // Parse new meeting
        final date = parts[0].trim();
        final time = parts[1].trim();
        final channel = parts[2].trim();
       final users = parts.sublist(3).join(',').split(',').map((u) => u.trim()).where((u) => u.isNotEmpty).toList();

        currentMeeting = Meeting(
          datetime: '$date $time',
          channel: channel,
          users: users,
          log: [],
        );
        currentLog = [];
      } else if (currentMeeting != null) {
        // Add to current log
        currentLog.add(line.trim());
      }
    }

    // Add the final meeting at end of file
    if (currentMeeting != null) {
      loadedMeetings.add(Meeting(
        datetime: currentMeeting.datetime,
        channel: currentMeeting.channel,
        users: currentMeeting.users,
        log: List.from(currentLog),
      ));
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
                       Text(
                          'Log:',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                          ),
                      const SizedBox(height: 4),
                      ...meeting.log.map(
                        (entry) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2),
                          child: Text(
                           entry,
                           style: const TextStyle(fontSize: 16),
                           textAlign: TextAlign.center,
                         ),
                        ),
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