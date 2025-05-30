import SwiftUI
import Combine
 
// Вспомогательный класс для хранения отменяемых подписок
class VNDCancellableStorage: ObservableObject {
    var cancellables = Set<AnyCancellable>()
} 