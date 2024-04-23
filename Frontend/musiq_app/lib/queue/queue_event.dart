

import 'package:file_picker/file_picker.dart';

class QueueEvents {}

class QueueAdd extends QueueEvents {
  final PlatformFile audioFile;

  QueueAdd(this.audioFile);
}

class QueueUpdate extends QueueEvents {}

class QueueLogout extends QueueEvents {}

class QueueRemoveItem extends QueueEvents {
  final String itemId;

  QueueRemoveItem(this.itemId);
}

class QueueReorder extends QueueEvents {
  final String id;
  final int oldIndex;
  final int newIndex;

  QueueReorder(this.id, this.oldIndex, this.newIndex);
}
