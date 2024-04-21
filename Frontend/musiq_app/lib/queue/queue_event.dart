
import 'package:file_picker/file_picker.dart';

class QueueEvents {}

class QueueAdd extends QueueEvents {
  final PlatformFile audioFile;

  QueueAdd(this.audioFile);
}

class QueueUpdate extends QueueEvents {}

class QueueLogout extends QueueEvents {}