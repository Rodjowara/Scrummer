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

      final tasksLines = await fileTasks.readAsLines();
      final delaysLines = await fileDelays.readAsLines();

      Set<String> delayed = <String>{};

      loadedTasks.putIfAbsent(entry.key, () => {});
      loadedTasks[entry.key]!.putIfAbsent("completed", () => []);
      loadedTasks[entry.key]!.putIfAbsent("delayed", () => []);
      loadedTasks[entry.key]!.putIfAbsent("unfinished", () => []);

      for(var line in delaysLines){
        final parts = line.split(",");
        delayed.add(parts[0]);
      }

      for(var line in tasksLines){
        final parts = line.split(",");

        if(parts[2] == "0"){
          String message = 'Task: ${parts[3]}, task number: ${parts[2]}, deadline: ${parts[1]}';
          loadedTasks[entry.key]!["completed"]!.add(message);
        }else if(delayed.contains(parts[2])){
          String explanation = "";

          for(var line in tasksLines){
            final parts2 = line.split(",");
            if(parts2[0] == parts[2]){
              explanation = parts2[1];
              break;
            }
          }

          String message = 'Task: ${parts[3]}, task number: ${parts[2]}, deadline: ${parts[1]}, explanation: ${explanation}';
          loadedTasks[entry.key]!["delayed"]!.add(message);
        }else{
          String message = 'Task: ${parts[3]}, task number: ${parts[2]}, deadline: ${parts[1]}';
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
      appBar: AppBar(title: Text('Tasks & Delays')),
      body: Center(
        child: Text('Omegalol')),
    );
  }
}