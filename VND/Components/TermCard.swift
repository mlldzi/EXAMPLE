import SwiftUI

struct TermCard: View {
    let term: Term
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(term.name)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(Color.gray700)
                
                Spacer()
                
                if term.isApproved {
                    Image(systemName: "checkmark.seal.fill")
                        .foregroundColor(Color.teal)
                        .font(.system(size: 16))
                }
            }
            
            Text(term.currentDefinition)
                .font(.system(size: 14))
                .foregroundColor(Color.gray600)
                .lineLimit(3)
                .multilineTextAlignment(.leading)
            
            Spacer()
            
            if !term.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 6) {
                        ForEach(term.tags, id: \.self) { tag in
                            Text(tag)
                                .font(.system(size: 11, weight: .medium))
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.accentLight)
                                .foregroundColor(Color.accent)
                                .cornerRadius(12)
                        }
                    }
                }
            }
            
            HStack {
                Spacer()
                Text("Подробнее")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(Color.accent)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(16)
        .shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 4)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color.gray300, lineWidth: 1)
        )
    }
} 