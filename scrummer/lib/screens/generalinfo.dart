import 'dart:io';
import 'package:flutter/material.dart';

class GeneralInfo extends StatefulWidget{
  final String folderPath;
  final Map<String, String> users;

  const GeneralInfo({
    super.key,
    required this.folderPath,
    required this.users
  });

  @override
  GeneralInfoState createState() => GeneralInfoState();

}

class GeneralInfoState extends State<GeneralInfo> {

  Map<String, String> data = {};
  double completion = 0.0;

  @override
  void initState() {
    super.initState();
    initialise();
  }

  Future<void> initialise() async{
    await loadData();
    await loadProgress();
  }

  Future<void> loadData() async{

    final file1 = File('${widget.folderPath}/initialise.txt');
    final lines = await file1.readAsLines();
    final Map<String, String> loadedData = {};

    for(var line in lines){
      final parts = line.split("-");

      if(parts[0] == "startdate"){
        loadedData[parts[0].trim()] = parts[1].trim();
      }else if(parts[0] == "enddate"){
        loadedData[parts[0].trim()] = parts[1].trim();
      }else if(parts[0] == "meeting_time"){
        loadedData[parts[0].trim()] = parts[1].trim();
      }
    }

    final directory = Directory(widget.folderPath);
    String filename2 = " ";
    await for(var entity in directory.list()){
      if(entity is File){
        final name = entity.uri.pathSegments.last;
        if(name.startsWith("setup")){
          filename2 = name;
          break;
        }
      }
    }

    final file2 = File('${widget.folderPath}/$filename2');
    final lines2 = await file2.readAsLines();
    for(var line in lines2){
      final parts = line.split(":");
      if(parts[0] == "server_name"){
        loadedData[parts[0].trim()] = parts[1].trim();
      }else if(parts[0] == "current_week"){
        loadedData[parts[0].trim()] = parts[1].trim();
      }
    }

    setState(() {
      data = loadedData;
    });
  }

  Future<void> loadProgress() async{

    double tasks = 0;
    double completed = 0;

    for(var entry in widget.users.entries){

      final filename = 'workday_${entry.key}.txt';
      final file = File('${widget.folderPath}/$filename');

      if(!await file.exists()){
        continue;
      }

      final lines = await file.readAsLines();
      for(var line in lines){
        tasks++;
        final parts = line.split(",");
        if(parts[2] == "0"){
          completed++;
        }
      }
    }

    setState(() {
      if(tasks == 0){
        completion = 0;
      }else{
        completion = (completed/tasks)*100;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
   return Scaffold(
     appBar: AppBar(title: Text('General information')),
     body: Align(
       alignment: Alignment.topCenter, // Align content horizontally center but top vertically
       child: ConstrainedBox(
         constraints: BoxConstraints(maxWidth: 600), // max width to avoid stretching
         child: Padding(
           padding: const EdgeInsets.all(16),
            child: ListView(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.center, // center text horizontally
                  children: [
                    Text(
                     data["server_name"] ?? 'unknown server',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 36),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 4),
                   Text(
                      'Start date for the project: ${data["startdate"] ?? 'N/A'}',
                     textAlign: TextAlign.center,
                    ),
                   Text(
                     'End date for the project: ${data["enddate"] ?? 'N/A'}',
                     textAlign: TextAlign.center,
                   ),
                   Text(
                     'Current week: ${data["current_week"] ?? 'N/A'}',
                     textAlign: TextAlign.center,
                   ),
                   SizedBox(height: 12),
                   Divider(),
                 ],
               ),

               Text(
                  'Team members:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 8),

                LayoutBuilder(
                  builder: (context, constraints) {
                    final itemWidth = (constraints.maxWidth - 12 * 4) / 5;

                   return Wrap(
                     alignment: WrapAlignment.center, // center horizontally inside Wrap
                     spacing: 12,
                      runSpacing: 8,
                     children: widget.users.entries.map((entry) {
                        return SizedBox(
                         width: itemWidth,
                         child: Column(
                           children: [
                             Text(
                               entry.key,
                               textAlign: TextAlign.center,
                                style: TextStyle(fontWeight: FontWeight.bold),
                             ),
                             SizedBox(height: 4),
                             Text(
                               entry.value,
                               textAlign: TextAlign.center,
                               style: TextStyle(color: Colors.grey),
                             ),
                           ],
                         ),
                       );
                      }).toList(),
                   );
                 },
               ),
               SizedBox(height: 8),
               Divider(),
               Text(
                'Tasks completed: ${completion.toStringAsFixed(2)}%',
                textAlign: TextAlign.center,
               ),
             ],
           ),
         ),
       ),
     ),
   );
  }
}