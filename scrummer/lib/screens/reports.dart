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
  Map<String, List<String>> reports = {};

  @override
  void initState(){
    super.initState();
    loadReports();
  }

  Future<void> loadReports() async {
    Map<String, List<String>> loadedReports = {};
    final file = File('${widget.folderPath}/reports.txt');

    bool exists = true;

    if(!await file.exists()){
      exists = false;
    }

    if(exists){
      final lines = await file.readAsLines();

      for(var entry in widget.users.entries){
        loadedReports.putIfAbsent(entry.key, () => []);
      }

      for(var line in lines){
        final parts = line.split(",");
        loadedReports[parts[0].trim()]!.add(parts[1].trim());
      }

      setState(() {
        reports = loadedReports;
      });
    }else{
      setState(() {
        reports = {};
      });
    }
  }

  @override
  Widget build(BuildContext context) {
   return Scaffold(
     appBar: AppBar(title: const Text('Reports')),
     body: Padding(
       padding: const EdgeInsets.all(16),
       child: GridView.count(
         crossAxisCount: 3,
         crossAxisSpacing: 16,
         mainAxisSpacing: 16,
         childAspectRatio: 0.75,
         children: widget.users.entries.map((entry) {
           final userName = entry.key;
           final reportsList = reports[userName] ?? [];

           return Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      userName,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                     ),
                    ),
                    const SizedBox(height: 8),
                    if (reportsList.isEmpty)
                      const Text(
                       'No reports for this member',
                       textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 14),
                      )
                   else
                     ...reportsList.map(
                       (report) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 2),
                          child: Text(
                            'Reported for: $report',
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 14),
                          ),
                        ),
                      ),
                 ],
               ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}