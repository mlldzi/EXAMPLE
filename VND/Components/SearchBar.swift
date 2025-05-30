import SwiftUI

struct SearchBar: View {
    @Binding var text: String
    var placeholder: String = "Поиск терминов..."
    var onSubmit: (() -> Void)? = nil
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(Color.gray500)
                .padding(.leading, 12)
            
            TextField(placeholder, text: $text)
                .padding(.vertical, 10)
                .padding(.horizontal, 4)
                .font(.system(size: 16))
                .foregroundColor(Color.gray700)
                .disableAutocorrection(true)
                .onSubmit {
                    onSubmit?()
                }
            
            if !text.isEmpty {
                Button {
                    text = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(Color.gray400)
                }
                .padding(.trailing, 12)
            }
        }
        .background(Color.white)
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color.gray300, lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
} 