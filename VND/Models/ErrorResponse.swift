import Foundation

struct ErrorResponse: Codable {
    let detail: String?
    let message: String?
    let errors: [FieldError]?
    
    struct FieldError: Codable {
        let field: String
        let message: String
    }
    
    var displayMessage: String {
        if let detail = detail {
            return detail
        }
        
        if let message = message {
            return message
        }
        
        if let errors = errors, !errors.isEmpty {
            return errors.map { "\($0.field): \($0.message)" }.joined(separator: "\n")
        }
        
        return "Неизвестная ошибка сервера"
    }
} 