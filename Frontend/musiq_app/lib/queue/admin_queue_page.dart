
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:musiq_app/queue/queue_bloc.dart';
import 'package:musiq_app/queue/queue_event.dart';
import 'package:musiq_app/queue/queue_state.dart';


enum SampleItem { itemOne, itemTwo, itemThree }


class AdminQueuePageBloc extends StatefulWidget {
  const AdminQueuePageBloc({super.key});

  @override
  State<AdminQueuePageBloc> createState() => _AdminQueuePageBlocState();
}


class _AdminQueuePageBlocState extends State<AdminQueuePageBloc> {

  @override
  void initState() {
    super.initState();
    context.read<QueueBloc>().add(QueueUpdate());
  }

  List<QueueListItem> queue = [];
  late RelativeRect menuRect;

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<QueueBloc, QueueStates>(
        listener: (context, state) {
          if (state is QueueUpdateSuccess) {
            queue = state.queue;
          }
          else if (state is QueueUpdateFail) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
          }
          else if (state is QueueUploadFail) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.message)));
          }
          else if (state is QueueUploadSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.response[0]['title'])));
          }
          else if (state is QueueExit) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${state.loggedOutUser} logged out.')));
            Navigator.pushReplacementNamed(context, '/');
          }
        },
        builder: (context, state) {
          return Scaffold(
            appBar: AppBar(
              leading: IconButton(
                icon: Transform.flip(
                  flipX: true,
                  child: const Icon(Icons.logout),
                ),
                onPressed: () {
                  print('trying to logout');
                  context.read<QueueBloc>().add(QueueLogout());
                },
              ),
              title: const Text('MusiQ'),
              actions: [
                Padding(
                  padding: const EdgeInsets.only(right: 50.0),
                  child: IconButton(
                    icon: const Icon(Icons.autorenew),
                    onPressed: () {
                      context.read<QueueBloc>().add(QueueUpdate());
                    }
                  ),
                ),
              ]
            ),
            body: state is QueueLoading ? const Center(
              child: CircularProgressIndicator()
            ) : ListView.builder(
              padding: const EdgeInsets.all(25.0),
              itemCount: queue.length,
              itemBuilder: (context, index) {
                final item = queue[index];
                return GestureDetector(
                  onTapDown: (TapDownDetails details) {
                    final tapPosition = details.globalPosition;

                    // Calculate top left corner of the relative rect
                    final double left = tapPosition.dx;
                    final double top = tapPosition.dy;

                    // Create the RelativeRect object
                    final relativeRect = RelativeRect.fromLTRB(left, top, left, top);

                    print(relativeRect);
                    menuRect = relativeRect;
                  },
                  onLongPress: () {
                    showMenu(
                      context: context,
                      position: menuRect,
                      constraints: const BoxConstraints(minWidth: 0, maxWidth: double.infinity, minHeight: 0, maxHeight: double.infinity),
                      items: <PopupMenuEntry<SampleItem>>[
                        const PopupMenuItem<SampleItem>(
                          value: SampleItem.itemOne,
                          child: Center(child: Icon(Icons.upload)),
                        ),
                        const PopupMenuItem<SampleItem>(
                          value: SampleItem.itemTwo,
                          child: Center(child: Icon(Icons.download)),
                        ),
                        const PopupMenuItem<SampleItem>(
                          value: SampleItem.itemThree,
                          child: Center(child: Icon(Icons.delete)),
                        ),
                      ]
                    );
                  },
                  child: Card(
                    elevation: 5,
                    child: ListTile( 
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)
                      ),
                      tileColor: Colors.amber[200],
                      title: Center(child: Text('${item.title} - (${item.artists})')),
                      subtitle: Center(child: Text(item.user)),
                      
                    ),
                  ),
                );
              },
            ),
            floatingActionButton: Padding(
              padding: const EdgeInsets.fromLTRB(0, 0, 25, 25),
              child: FloatingActionButton(
                onPressed: () async {
                  if (state is QueueUploading) return;
                  FilePickerResult? result = await FilePicker.platform.pickFiles(type: FileType.audio);
                  print('FilePicker closed');
                  if (result != null && context.mounted) {
                    final audioFile = result.files.first;
                    print('File was chosen');
                    print(audioFile.name);
                    context.read<QueueBloc>().add(QueueAdd(audioFile));
                  }
                },
                child: state is QueueUploading ? const CircularProgressIndicator() : const Icon(Icons.add),
                
              ),
            ),
          );
        },
    );
  }
}