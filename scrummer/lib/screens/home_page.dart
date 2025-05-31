import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:scrummer/screens/meetings.dart';
import 'package:scrummer/screens/reports.dart';
import 'generalinfo.dart';
import 'progress.dart';
import 'tasksdelays.dart';
import 'package:path/path.dart' as p;

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? folderPath;
  String? selectedCategory;
  Map<String, String> users = {};

  final List<String> viewOptions = [
    "General Information",
    "Progress",
    "Tasks & Delays",
    "Meetings",
    "Reports"
  ];

  Future<void> loadFolder() async{
    await pickFile();
    if(folderPath != null){
      await loadUsers();
    }
  }

  Future<void> loadUsers() async{

    final file = File('$folderPath/initialise.txt');
    final lines = await file.readAsLines();
    final Map<String, String> loadedUsers = {};

    for(var line in lines){
      final parts = line.split("-");

      if(parts[0] == "role"){
        final user = parts[1].split(":");
        loadedUsers[user[0].trim()] = user[1].trim();
      }
    }

    setState(() {
      users = loadedUsers;
    });
  }

  Future<void> pickFile() async {
    String? selectedDirectory = await FilePicker.platform.getDirectoryPath();

    if (selectedDirectory != null) {

      final directory = Directory(selectedDirectory);
      final List<FileSystemEntity> files = await directory.list().toList();
      final fileList = files.whereType<File>();

      int count = 0;
      for(var file in fileList){
        String filename = p.basename(file.path);
        if(filename.startsWith("setup") || filename.startsWith("initialise")){
          count++;
        }
      }

      if(count < 2){
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Invalid folder: doesn't contain the setup file or the initialise file"))
        );
      }else{
        setState(() {
            folderPath = selectedDirectory;
        });
      }

    }
  }

  void navigateToPage(String selectedOption){
    
    if(selectedOption == "General Information"){
      Navigator.push(context, MaterialPageRoute(builder: (_) => GeneralInfo(folderPath: folderPath ?? "No folder selected", users: users,)));
    }else if(selectedOption == "Progress"){
      Navigator.push(context, MaterialPageRoute(builder: (_) => Progress(folderPath: folderPath ?? "No folder selected", users: users)));
    }else if(selectedOption == "Tasks & Delays"){
      Navigator.push(context, MaterialPageRoute(builder: (_) => TasksDelays(folderPath: folderPath ?? "No folder selected", users: users)));
    }else if(selectedOption == "Meetings"){
      Navigator.push(context, MaterialPageRoute(builder: (_) => Meetings(folderPath: folderPath ?? "No folder selected", users: users)));
    }else if(selectedOption == "Reports"){
      Navigator.push(context, MaterialPageRoute(builder: (_) => Reports(folderPath: folderPath ?? "No folder selected", users: users)));
    }else{
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Page for "$selectedOption" not yet implemented'))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                'Scrummer Dashboard',
                style: TextStyle(fontSize: 48, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 40),
              ElevatedButton(
                onPressed: loadFolder,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(200, 50),
                  padding: const EdgeInsets.only(bottom: 12)
                ),
                child: const Text(
                          'Choose Folder',
                          style: TextStyle(fontSize: 20),
                          //textAlign: TextAlign.center,
                      ),
              ),

              const SizedBox(height: 20),
              Text(
                folderPath ?? 'No folder selected',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),

              const SizedBox(height: 20),
              Center(
                child: DropdownButton<String>(
                  //isExpanded: true,
                  alignment: Alignment.center,
                  padding: const EdgeInsets.only(left: 17),
                  hint: const Text(
                    "Select a category",
                    textAlign: TextAlign.center,
                  ),
                  value: selectedCategory,
                  onChanged: (String? newValue){
                    setState(() {
                      selectedCategory = newValue;
                    });

                    if(newValue != null && folderPath != null){
                      navigateToPage(newValue);
                    }

                  },
                  items: viewOptions.map<DropdownMenuItem<String>>((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Center(child: Text(
                        value,
                        textAlign: TextAlign.center,
                      )),
                    );
                  }).toList(),
                )
              ),
            ],
          ),
        ),
      ),
    );
  }
}