import SwiftUI

struct iPadEmptyStateView: View {
    let title: String
    let message: String
    let iconName: String
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: iconName)
                .font(.system(size: 60))
                .foregroundColor(Color.gray400)
            
            Text(title)
                .font(.title2)
                .fontWeight(.medium)
                .foregroundColor(Color.gray700)
            
            Text(message)
                .font(.body)
                .foregroundColor(Color.gray600)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.bgPrimary)
    }
} 