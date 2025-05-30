import SwiftUI
import Combine

class NavigationController: ObservableObject {
    @Published var selectedTermId: String? = nil
    @Published var showGraph: Bool = false
    
    // Метод для навигации к термину
    func navigateToTerm(id: String) {
        // Устанавливаем выбранный ID термина
        selectedTermId = id
        
        // Переключаемся на детальный просмотр
        showGraph = false
        
        // Уведомляем о навигации
        NotificationCenter.default.post(name: Notification.Name("navigateToTermNotification"), object: id)
    }
} 