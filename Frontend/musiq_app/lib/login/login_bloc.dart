import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:musiq_app/login/login_event.dart';
import 'package:musiq_app/login/login_state.dart';

class LoginBloc extends Bloc<LoginEvents, LoginStates> {
  LoginBloc() : super(LoginInitial()) {
    
    on<LoginAdminSubmit>(onLoginAdminSubmit);
    on<LoginSubmit>(onLoginSubmit);
  }

  void onLoginSubmit(LoginSubmit event, Emitter<LoginStates> emit) async {
    print('Standard login with nickname');

    if (state is LoginLoading) return;
    emit(LoginLoading());

    try {
      var formData = FormData.fromMap({
        'nickname': event.username
      });
      print('FormData created');
      print(GetIt.I<Dio>().options.baseUrl);
      var response = await GetIt.I<Dio>().post(
        '/standard_token',
        data: formData
      );
      var token = response.data['access_token'];
      GetIt.I<Dio>().options.headers["Authorization"] = "Bearer $token";

      print('Dio success');

      emit(LoginSuccess());
      emit(LoginInitial());

    } on DioException catch (e) {
      if (e.response != null) {
        print(e.response?.data.toString());
        emit(LoginFail(e.response?.data['detail']));
      }
      else {
        print('message: ${e.message}');
        print('error: ${e.error}');
        print('tpye: ${e.type}');
        print('trace: ${e.stackTrace}');
        emit(LoginFail("Something went wrong"));
      }
      emit(LoginInitial());
    }
  }

  void onLoginAdminSubmit(LoginAdminSubmit event, Emitter<LoginStates> emit) async {
    if (state is LoginLoading) return;
    emit(LoginLoading());

    try {
      var formData = FormData.fromMap({
        'username': event.username,
        'password': event.password
      });
      var response = await GetIt.I<Dio>().post(
        '/admin_token',
        data: formData
      );
      var token = response.data['access_token'] as String;
      GetIt.I<Dio>().options.headers["Authorization"] = "Bearer $token";

      emit(LoginAdminSuccess());
      emit(LoginInitial());

    } on DioException catch (e) {
      if (e.response != null) {
        emit(LoginFail(e.response?.data['detail']));
      }
      else {
        emit(LoginFail("Something went wrong"));
      }
      emit(LoginInitial());
    }
  }
}
