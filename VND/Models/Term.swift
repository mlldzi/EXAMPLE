import Foundation

struct Term: Codable, Identifiable {
    let id: String
    let name: String
    let currentDefinition: String
    let isApproved: Bool
    let createdAt: String
    let updatedAt: String?
    let tags: [String]
    let definitionsHistory: [TermDefinition]?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case currentDefinition = "current_definition"
        case isApproved = "is_approved"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
        case tags
        case definitionsHistory = "definitions_history"
    }
}

struct TermDefinition: Codable {
    let definition: String
    let createdAt: String
    let createdBy: String
    let sourceDocumentId: String?
    
    enum CodingKeys: String, CodingKey {
        case definition
        case createdAt = "created_at"
        case createdBy = "created_by"
        case sourceDocumentId = "source_document_id"
    }
}

struct TermCreate: Codable {
    var name: String
    var definition: String
    var sourceDocumentId: String?
    var tags: [String]
    
    enum CodingKeys: String, CodingKey {
        case name
        case definition
        case sourceDocumentId = "source_document_id"
        case tags
    }
}

struct TermUpdate: Codable {
    var name: String?
    var definition: String?
    var isApproved: Bool?
    var tags: [String]?
    
    enum CodingKeys: String, CodingKey {
        case name
        case definition
        case isApproved = "is_approved"
        case tags
    }
} 