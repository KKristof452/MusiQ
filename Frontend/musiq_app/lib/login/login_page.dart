import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:musiq_app/login/login_bloc.dart';
import 'package:musiq_app/login/login_event.dart';
import 'package:musiq_app/login/login_state.dart';

class LoginPageBloc extends StatefulWidget {
  const LoginPageBloc({super.key});

  @override
  State<LoginPageBloc> createState() => _LoginPageBlocState();
}

class _LoginPageBlocState extends State<LoginPageBloc> {

  @override
  void initState() {
    super.initState();
  }

  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  bool _userValid = true;
  bool _passValid = true;
  bool isAdminLogin = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('MusiQ'),),
      body: BlocConsumer<LoginBloc, LoginStates>(
        builder: (context, state) {
          return Container(
            padding: const EdgeInsets.all(30.0),
            child: Column(
              children: [
                TextFormField(
                  decoration: InputDecoration(
                    labelText: isAdminLogin ? 'Username' : 'Nickname',
                    prefixIcon: const Icon(Icons.account_circle),
                    border: const OutlineInputBorder(),
                    errorText: _userValid ? null : '${isAdminLogin ? 'Username' : 'Nickname'} is too short!'
                  ),
                  controller: usernameController,
                  enabled: state is LoginLoading ? false : true,
                  onChanged: (value) {
                    setState(() => _userValid = true);
                  },
                ),
                if (isAdminLogin) Padding(
                  padding: const EdgeInsets.fromLTRB(0, 10, 0, 0),
                  child: TextFormField(
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.password),
                      border: const OutlineInputBorder(),
                      errorText: _passValid ? null : 'Invalid password',
                    ),
                    controller: passwordController,
                    obscureText: true,
                    enabled: state is LoginLoading ? false : true,
                    onChanged: (value) {
                      setState(() => _passValid = true);
                    },
                  ),
                ),
                CheckboxListTile(
                  title: const Text('Admin login'),
                  controlAffinity: ListTileControlAffinity.platform,
                  value: isAdminLogin,
                  enabled: state is LoginLoading ? false : true,
                  onChanged: (bool? value) {
                    setState(() => isAdminLogin = value ?? false);
                  },
                ),
                SizedBox(
                  height: 30,
                  child: ElevatedButton(
                    onPressed: state is! LoginLoading ? () {
                      setState(() {
                        _userValid = usernameController.text.length >= 4 ? true : false;
                        _passValid = passwordController.text.length >= 4 ? true : false;
                      });
                      if (_userValid) {
                        if (isAdminLogin & _passValid) {
                          context.read<LoginBloc>().add(LoginAdminSubmit(usernameController.text, passwordController.text));
                        }
                        else {
                          context.read<LoginBloc>().add(LoginSubmit(usernameController.text));
                        }
                      }
                    } : null,
                    child: const Text('Login'),
                  ),
                )
              ],
            ),
          );
        },
        listener: (context, state) {
          if (state is LoginSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Login success'))
            );
            Navigator.pushReplacementNamed(context, '/queue');
          }
          else if (state is LoginAdminSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Admin login success'))
            );
            Navigator.pushReplacementNamed(context, '/admin');
          }
          else if (state is LoginFail) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message))
            );
          }
        },
      ),
    );
  }
}