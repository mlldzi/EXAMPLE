import SwiftUI

struct iPadSearchBar: View {
    @Binding var text: String
    var onSubmit: () -> Void
    
    @State private var isEditing = false
    
    var body: some View {
        HStack {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.gray500)
                    .padding(.leading, 8)
                
                TextField("Поиск терминов...", text: $text, onCommit: onSubmit)
                    .padding(.vertical, 10)
                    .background(Color.clear)
                    .disableAutocorrection(true)
                    .onTapGesture {
                        isEditing = true
                    }
                
                if !text.isEmpty {
                    Button(action: {
                        text = ""
                        onSubmit()
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.gray500)
                            .padding(.trailing, 8)
                    }
                }
            }
            .padding(2)
            .background(Color.white)
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.gray300, lineWidth: 1)
            )
            .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
            
            if isEditing {
                Button("Отмена") {
                    text = ""
                    isEditing = false
                    onSubmit()
                    
                    // Скрываем клавиатуру
                    UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
                }
                .padding(.leading, 8)
                .transition(.move(edge: .trailing))
                .animation(.default, value: isEditing)
            }
        }
    }
} 