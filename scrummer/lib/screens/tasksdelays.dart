import 'dart:io';
import 'package:flutter/material.dart';

class TasksDelays extends StatefulWidget{
  final String folderPath;
  final Map<String, String> users;

  const TasksDelays({
    super.key,
    required this.folderPath,
    required this.users
  });

  @override
  TasksDelaysState createState() => TasksDelaysState();
}

class TasksDelaysState extends State<TasksDelays> {

  Map<String, Map<String, List<String>>> tasks = {};

  @override
  void initState(){
    super.initState();
    initialise();
  }

  Future<void> initialise() async{
    await loadTasks();
  }

  Future<void> loadTasks() async{
    Map<String, Map<String, List<String>>> loadedTasks = {};

    for(var entry in widget.users.entries){

      final filenameTasks = '${widget.folderPath}/workday_${entry.key}.txt';
      final filenameDelays = '${widget.folderPath}/delay_${entry.key}.txt';

      final fileTasks = File(filenameTasks);
      final fileDelays = File(filenameDelays);

      if(!await fileTasks.exists()){
        continue;
      }else if(!await fileDelays.exists()){
        continue;
      }

      final tasksLines = await fileTasks.readAsLines();
      final delaysLines = await fileDelays.readAsLines();

      Set<String> delayed = <String>{};

      loadedTasks.putIfAbsent(entry.key, () => {});
      loadedTasks[entry.key]!.putIfAbsent("completed", () => []);
      loadedTasks[entry.key]!.putIfAbsent("delayed", () => []);
      loadedTasks[entry.key]!.putIfAbsent("unfinished", () => []);

      for(var line in delaysLines){
        final parts = line.split(",");
        delayed.add(parts[0].trim());
      }

      for(var line in tasksLines){
        final parts = line.split(",");

        if(parts[2] == "0"){
          String message = 'Task: ${parts[3].trim()}, deadline: ${parts[1].trim()}';
          loadedTasks[entry.key]!["completed"]!.add(message);
        }else if(delayed.contains(parts[2])){
          String explanation = "";

          for(var line in delaysLines){
            final parts2 = line.split(",");
            if(parts2[0].trim() == parts[2].trim()){
              explanation = parts2[1].trim();
              break;
            }
          }

          String message = 'Task: ${parts[3].trim()}, task number: ${parts[2].trim()}, deadline: ${parts[1].trim()}, \nexplanation: ${explanation}';
          loadedTasks[entry.key]!["delayed"]!.add(message);

        }else{
          String message = 'Task: ${parts[3].trim()}, task number: ${parts[2].trim()}, deadline: ${parts[1].trim()}';
          loadedTasks[entry.key]!["unfinished"]!.add(message);
        }
      }
    }

    setState(() {
      tasks = loadedTasks;
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

           final userTasks = tasks[userName] ?? {};
           final completed = userTasks["completed"] ?? [];
           final delayed = userTasks["delayed"] ?? [];
           final unfinished = userTasks["unfinished"] ?? [];

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
                      const Text(
                        'Completed:',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                      ),
                      if (completed.isEmpty)
                        const Text('No completed tasks', textAlign: TextAlign.center)
                      else
                        ...completed.map(
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
                      const Text(
                        'Delayed:',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                      ),
                      if (delayed.isEmpty)
                        const Text('No delayed tasks', textAlign: TextAlign.center)
                      else
                        ...delayed.map(
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
                      const Text(
                        'Unfinished:',
                       style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                      ),
                      if (unfinished.isEmpty)
                        const Text('No unfinished tasks', textAlign: TextAlign.center)
                      else
                        ...unfinished.map(
                          (task) => Padding(
                           padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text(
                             task,
                             textAlign: TextAlign.center,
                             style: const TextStyle(fontSize: 16),
                           ),
                         ),
                       ),
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