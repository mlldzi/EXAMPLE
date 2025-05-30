import SwiftUI

struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.vertical, 12)
            .padding(.horizontal, 20)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [Color.accent, Color.accentHover]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .foregroundColor(.white)
            .font(.system(size: 16, weight: .semibold))
            .cornerRadius(12)
            .shadow(color: Color.accent.opacity(0.4), radius: 5, x: 0, y: 3)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

struct SecondaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.vertical, 12)
            .padding(.horizontal, 20)
            .background(Color.bgPrimary)
            .foregroundColor(Color.gray600)
            .font(.system(size: 16, weight: .medium))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.gray300, lineWidth: 1)
            )
            .shadow(color: Color.black.opacity(0.05), radius: 3, x: 0, y: 1)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

struct AdminButtonStyle: ButtonStyle {
    var isActive: Bool
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .padding(.vertical, 8)
            .padding(.horizontal, 16)
            .background(isActive ? Color.teal.opacity(0.15) : Color.bgPrimary)
            .foregroundColor(isActive ? Color.teal : Color.gray600)
            .font(.system(size: 14, weight: .medium))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(isActive ? Color.teal.opacity(0.3) : Color.gray300, lineWidth: 1)
            )
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

struct AddButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 24))
            .foregroundColor(.white)
            .frame(width: 60, height: 60)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [Color.accent, Color.accentHover]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .clipShape(Circle())
            .shadow(color: Color.accent.opacity(0.4), radius: 10, x: 0, y: 4)
            .scaleEffect(configuration.isPressed ? 0.95 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

struct ApproveButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 24))
            .foregroundColor(.white)
            .frame(width: 60, height: 60)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [Color.teal, Color.teal.opacity(0.8)]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .clipShape(Circle())
            .shadow(color: Color.teal.opacity(0.4), radius: 10, x: 0, y: 4)
            .scaleEffect(configuration.isPressed ? 0.95 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(.easeInOut(duration: 0.2), value: configuration.isPressed)
    }
}

extension ButtonStyle where Self == PrimaryButtonStyle {
    static var primary: PrimaryButtonStyle {
        PrimaryButtonStyle()
    }
}

extension ButtonStyle where Self == SecondaryButtonStyle {
    static var secondary: SecondaryButtonStyle {
        SecondaryButtonStyle()
    }
}

extension ButtonStyle where Self == AdminButtonStyle {
    static func admin(isActive: Bool) -> AdminButtonStyle {
        AdminButtonStyle(isActive: isActive)
    }
}

extension ButtonStyle where Self == AddButtonStyle {
    static var add: AddButtonStyle {
        AddButtonStyle()
    }
}

extension ButtonStyle where Self == ApproveButtonStyle {
    static var approve: ApproveButtonStyle {
        ApproveButtonStyle()
    }
} 