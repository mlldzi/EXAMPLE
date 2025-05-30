import Foundation

struct Document: Codable, Identifiable {
    let id: String
    let title: String
    let documentNumber: String?
    let description: String?
    let approvalDate: String?
    let status: String?
    let department: String?
    let documentUrl: String?
    let tags: [String]
    let createdAt: String?
    let updatedAt: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case title
        case documentNumber = "document_number"
        case description
        case approvalDate = "approval_date"
        case status
        case department
        case documentUrl = "document_url"
        case tags
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
} 