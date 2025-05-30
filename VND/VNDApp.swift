import SwiftUI
import Combine

@main
struct VNDApp: App {
    // Инициализируем сервисы на уровне приложения
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            MainView()
                .environmentObject(appState)
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