import SwiftUI
import Combine

@main
struct VNDApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(AuthService.shared)
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var authService: AuthService
    
    var body: some View {
        Group {
            if UIDevice.current.userInterfaceIdiom == .pad {
                // iPad интерфейс
                DeviceTypeAwareView(isIPad: true)
            } else {
                // iPhone интерфейс
                DeviceTypeAwareView(isIPad: false)
            }
        }
    }
}

struct DeviceTypeAwareView: View {
    let isIPad: Bool
    @State private var selectedTab = 0
    @EnvironmentObject var authService: AuthService
    
    var body: some View {
        Group {
            if isIPad {
                // iPad-версия
                SplitViewContainer()
            } else {
                // iPhone-версия
                TabView(selection: $selectedTab) {
                    NavigationView {
                        TermsListView()
                    }
                    .navigationViewStyle(StackNavigationViewStyle())
                    .tabItem {
                        Label("Глоссарий", systemImage: "book")
                    }
                    .tag(0)
                    
                    NavigationView {
                        DocumentsListView()
                    }
                    .navigationViewStyle(StackNavigationViewStyle())
                    .tabItem {
                        Label("Документы", systemImage: "doc.text")
                    }
                    .tag(1)
                    
                    NavigationView {
                        ProfileView()
                    }
                    .navigationViewStyle(StackNavigationViewStyle())
                    .tabItem {
                        Label("Профиль", systemImage: "person")
                    }
                    .tag(2)
                }
            }
        }
        .onAppear {
            // Для отладки: автоматически авторизуем пользователя
            if !authService.isLoggedIn {
                authService.loadStoredUser()
            }
        }
    }
}

// Класс для безопасной инициализации сервисов
class AppState: ObservableObject {
    private let authService: AuthService
    
    init() {
        // Инициализируем сервисы в контролируемом порядке
        print("Инициализация AppState")
        
        // Инициализируем AuthService после создания всех зависимостей
        authService = AuthService.shared
    }
} 