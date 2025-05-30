import Foundation
import Combine

class TermService {
    static let shared = TermService()
    
    private let apiClient = APIClient.shared
    
    func getTerms(skip: Int = 0, limit: Int = 20, query: String? = nil) -> AnyPublisher<[Term], APIError> {
        var params: [String: String] = [
            "skip": String(skip),
            "limit": String(limit)
        ]
        
        if let query = query, !query.isEmpty {
            params["query"] = query
        }
        
        return apiClient.request("/terms/", params: params)
    }
    
    func getTermById(id: String) -> AnyPublisher<Term, APIError> {
        return apiClient.request("/terms/\(id)")
    }
    
    func createTerm(term: TermCreate) -> AnyPublisher<Term, APIError> {
        return apiClient.requestWithBody("/terms/", body: term)
    }
    
    func updateTerm(id: String, term: TermUpdate) -> AnyPublisher<Term, APIError> {
        return apiClient.requestWithBody("/terms/\(id)", method: "PUT", body: term)
    }
    
    func approveTerm(id: String) -> AnyPublisher<Term, APIError> {
        let approvalUpdate = TermUpdate(isApproved: true)
        return updateTerm(id: id, term: approvalUpdate)
    }
    
    func deleteTerm(id: String) -> AnyPublisher<DeleteResponse, APIError> {
        return apiClient.request("/terms/\(id)", method: "DELETE")
    }
    
    func getDocumentsForTerm(id: String) -> AnyPublisher<[Document], APIError> {
        return apiClient.request("/terms/\(id)/documents")
    }
    
    func getTermsStatistics() -> AnyPublisher<[TermStatistic], APIError> {
        return apiClient.request("/terms/statistics")
    }
}

struct TermStatistic: Codable, Identifiable {
    var id: String { termId }
    let termId: String
    let termName: String
    let documentCount: Int
    
    enum CodingKeys: String, CodingKey {
        case termId = "term_id"
        case termName = "term_name"
        case documentCount = "document_count"
    }
}

struct DeleteResponse: Codable {
    let success: Bool
    let message: String?
} 