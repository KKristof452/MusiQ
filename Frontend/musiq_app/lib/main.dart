import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:musiq_app/login/login_bloc.dart';
import 'package:musiq_app/login/login_page.dart';
import 'package:get_it/get_it.dart';
import 'package:musiq_app/queue/admin_queue_page.dart';
import 'package:musiq_app/queue/queue_bloc.dart';
import 'package:musiq_app/queue/queue_page.dart';

void main() {
  print('Main started');
  configureDependecies();
  runApp(const MyApp());
}


Future configureDependecies() async {
  var dio = Dio();
  dio.options.baseUrl = 'http://localhost';
  dio.options.connectTimeout = const Duration(seconds: 15);
  dio.options.receiveTimeout = const Duration(seconds: 13);
  GetIt.I.registerSingleton(dio);
  print('dependency configuration done!!!!!');
}


class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<LoginBloc>(create: (context) => LoginBloc()),
        BlocProvider<QueueBloc>(create: (context) => QueueBloc()),
      ],
      child: MaterialApp (
        title: "MusiQ",
        theme: ThemeData(
          primarySwatch: Colors.blueGrey,
        ),
        home: const LoginPageBloc(),
        routes: {
          "/queue": (context) => const QueuePageBloc(),
          "/admin": (context) => const AdminQueuePageBloc(),
        },
      ),
    );
  }
}


