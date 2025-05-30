import Foundation
import Combine

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int, data: Data?)
    case decodingError(Error)
    case unknown(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Неверный URL запроса"
        case .invalidResponse:
            return "Некорректный ответ сервера"
        case .httpError(let statusCode, _):
            switch statusCode {
            case 400:
                return "Некорректный запрос (400)"
            case 401:
                return "Требуется авторизация (401)"
            case 403:
                return "Доступ запрещен (403)"
            case 404:
                return "Ресурс не найден (404)"
            case 422:
                return "Ошибка валидации данных (422)"
            case 500, 501, 502, 503:
                return "Ошибка сервера (\(statusCode))"
            default:
                return "Ошибка HTTP: \(statusCode)"
            }
        case .decodingError(let error):
            return "Ошибка обработки данных: \(error.localizedDescription)"
        case .unknown(let error):
            return "Неизвестная ошибка: \(error.localizedDescription)"
        }
    }
}

class APIClient {
    static let shared = APIClient()
    
    private let baseURL = "http://localhost:8000/api/v1"
    private var accessToken: String?
    private var refreshToken: String?
    private var expiresAt: Date?
    
    private init() {}
    
    func setTokens(accessToken: String, refreshToken: String, expiresIn: Double) {
        self.accessToken = accessToken
        self.refreshToken = refreshToken
        self.expiresAt = Date().addingTimeInterval(expiresIn)
    }
    
    func clearTokens() {
        accessToken = nil
        refreshToken = nil
        expiresAt = nil
    }
    
    var isAuthenticated: Bool {
        accessToken != nil && refreshToken != nil && expiresAt != nil && expiresAt! > Date()
    }
    
    private func headers(requireAuth: Bool = true) -> [String: String] {
        var headers = [
            "Content-Type": "application/json",
            "Accept": "application/json"
        ]
        
        if requireAuth, let token = accessToken {
            headers["Authorization"] = "Bearer \(token)"
        }
        
        #if DEBUG
        if let authService = _authServiceForDebug, authService.isDebugAdminMode {
            headers["X-Debug-Admin-Mode"] = "true"
        }
        #endif
        
        return headers
    }
    
    func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        params: [String: String]? = nil,
        body: Data? = nil,
        requireAuth: Bool = true
    ) -> AnyPublisher<T, APIError> {
        
        guard var components = URLComponents(string: "\(baseURL)\(endpoint)") else {
            return Fail(error: APIError.invalidURL).eraseToAnyPublisher()
        }
        
        if let params = params {
            components.queryItems = params.map { URLQueryItem(name: $0.key, value: $0.value) }
        }
        
        guard let url = components.url else {
            return Fail(error: APIError.invalidURL).eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.allHTTPHeaderFields = headers(requireAuth: requireAuth)
        request.httpBody = body
        
        #if DEBUG
        print("API Request: \(method) \(url.absoluteString)")
        if let body = body, let bodyString = String(data: body, encoding: .utf8) {
            print("Request Body: \(bodyString)")
        }
        #endif
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.invalidResponse
                }
                
                #if DEBUG
                print("API Response: \(httpResponse.statusCode)")
                if let responseString = String(data: data, encoding: .utf8) {
                    print("Response Body: \(responseString)")
                }
                #endif
                
                if !(200...299).contains(httpResponse.statusCode) {
                    // Попытка распознать структуру ошибки
                    if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                        print("Structured error response: \(errorResponse.displayMessage)")
                    }
                    
                    throw APIError.httpError(statusCode: httpResponse.statusCode, data: data)
                }
                
                return data
            }
            .decode(type: T.self, decoder: JSONDecoder())
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                } else if let decodingError = error as? DecodingError {
                    print("Decoding error: \(decodingError)")
                    return APIError.decodingError(decodingError)
                } else {
                    print("Unknown error: \(error)")
                    return APIError.unknown(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    func requestWithBody<T: Decodable, E: Encodable>(
        _ endpoint: String,
        method: String = "POST",
        body: E,
        requireAuth: Bool = true
    ) -> AnyPublisher<T, APIError> {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(body)
            return request(endpoint, method: method, body: data, requireAuth: requireAuth)
        } catch {
            print("Encoding error: \(error)")
            return Fail(error: APIError.unknown(error)).eraseToAnyPublisher()
        }
    }
    
    #if DEBUG
    private var _authServiceForDebug: AuthService? = nil
    func setAuthServiceForDebug(_ service: AuthService) {
        _authServiceForDebug = service
    }
    #endif
} 