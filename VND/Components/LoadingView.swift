import SwiftUI

struct LoadingView: View {
    var body: some View {
        VStack {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: Color.accent))
                .scaleEffect(1.5)
                .padding()
            
            Text("Загрузка...")
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(Color.gray600)
                .padding(.top, 8)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.bgPrimary)
    }
}

struct ErrorView: View {
    let message: String
    var retryAction: (() -> Void)?
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.circle")
                .font(.system(size: 50))
                .foregroundColor(Color.coral)
                .padding()
            
            Text("Ошибка")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(Color.gray700)
            
            Text(message)
                .font(.system(size: 16))
                .foregroundColor(Color.gray600)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            
            if let retryAction = retryAction {
                Button(action: retryAction) {
                    Text("Повторить")
                        .padding(.vertical, 12)
                        .padding(.horizontal, 24)
                }
                .buttonStyle(.primary)
                .padding(.top, 16)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.bgPrimary)
    }
}

struct CommonEmptyStateView: View {
    let title: String
    let message: String
    let iconName: String
    var action: (() -> Void)?
    var actionTitle: String = "Действие"
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: iconName)
                .font(.system(size: 50))
                .foregroundColor(Color.gray400)
                .padding()
            
            Text(title)
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(Color.gray700)
            
            Text(message)
                .font(.system(size: 16))
                .foregroundColor(Color.gray600)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            
            if let action = action {
                Button(action: action) {
                    Text(actionTitle)
                        .padding(.vertical, 12)
                        .padding(.horizontal, 24)
                }
                .buttonStyle(.primary)
                .padding(.top, 16)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.bgPrimary)
    }
} 