import 'dart:math';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:musiq_app/queue/queue_bloc.dart';
import 'package:musiq_app/queue/queue_event.dart';
import 'package:musiq_app/queue/queue_state.dart';

enum SampleItem { itemOne }

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
  int currentPageIndex = 0;

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<QueueBloc, QueueStates>(
      listener: (context, state) {
        if (state is QueueUpdateSuccess) {
          queue = state.queue;
        } else if (state is QueueUpdateFail) {
          ScaffoldMessenger.of(context)
              .showSnackBar(SnackBar(content: Text(state.message)));
        } else if (state is QueueUploadFail) {
          ScaffoldMessenger.of(context)
              .showSnackBar(SnackBar(content: Text(state.message)));
        } else if (state is QueueUploadSuccess) {
          ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.metadata[0]['title'])));
          queue = state.queue;
        } else if (state is QueueExit) {
          ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('${state.loggedOutUser} logged out.')));
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
                      }),
                ),
              ]),
          bottomNavigationBar: NavigationBar(
            onDestinationSelected: (index) {
              setState(() {
                currentPageIndex = index;
              });
            },
            indicatorColor: Colors.amber,
            surfaceTintColor: Colors.white,
            backgroundColor: Colors.amber[200],
            selectedIndex: currentPageIndex,
            destinations: const <Widget>[
              NavigationDestination(
                icon: Icon(Icons.queue_music),
                label: 'Q',
              ),
              NavigationDestination(
                selectedIcon: Icon(Icons.settings),
                icon: Icon(Icons.settings_outlined),
                label: 'Settings',
              ),
            ],
          ),
          body: <Widget>[
            state is QueueLoading
                ? const Center(child: CircularProgressIndicator())
                : Column(
                    children: [
                      Expanded(
                        flex: 3,
                        child: ReorderableListView.builder(
                            padding: const EdgeInsets.all(25.0),
                            onReorder: (oldIndex, newIndex) {
                              setState(() {
                                if (oldIndex < newIndex) newIndex -= 1;
                                print(
                                    'oldIndex: $oldIndex - newIndex: $newIndex');
                                var song = queue.removeAt(oldIndex);
                                var songId = song.id;
                                queue.insert(newIndex, song);
                                context.read<QueueBloc>().add(
                                    QueueReorder(songId, oldIndex, newIndex));
                              });
                            },
                            itemCount: queue.length,
                            itemBuilder: (context, index) {
                              final item = queue[index];
                              return QueueItem(index, context, item);
                            }),
                      ),
                      Expanded(
                          flex: 1,
                          child: Row(
                            mainAxisSize: MainAxisSize.max,
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              IconButton(
                                  onPressed: () => print('fast rewind'),
                                  icon: Icon(
                                    Icons.fast_rewind,
                                    size: 50,
                                  )),
                              IconButton(
                                  onPressed: () => print('play/pause'),
                                  icon: Icon(
                                    Icons.play_arrow,
                                    size: 50,
                                  )),
                              IconButton(
                                  onPressed: () => print('fast forward'),
                                  icon: Icon(
                                    Icons.fast_forward,
                                    size: 50,
                                  ))
                            ],
                          ))
                    ],
                  ),
            const PreferenceView(),
          ][currentPageIndex],
          floatingActionButton: currentPageIndex == 0
              ? Padding(
                  padding: const EdgeInsets.fromLTRB(0, 0, 25, 25),
                  child: FloatingActionButton(
                    backgroundColor: Colors.amber[400],
                    hoverColor: Colors.amber,
                    onPressed: () async {
                      if (state is QueueUploading) return;
                      FilePickerResult? result = await FilePicker.platform
                          .pickFiles(type: FileType.audio);
                      print('FilePicker closed');
                      if (result != null && context.mounted) {
                        final audioFile = result.files.first;
                        print('File was chosen');
                        print(audioFile.name);
                        context.read<QueueBloc>().add(QueueAdd(audioFile));
                      }
                    },
                    child: state is QueueUploading
                        ? const CircularProgressIndicator()
                        : const Icon(Icons.add),
                  ),
                )
              : null,
        );
      },
    );
  }

  GestureDetector QueueItem(
      int index, BuildContext context, QueueListItem item) {
    return GestureDetector(
      key: ValueKey(queue[index]),
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
      onTap: () {
        showDialog(
            context: context,
            builder: (BuildContext context) {
              return Dialog(
                child: Padding(
                  padding: const EdgeInsets.all(15.0),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Title: ${item.title}'),
                      Text('Artists: ${item.artists}'),
                      Text('Genre: ${item.genre}'),
                      Text('BPM: ${item.bpm}'),
                      Text('Mood: ${item.mood}'),
                      Text('Voice gender: ${item.voiceGender}'),
                      Text('Key: ${item.key}'),
                      Text('Fixed position: ${item.fixedPosition}')
                    ],
                  ),
                ),
              );
            });
      },
      onLongPress: () {
        showSongTileMenu(context, index);
      },
      child: SongTile(item: item),
    );
  }

  Future<SampleItem?> showSongTileMenu(BuildContext context, int index) {
    return showMenu(
        context: context,
        position: menuRect,
        constraints: const BoxConstraints(
            minWidth: 0,
            maxWidth: double.infinity,
            minHeight: 0,
            maxHeight: double.infinity),
        items: <PopupMenuEntry<SampleItem>>[
          PopupMenuItem<SampleItem>(
            value: SampleItem.itemOne,
            child: const Center(child: Icon(Icons.delete)),
            onTap: () {
              var itemId = queue[index].id;
              context.read<QueueBloc>().add(QueueRemoveItem(itemId));
            },
          ),
        ]);
  }
}

class PreferenceView extends StatefulWidget {
  const PreferenceView({super.key});

  @override
  State<PreferenceView> createState() => _PreferenceView();
}

class _PreferenceView extends State<PreferenceView> {
  @override
  void initState() {
    super.initState();
    context.read<QueueBloc>().add(QueueLoadPreferences());
  }

  Map<String, dynamic> preferences = {};
  final artistsController = TextEditingController();
  final genresController = TextEditingController();
  final minBpmController = TextEditingController();
  final maxBpmController = TextEditingController();
  final moodController = TextEditingController();
  final voiceGenderController = TextEditingController();
  final keysController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<QueueBloc, QueueStates>(
      listener: (context, state) {
        if (state is QueuePreferencesLoaded) {
          var minBpm = state.preferences['min_bpm']; 
          var maxBpm = state.preferences['max_bpm'];

          artistsController.text = state.preferences['artists'].join(', ');
          genresController.text = state.preferences['genre'].join(', ');
          minBpmController.text = (minBpm == 0) ? '' : minBpm.toString();
          maxBpmController.text = (maxBpm == 0) ? '' : maxBpm.toString();
          moodController.text = state.preferences['mood'].join(', ');
          voiceGenderController.text = state.preferences['voice_gender'].join(', ');
          keysController.text = state.preferences['key'].join(', ');
          print('habakukk');
        }
      },
      builder: (context, state) {
        return ListView(
          padding: const EdgeInsets.all(25.0),
          children: <Widget>[
            const Padding(
              padding: EdgeInsets.only(bottom: 15.0),
              child: Text(
                'Preferences',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
              ),
            ),
            TextFormField(
              decoration: const InputDecoration(
                labelText: 'Artists',
              ),
              controller: artistsController,
            ),
            TextFormField(
              decoration: const InputDecoration(
                labelText: 'Genres',
              ),
              controller: genresController,
            ),
            IntrinsicHeight(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: TextFormField(
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      decoration: const InputDecoration(
                        labelText: 'Min BPM',
                        hintText: 'E.g. 80',
                      ),
                      controller: minBpmController,
                    ),
                  ),
                  Expanded(
                    child: TextFormField(
                      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                      decoration: const InputDecoration(
                        labelText: 'Max BPM',
                        hintText: 'E.g. 120',
                      ),
                      controller: maxBpmController,
                    ),
                  ),
                ],
              ),
            ),
            TextFormField(
              decoration: const InputDecoration(
                labelText: 'Mood',
              ),
              controller: moodController,
            ),
            TextFormField(
              decoration: const InputDecoration(
                  labelText: 'Voice gender', hintText: 'Male/Female'),
              controller: voiceGenderController,
            ),
            TextFormField(
              decoration: const InputDecoration(
                labelText: 'Keys',
              ),
              controller: keysController,
            ),
            Padding(
              padding: const EdgeInsets.only(top: 15.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  ElevatedButton(
                    onPressed: () {
                      var preferences = {
                        'artists': formatPreferenceText(artistsController),
                        'genre': formatPreferenceText(genresController),
                        'min_bpm': minBpmController.text.isNotEmpty
                            ? int.tryParse(minBpmController.text)
                            : 0,
                        'max_bpm': maxBpmController.text.isNotEmpty
                            ? int.tryParse(maxBpmController.text)
                            : 0,
                        'mood': formatPreferenceText(moodController),
                        'voice_gender':
                            formatPreferenceText(voiceGenderController),
                        'key': formatPreferenceText(keysController)
                      };
                      print(preferences);
                      context
                          .read<QueueBloc>()
                          .add(QueueSetPreferences(preferences));
                    },
                    child: const Text('Save'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      showDialog(
                          context: context,
                          builder: (BuildContext context) {
                            return AlertDialog(
                              content: const Text(
                                  'Are you sure to clear the preferences?'),
                              actions: <Widget>[
                                TextButton(
                                  onPressed: () =>
                                      Navigator.pop(context, 'Cancel'),
                                  child: const Text('Cancel'),
                                ),
                                TextButton(
                                  onPressed: () {
                                    print("Cancel");
                                  },
                                  child: const Text('Yes'),
                                ),
                              ],
                            );
                          });
                    },
                    child: const Text('Clear'),
                  )
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

class SongTile extends StatelessWidget {
  const SongTile({
    super.key,
    required this.item,
  });

  final QueueListItem item;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 5,
      child: ListTile(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        tileColor: Colors.amber[300],
        title: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('${item.title} - (${item.artists})'),
          ],
        ),
        subtitle: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(item.user),
          ],
        ),
      ),
    );
  }
}

List<dynamic> formatPreferenceText(TextEditingController controller) {
  List<dynamic> formattedPreference =
      controller.text.split(',').map((element) => element.trim()).toList();
  return formattedPreference;
}
