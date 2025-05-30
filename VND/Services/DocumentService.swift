import Foundation
import Combine

class DocumentService {
    static let shared = DocumentService()
    
    private let apiClient = APIClient.shared
    
    func getDocuments(skip: Int = 0, limit: Int = 20, query: String? = nil) -> AnyPublisher<[Document], APIError> {
        var params: [String: String] = [
            "skip": String(skip),
            "limit": String(limit)
        ]
        
        if let query = query, !query.isEmpty {
            params["query"] = query
        }
        
        return apiClient.request("/documents/", params: params)
    }
    
    func getDocumentById(id: String) -> AnyPublisher<Document, APIError> {
        return apiClient.request("/documents/\(id)")
    }
    
    func getTermsForDocument(id: String) -> AnyPublisher<[Term], APIError> {
        return apiClient.request("/documents/\(id)/terms")
    }
} 