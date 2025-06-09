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

  Map<String, List<String>> progress = {};

  @override
  void initState(){
    super.initState();
    loadProgress();
  }

  Future<void> loadProgress() async{

    Map<String, List<String>> loadedProgress = {};

    for(var entry in widget.users.entries){
      loadedProgress.putIfAbsent(entry.key, () => []);
    }

    final file = File('${widget.folderPath}/progress.txt');
    final lines = await file.readAsLines();
    for(var line in lines){
      var parts = line.split("|");

      if(parts.length == 4){
        String message = '${parts[0].trim()} ${parts[2].trim()}, \n${parts[3].trim()}';
        loadedProgress[parts[1].trim()]!.add(message);
      }else{
        String message = '${parts[0].trim()}, ${parts[2].trim()}';
        loadedProgress[parts[1].trim()]!.add(message);
      }
    }

    setState(() {
      progress = loadedProgress;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
     appBar: AppBar(title: const Text('Tasks & Delays')),
     body: Padding(
       padding: const EdgeInsets.all(16),
       child: GridView.count(
          crossAxisCount: 3, // Max 3 users per row
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
         childAspectRatio: 0.75,
         children: widget.users.entries.map((entry) {
           final userName = entry.key;
           final userRole = entry.value;

           final List<String> userProgress = progress[userName] ?? [];

            return Card(
              elevation: 3,
              shape: RoundedRectangleBorder(
               borderRadius: BorderRadius.circular(12),
              ),
             child: Padding(
               padding: const EdgeInsets.all(12),
               child: SingleChildScrollView(
                 child: Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Text(
                        userName,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                         fontSize: 22,
                       ),
                     ),
                     Text(
                        userRole,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontStyle: FontStyle.italic,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 10),

                      if (userProgress.isEmpty)
                        const Text('No progress reported', textAlign: TextAlign.center)
                      else
                        ...userProgress.map(
                          (task) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text(
                              task,
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontSize: 16),
                           ),
                         ),
                        ),
                      const SizedBox(height: 15),
                   ],
                 ),
               ),
             ),
           );
         }).toList(),
       ),
     ),
   );
  }
}