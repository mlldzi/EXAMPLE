import SwiftUI
import Combine

class TabViewModel: ObservableObject {
    @Published var selectedTab: Int = 0
    
    enum Tab: Int, CaseIterable {
        case terms = 0
        case documents = 1
        case profile = 2
        
        var icon: String {
            switch self {
            case .terms:
                return "doc.text.magnifyingglass"
            case .documents:
                return "folder"
            case .profile:
                return "person"
            }
        }
        
        var selectedIcon: String {
            switch self {
            case .terms:
                return "doc.text.magnifyingglass"
            case .documents:
                return "folder.fill"
            case .profile:
                return "person.fill"
            }
        }
        
        var title: String {
            switch self {
            case .terms:
                return "Термины"
            case .documents:
                return "Документы"
            case .profile:
                return "Профиль"
            }
        }
    }
} 