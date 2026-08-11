import 'package:ai_clinical_cdss_app/core/api/api_client.dart';
import 'package:ai_clinical_cdss_app/core/constants/app_theme.dart';
import 'package:ai_clinical_cdss_app/features/authentication/bloc/auth_bloc.dart';
import 'package:ai_clinical_cdss_app/features/authentication/repository/auth_repository.dart';
import 'package:ai_clinical_cdss_app/features/authentication/view/login_view.dart';
import 'package:ai_clinical_cdss_app/features/dashboard/view/dashboard_view.dart';
import 'package:ai_clinical_cdss_app/features/history/bloc/history_bloc.dart';
import 'package:ai_clinical_cdss_app/features/history/repository/history_repository.dart';
import 'package:ai_clinical_cdss_app/features/history/view/history_view.dart';
import 'package:ai_clinical_cdss_app/features/prediction/bloc/prediction_bloc.dart';
import 'package:ai_clinical_cdss_app/features/prediction/repository/prediction_repository.dart';
import 'package:ai_clinical_cdss_app/features/prediction/view/prediction_view.dart';
import 'package:ai_clinical_cdss_app/features/profile/view/profile_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    final apiClient = ApiClient();
    final authRepo = AuthRepository(apiClient: apiClient);
    final predictionRepo = PredictionRepository(apiClient: apiClient);
    final historyRepo = HistoryRepository(apiClient: apiClient);

    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider.value(value: apiClient),
        RepositoryProvider.value(value: authRepo),
        RepositoryProvider.value(value: predictionRepo),
        RepositoryProvider.value(value: historyRepo),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider(create: (_) => AuthBloc(authRepository: authRepo)),
          BlocProvider(create: (_) => PredictionBloc(predictionRepository: predictionRepo)),
          BlocProvider(create: (_) => HistoryBloc(historyRepository: historyRepo)),
        ],
        child: MaterialApp(
          title: 'AI Clinical CDSS',
          theme: AppTheme.lightTheme,
          debugShowCheckedModeBanner: false,
          home: const AppRootView(),
        ),
      ),
    );
  }
}

class AppRootView extends StatelessWidget {
  const AppRootView({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is Authenticated) {
          return const HomeShell();
        }
        return const LoginView();
      },
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final apiClient = context.read<ApiClient>();

    final pages = [
      DashboardView(
        onNavigateToPrediction: () => setState(() => _currentIndex = 1),
        onNavigateToHistory: () => setState(() => _currentIndex = 2),
      ),
      const PredictionView(),
      const HistoryView(),
      ProfileView(apiClient: apiClient),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.document_scanner_outlined), selectedIcon: Icon(Icons.document_scanner), label: 'Scan X-Ray'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: 'History'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
