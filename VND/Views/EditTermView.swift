import SwiftUI
import Combine

struct EditTermView: View {
    let term: Term
    @Binding var isPresented: Bool
    var onTermUpdated: ((Term) -> Void)?
    
    @State private var name: String
    @State private var definition: String
    @State private var tags: String
    @State private var isApproved: Bool
    @State private var isSubmitting: Bool = false
    @State private var errorMessage: String?
    
    @StateObject private var subscriptions = TermCancellableStorage()
    
    private let termService = TermService.shared
    
    init(term: Term, isPresented: Binding<Bool>, onTermUpdated: ((Term) -> Void)? = nil) {
        self.term = term
        self._isPresented = isPresented
        self.onTermUpdated = onTermUpdated
        
        _name = State(initialValue: term.name)
        _definition = State(initialValue: term.currentDefinition)
        _tags = State(initialValue: term.tags.joined(separator: ", "))
        _isApproved = State(initialValue: term.isApproved)
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.bgPrimary.ignoresSafeArea()
                
                Form {
                    Section(header: Text("Информация о термине")) {
                        TextField("Название термина", text: $name)
                            .padding(.vertical, 8)
                        
                        VStack(alignment: .leading) {
                            Text("Определение")
                                .font(.system(size: 14))
                                .foregroundColor(.gray500)
                                .padding(.top, 6)
                                .padding(.bottom, 2)
                            
                            TextEditor(text: $definition)
                                .frame(minHeight: 100)
                                .padding(4)
                                .background(Color.white)
                                .cornerRadius(8)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.gray300, lineWidth: 1)
                                )
                        }
                        
                        TextField("Теги (через запятую)", text: $tags)
                            .padding(.vertical, 8)
                        
                        Toggle("Утвержден", isOn: $isApproved)
                            .toggleStyle(SwitchToggleStyle(tint: Color.teal))
                    }
                    
                    if let errorMessage = errorMessage {
                        Section {
                            Text(errorMessage)
                                .foregroundColor(.red)
                                .font(.system(size: 14))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    
                    Section {
                        Button(action: submitUpdate) {
                            if isSubmitting {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle())
                            } else {
                                Text("Сохранить изменения")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .disabled(isSubmitting || name.isEmpty || definition.isEmpty)
                    }
                }
            }
            .navigationTitle("Редактирование")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button {
                        isPresented = false
                    } label: {
                        Text("Отмена")
                    }
                }
            }
        }
        .alert(isPresented: .constant(errorMessage != nil), content: {
            Alert(
                title: Text("Ошибка"),
                message: Text(errorMessage ?? "Неизвестная ошибка"),
                dismissButton: .default(Text("OK"))
            )
        })
    }
    
    private func submitUpdate() {
        guard !name.isEmpty && !definition.isEmpty else { return }
        
        isSubmitting = true
        errorMessage = nil
        
        let tagArray = tags.isEmpty ? [] : tags.split(separator: ",").map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
        
        let termUpdate = TermUpdate(
            name: name,
            definition: definition,
            isApproved: isApproved,
            tags: tagArray
        )
        
        print("Отправка запроса на обновление термина ID: \(term.id)")
        print("Данные для обновления: \(termUpdate)")
        
        termService.updateTerm(id: term.id, term: termUpdate)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isSubmitting = false
                    if case let .failure(error) = completion {
                        print("Ошибка обновления термина: \(error)")
                        
                        switch error {
                        case .httpError(let statusCode, let data):
                            var message = "Ошибка сервера (\(statusCode))"
                            
                            if let data = data {
                                // Попытка распознать структурированную ошибку
                                if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                                    message = errorResponse.displayMessage
                                } else if let errorStr = String(data: data, encoding: .utf8) {
                                    message += ": \(errorStr)"
                                }
                            }
                            
                            errorMessage = message
                        default:
                            errorMessage = error.localizedDescription
                        }
                    }
                },
                receiveValue: { updatedTerm in
                    print("Термин успешно обновлен: \(updatedTerm.id)")
                    onTermUpdated?(updatedTerm)
                    isPresented = false
                }
            )
            .store(in: &subscriptions.cancellables)
    }
}