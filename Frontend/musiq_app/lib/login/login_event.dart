

class LoginEvents {}

class LoginSubmit extends LoginEvents {
  final String username;

  LoginSubmit(this.username);
}

class LoginAdminSubmit extends LoginEvents {
  final String username;
  final String password;

  LoginAdminSubmit(this.username, this.password);
}