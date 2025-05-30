import SwiftUI
import Combine

struct AddTermForm: View {
    @Binding var isPresented: Bool
    @State private var name: String = ""
    @State private var definition: String = ""
    @State private var tags: String = ""
    @State private var selectedDocumentId: String?
    @State private var isSubmitting: Bool = false
    @State private var errorMessage: String?
    @State private var documents: [Document] = []
    @State private var isLoadingDocuments: Bool = false
    
    @StateObject private var subscriptions = TermCancellableStorage()
    
    private let termService = TermService.shared
    private let documentService = DocumentService.shared
    
    var body: some View {
        NavigationView {
            VStack {
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
                    }
                    
                    Section(header: Text("Документ-источник")) {
                        if isLoadingDocuments {
                            HStack {
                                Spacer()
                                ProgressView()
                                Spacer()
                            }
                        } else {
                            Picker("Выберите документ", selection: $selectedDocumentId) {
                                Text("Нет документа").tag(String?.none)
                                ForEach(documents) { document in
                                    Text(document.title).tag(document.id as String?)
                                }
                            }
                            .pickerStyle(.menu)
                        }
                    }
                    
                    if let errorMessage = errorMessage {
                        Section {
                            Text(errorMessage)
                                .foregroundColor(.red)
                                .font(.system(size: 14))
                        }
                    }
                    
                    Section {
                        Button(action: submitTerm) {
                            if isSubmitting {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle())
                            } else {
                                Text("Добавить термин")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .disabled(isSubmitting || name.isEmpty || definition.isEmpty)
                    }
                }
            }
            .navigationTitle("Добавить термин")
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
            .onAppear {
                loadDocuments()
            }
        }
    }
    
    private func loadDocuments() {
        isLoadingDocuments = true
        
        documentService.getDocuments(limit: 100)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoadingDocuments = false
                    if case .failure = completion {
                        errorMessage = "Не удалось загрузить документы"
                    }
                },
                receiveValue: { documents in
                    self.documents = documents
                }
            )
            .store(in: &subscriptions.cancellables)
    }
    
    private func submitTerm() {
        guard !name.isEmpty && !definition.isEmpty else { return }
        
        isSubmitting = true
        errorMessage = nil
        
        let tagArray = tags.isEmpty ? [] : tags.split(separator: ",").map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
        
        let newTerm = TermCreate(
            name: name,
            definition: definition,
            sourceDocumentId: selectedDocumentId,
            tags: tagArray
        )
        
        termService.createTerm(term: newTerm)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isSubmitting = false
                    if case let .failure(error) = completion {
                        errorMessage = "Ошибка при создании термина: \(error.localizedDescription)"
                    }
                },
                receiveValue: { _ in
                    isPresented = false
                }
            )
            .store(in: &subscriptions.cancellables)
    }
} 