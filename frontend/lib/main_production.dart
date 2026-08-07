import 'package:ai_clinical_cdss_app/app/app.dart';
import 'package:ai_clinical_cdss_app/bootstrap.dart';

Future<void> main() async {
  await bootstrap(() => const App());
}
