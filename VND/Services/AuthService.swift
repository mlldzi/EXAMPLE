import Foundation
import Combine

class AuthService: ObservableObject {
    static let shared = AuthService()
    
    private let apiClient = APIClient.shared
    private var cancellables = Set<AnyCancellable>()
    
    @Published var currentUser: User?
    @Published var isLoggedIn = false
    @Published var isDebugAdminMode = false
    
    private init() {
        // Проверка наличия сохраненных токенов при запуске
        loadTokensFromStorage()
        
        // Установка ссылки на сервис аутентификации для отладочных целей
        #if DEBUG
        apiClient.setAuthServiceForDebug(self)
        #endif
        
        // Если токены есть, пытаемся получить данные пользователя
        if apiClient.isAuthenticated {
            // Используем асинхронную загрузку для предотвращения цикла инициализации
            DispatchQueue.main.async {
                self.fetchCurrentUser()
                    .sink(
                        receiveCompletion: { _ in },
                        receiveValue: { _ in }
                    )
                    .store(in: &self.cancellables)
            }
        }
    }
    
    // Публичный метод для загрузки сохраненного пользователя
    public func loadStoredUser() {
        loadTokensFromStorage()
        
        if apiClient.isAuthenticated {
            fetchCurrentUser()
                .sink(
                    receiveCompletion: { _ in },
                    receiveValue: { _ in }
                )
                .store(in: &self.cancellables)
        }
    }
    
    private func loadTokensFromStorage() {
        if let accessToken = UserDefaults.standard.string(forKey: "accessToken"),
           let refreshToken = UserDefaults.standard.string(forKey: "refreshToken"),
           let expiresAt = UserDefaults.standard.object(forKey: "expiresAt") as? Date {
            
            let expiresIn = expiresAt.timeIntervalSince(Date())
            if expiresIn > 0 {
                apiClient.setTokens(accessToken: accessToken, refreshToken: refreshToken, expiresIn: expiresIn)
            } else {
                // Если токен истек, попробуем обновить его
                refreshAccessToken(with: refreshToken)
            }
        }
    }
    
    private func saveTokensToStorage(accessToken: String, refreshToken: String, expiresIn: Double) {
        UserDefaults.standard.set(accessToken, forKey: "accessToken")
        UserDefaults.standard.set(refreshToken, forKey: "refreshToken")
        UserDefaults.standard.set(Date().addingTimeInterval(expiresIn), forKey: "expiresAt")
    }
    
    func login(email: String, password: String) -> AnyPublisher<User, APIError> {
        let loginRequest = UserLoginRequest(email: email, password: password)
        
        return apiClient.requestWithBody("/auth/login", body: loginRequest, requireAuth: false)
            .receive(on: DispatchQueue.main)
            .flatMap { (tokenResponse: TokenResponse) -> AnyPublisher<User, APIError> in
                // Сохраняем токены
                self.apiClient.setTokens(
                    accessToken: tokenResponse.accessToken,
                    refreshToken: tokenResponse.refreshToken,
                    expiresIn: tokenResponse.expiresIn
                )
                
                // Сохраняем токены в хранилище
                self.saveTokensToStorage(
                    accessToken: tokenResponse.accessToken,
                    refreshToken: tokenResponse.refreshToken,
                    expiresIn: tokenResponse.expiresIn
                )
                
                // Получаем информацию о пользователе
                return self.fetchCurrentUser()
            }
            .eraseToAnyPublisher()
    }
    
    func logout() {
        DispatchQueue.main.async {
            self.apiClient.clearTokens()
            
            // Удаляем токены из хранилища
            UserDefaults.standard.removeObject(forKey: "accessToken")
            UserDefaults.standard.removeObject(forKey: "refreshToken")
            UserDefaults.standard.removeObject(forKey: "expiresAt")
            
            // Обновляем состояние
            self.currentUser = nil
            self.isLoggedIn = false
            self.isDebugAdminMode = false
        }
    }
    
    func fetchCurrentUser() -> AnyPublisher<User, APIError> {
        return apiClient.request("/users/me")
            .receive(on: DispatchQueue.main)
            .handleEvents(receiveOutput: { [weak self] user in
                self?.currentUser = user
                self?.isLoggedIn = true
            })
            .eraseToAnyPublisher()
    }
    
    func refreshAccessToken(with refreshToken: String) {
        let refreshRequest = RefreshTokenRequest(refreshToken: refreshToken)
        
        apiClient.requestWithBody("/auth/refresh", body: refreshRequest, requireAuth: false)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure = completion {
                        // Если не удалось обновить токен, выходим из системы
                        self?.logout()
                    }
                },
                receiveValue: { [weak self] (tokenResponse: TokenResponse) in
                    // Обновляем токены
                    self?.apiClient.setTokens(
                        accessToken: tokenResponse.accessToken,
                        refreshToken: tokenResponse.refreshToken,
                        expiresIn: tokenResponse.expiresIn
                    )
                    
                    // Сохраняем обновленные токены
                    self?.saveTokensToStorage(
                        accessToken: tokenResponse.accessToken,
                        refreshToken: tokenResponse.refreshToken,
                        expiresIn: tokenResponse.expiresIn
                    )
                    
                    // Обновляем данные пользователя
                    self?.fetchCurrentUser()
                        .sink(receiveCompletion: { _ in }, receiveValue: { _ in })
                        .store(in: &self!.cancellables)
                }
            )
            .store(in: &cancellables)
    }
    
    func toggleDebugAdminMode() {
        DispatchQueue.main.async {
            self.isDebugAdminMode.toggle()
            print("Debug Admin Mode: \(self.isDebugAdminMode)")
            
            // Если пользователь аутентифицирован, обновим его информацию
            if self.isLoggedIn {
                self.fetchCurrentUser()
                    .sink(
                        receiveCompletion: { _ in },
                        receiveValue: { user in
                            print("Обновлена информация о пользователе: \(user.email), роли: \(user.roles)")
                        }
                    )
                    .store(in: &self.cancellables)
            }
        }
    }
    
    var isAdmin: Bool {
        guard let user = currentUser else { return false }
        return isDebugAdminMode || user.roles.contains("admin") || user.roles.contains("ADMIN")
    }
} 