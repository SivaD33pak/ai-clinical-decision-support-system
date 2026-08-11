import 'package:ai_clinical_cdss_app/app/app.dart';
import 'package:ai_clinical_cdss_app/features/authentication/view/login_view.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('App', () {
    testWidgets('renders LoginView initially', (tester) async {
      await tester.pumpWidget(const App());
      expect(find.byType(LoginView), findsOneWidget);
    });
  });
}
