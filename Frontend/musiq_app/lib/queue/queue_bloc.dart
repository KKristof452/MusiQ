
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:musiq_app/queue/queue_event.dart';
import 'package:musiq_app/queue/queue_state.dart';
import 'package:dio/dio.dart';

class QueueBloc extends Bloc<QueueEvents, QueueStates> {
  QueueBloc(): super(QueueInital()) {

    on<QueueAdd>(onQueueAdd);
    on<QueueUpdate>(onQueueUpdate);
    on<QueueLogout>(onQueueLogout);
    on<QueueRemoveItem>(onQueueRemoveItem);
    on<QueueReorder>(onQueueReorder);
    on<QueueSetPreferences>(onQueueSetPreferences);
    on<QueueLoadPreferences>(onQueueLoadPreferences);
  }

  void onQueueAdd(QueueAdd event, Emitter<QueueStates> emit) async {
    if (state is QueueUploading) return;
    emit(QueueUploading());

    print('trying to upload audio');

    final formData = FormData.fromMap({
      'uploaded_file': MultipartFile.fromBytes(event.audioFile.bytes!.toList(), filename: event.audioFile.name),
    });
    try {
      print('sending post request');
      var response = await GetIt.I<Dio>().post('/queue/add', data: formData);

      print(response.data);
      List<QueueListItem> queue = generateQueueListItems(response.data['Queue']);
      emit(QueueUploadSuccess(response.data['Filtered metadata'], queue));

    } on DioException catch (e) {
      if (e.response != null) {
        print(e.response);
        emit(QueueUploadFail(e.response?.data['message']));
      } else {
        print('Something went wrong...');
        emit(QueueUploadFail('Something went wrong...'));
      }
    }
  }

  void onQueueUpdate(QueueUpdate event, Emitter<QueueStates> emit) async {
    if (state is QueueLoading) return;
    emit(QueueLoading());

    try {
      var response = await GetIt.I<Dio>().get('/queue/list');

      List<QueueListItem> queueListItems = generateQueueListItems(response.data);

      emit(QueueUpdateSuccess(queueListItems));

    } on DioException catch (e) {
      if (e.response != null) {
        emit(QueueUpdateFail(e.response?.data['message']));
      } else {
        emit(QueueUpdateFail('Something went wrong...'));
      }
    } catch (e) {
      emit(QueueUpdateFail(e.toString()));
    }
  }

  void onQueueLogout(QueueLogout event, Emitter<QueueStates> emit) async {
    if (state is QueueUploading) return;

    try {
      var response = await GetIt.I<Dio>().post('/queue/logout');
      if (response.data['Result'] == 'Success') {
        final String loggedOutUser = response.data['User']['username'];
        emit(QueueExit(loggedOutUser));
        emit(QueueInital());
      }
    } on DioException catch (e) {
      if (e.response != null) {
        //emit(QueueUpdateFail(e.response?.data['message']));
        print('ERR: ${e.response?.data['message']}');
      } else {
        //emit(QueueUpdateFail('Something went wrong...'));
        print('Something went wrong...\n${e.toString()}}');
      }
    } catch (e) {
      print('ERROR: ${e.toString()}');
    }
  }

  void onQueueRemoveItem(QueueRemoveItem event, Emitter<QueueStates> emit) async {
    if (state is QueueLoading) return;
    emit(QueueLoading());

    try {
      var response = await GetIt.I<Dio>().delete('/queue/${event.itemId}/remove');
      List<QueueListItem> queue = generateQueueListItems(response.data);
      emit(QueueUpdateSuccess(queue));
    } on DioException catch (e) {
      if (e.response != null) {
        emit(QueueUpdateFail(e.response?.data['message']));
        print('ERR: ${e.response?.data['message']}');
      } else {
        emit(QueueUpdateFail('Something went wrong...'));
        print('Something went wrong...\n${e.toString()}}');
      }
    } catch (e) {
      print('[onQueueRemoveItem] ${e.toString()}');
    }
  }

  void onQueueReorder(QueueReorder event, Emitter<QueueStates> emit) async {
    if (state is QueueLoading || state is QueueActionPending) return;
    emit(QueueActionPending());

    try {
      final Map<String, int> queryParameters = {
        'old_index': event.oldIndex,
        'new_index': event.newIndex
      };
      var response = await GetIt.I<Dio>().patch('/queue/${event.id}/move', queryParameters: queryParameters);
      List<QueueListItem> queue = generateQueueListItems(response.data);
      emit(QueueUpdateSuccess(queue));
    } on DioException catch (e) {
      if (e.response != null) {
        emit(QueueUpdateFail(e.response?.data['message']));
        print('ERR: ${e.response?.data['message']}');
      } else {
        emit(QueueUpdateFail('Something went wrong...'));
        print('Something went wrong...\n${e.toString()}}');
      }
    } catch (e) {
      print('[onQueueReorder] ${e.toString()}');
    }
  }

  void onQueueSetPreferences(QueueSetPreferences event, Emitter<QueueStates> emit) async {
    if (state is QueuePreferencesLoading) {
      return;
    }
    emit(QueuePreferencesLoading());

    try {
      var response = await GetIt.I<Dio>().post('/queue/settings/preferences', data: event.preferences);

    } on DioException catch (e) {
      if (e.response != null) {
        //emit(QueueUpdateFail(e.response?.data['message']));
        print('ERR: ${e.response?.data}');
      } else {
        //emit(QueueUpdateFail('Something went wrong...'));
        print('Something went wrong...\n${e.toString()}}');
      }
    } catch (e) {
      print('[onQueueReorder] ${e.toString()}');
    }
    
  }

  void onQueueLoadPreferences(QueueLoadPreferences event, Emitter<QueueStates> emit) async {
    if (state is QueuePreferencesLoading) {
      return;
    }
    emit(QueuePreferencesLoading());

    try {
      var response = await GetIt.I<Dio>().get('/queue/settings/preferences');
      print(response.data);
      emit(QueuePreferencesLoaded(response.data));

    } on DioException catch (e) {
      if (e.response != null) {
        //emit(QueueUpdateFail(e.response?.data['message']));
        print('ERR: ${e.response?.data}');
      } else {
        //emit(QueueUpdateFail('Something went wrong...'));
        print('Something went wrong...\n${e.toString()}}');
      }
    } catch (e) {
      print('[onQueueReorder] ${e.toString()}');
    }

  }
}


List<QueueListItem> generateQueueListItems(List<dynamic> queue) {
    List<QueueListItem> queueListItems = [];
    for (final song in queue) {
      queueListItems.add(QueueListItem.fromMap(song));
    }
    return queueListItems;
  }