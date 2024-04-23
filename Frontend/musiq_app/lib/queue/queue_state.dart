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
  final List<dynamic> metadata;
  final List<QueueListItem> queue;

  QueueUploadSuccess(this.metadata, this.queue);

  @override
  List<Object> get props => [metadata];
}


class QueueUploadFail extends QueueStates {
  final String message;

  QueueUploadFail(this.message);

  @override
  List<Object> get props => [message];
}


class QueueActionPending extends QueueStates {
  @override
  List<Object> get props => [];
}


class QueueActionSuccess extends QueueStates {
  final List<dynamic> response;

  QueueActionSuccess(this.response);

  @override
  List<Object> get props => [response];
}


class QueueActionFail extends QueueStates {
  final String message;

  QueueActionFail(this.message);

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
  final String id;

  QueueListItem({required this.title, required this.artists, required this.user, required this.id});

  factory QueueListItem.fromMap(Map<String, dynamic> data) => QueueListItem(
    title: data['title'],
    artists: data['artists'].join(' & '),
    user: data['user'],
    id: data['id']
  );
}
