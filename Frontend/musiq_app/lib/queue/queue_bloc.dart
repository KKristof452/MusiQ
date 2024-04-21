
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
  }

  void onQueueAdd(QueueAdd event, Emitter<QueueStates> emit) async {
    if (state is QueueLoading || state is QueueUploading) return;
    emit(QueueUploading());

    print('trying to upload audio');

    final formData = FormData.fromMap({
      'uploaded_file': MultipartFile.fromBytes(event.audioFile.bytes!.toList(), filename: event.audioFile.name),
    });
    try {
      print('sending post request');
      var response = await GetIt.I<Dio>().post('/queue/add', data: formData);

      print(response.data);

      emit(QueueUploadSuccess(response.data['Filtered metadata']));

    } on DioException catch (e) {
      if (e.response != null) {
        print(e.response);
        emit(QueueUploadFail(e.response?.data['message']));
      }
      else {
        print('Something went wrong...');
        emit(QueueUploadFail('Something went wrong...'));
      }
    }
  }

  void onQueueUpdate(QueueUpdate event, Emitter<QueueStates> emit) async {
    if (state is QueueLoading || state is QueueUploading) return;
    emit(QueueLoading());

    try {
      var response = await GetIt.I<Dio>().get('/queue/list');

      List<QueueListItem> queueListItems = [];
      for (final song in response.data) {
        var title = song['title'];
        var artists = song['artists'].join(' & ');
        var user = song['user'];

        queueListItems.add(QueueListItem(title: title, artists: artists, user: user));
      }

      emit(QueueUpdateSuccess(queueListItems));

    } on DioException catch (e) {
      if (e.response != null) {
        emit(QueueUpdateFail(e.response?.data['message']));
      }
      else {
        emit(QueueUpdateFail('Something went wrong...'));
      }
    } catch (e) {
      emit(QueueUpdateFail(e.toString()));
    }
  }

  void onQueueLogout(QueueLogout event, Emitter<QueueStates> emit) async {
    if (state is QueueLoading || state is QueueUploading) return;
    print('trying to logout 2');
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
      }
      else {
        //emit(QueueUpdateFail('Something went wrong...'));
        print('Something went wrong...\n${e.toString()}}');
      }
    } catch (e) {
      print('ERROR: ${e.toString()}');
    }
  }
}