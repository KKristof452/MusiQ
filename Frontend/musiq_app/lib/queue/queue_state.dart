import 'package:equatable/equatable.dart';


abstract class QueueStates extends Equatable {}


class QueueInital extends QueueStates {
  @override
  List<Object> get props => [];
}


class QueueLoading extends QueueStates {
  @override
  List<Object> get props => [];
}


class QueueUpdateSuccess extends QueueStates {
  final List<QueueListItem> queue;

  QueueUpdateSuccess(this.queue);

  @override
  List<Object> get props => [queue];
}


class QueueUpdateFail extends QueueStates {
  final String message;

  QueueUpdateFail(this.message);

  @override
  List<Object> get props => [message];
}


class QueueUploading extends QueueStates {
  @override
  List<Object> get props => [];
}


class QueueUploadSuccess extends QueueStates {
  final List<dynamic> response;

  QueueUploadSuccess(this.response);

  @override
  List<Object> get props => [response];
}


class QueueUploadFail extends QueueStates {
  final String message;

  QueueUploadFail(this.message);

  @override
  List<Object> get props => [message];
}


class QueueExit extends QueueStates {
  final String loggedOutUser;

  QueueExit(this.loggedOutUser);

  @override
  List<Object> get props => [loggedOutUser];
}


class QueueListItem {
  final String title;
  final String artists;
  final String user;

  QueueListItem({required this.title, required this.artists, required this.user});

  factory QueueListItem.fromMap(Map<String, dynamic> data) => QueueListItem(
    title: data['title'],
    artists: data['artists'],
    user: data['user'],
  );
}
