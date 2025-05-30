import Combine

class TermCancellableStorage: ObservableObject {
    var cancellables = Set<AnyCancellable>()
} 