import 'package:equatable/equatable.dart';

abstract class LoginStates extends Equatable {}

class LoginInitial extends LoginStates {
  @override
  List<Object> get props => [];
}

class LoginLoading extends LoginStates {
  @override
  List<Object> get props => [];
}

class LoginSuccess extends LoginStates {
  @override
  List<Object> get props => [];
}

class LoginAdminSuccess extends LoginStates {
  @override
  List<Object> get props => [];
}

class LoginFail extends LoginStates {
  final String message;

  LoginFail(this.message);

  @override
  List<Object> get props => [message];
}
