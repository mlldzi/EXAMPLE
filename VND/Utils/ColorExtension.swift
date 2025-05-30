import SwiftUI

extension Color {
    static let bgPrimary = Color(hex: "F8F9FC")
    static let bgSecondary = Color(hex: "EEF1F8")
    static let accent = Color(hex: "4E6AF1")
    static let accentHover = Color(hex: "3A56DE")
    static let accentLight = Color(hex: "E9EDFF")
    static let coral = Color(hex: "FF7D50")
    static let teal = Color(hex: "2DD4BF")
    static let gray100 = Color(hex: "F0F3F9")
    static let gray200 = Color(hex: "E4E9F5")
    static let gray300 = Color(hex: "D5DCED")
    static let gray400 = Color(hex: "ACB8D1")
    static let gray500 = Color(hex: "6B7A99")
    static let gray600 = Color(hex: "4A5568")
    static let gray700 = Color(hex: "2D3748")
    static let textColor = Color(hex: "2D3748")
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
} 