import SwiftUI
import Combine

struct TermDetailView: View {
    let termId: String
    
    @ObservedObject private var authService = AuthService.shared
    @Environment(\.presentationMode) var presentationMode
    
    @State private var term: Term?
    @State private var relatedDocuments: [Document] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var isShowingEditForm: Bool = false
    @State private var selectedTab: Int = 0
    
    @StateObject private var subscriptions = TermCancellableStorage()
    
    private let termService = TermService.shared
    
    var body: some View {
        ZStack {
            Color.bgPrimary.ignoresSafeArea()
            
            if isLoading && term == nil {
                LoadingView()
            } else if let errorMessage = errorMessage {
                ErrorView(message: errorMessage, retryAction: loadTermData)
            } else if let term = term {
                TermDetailContent(
                    term: term,
                    relatedDocuments: relatedDocuments,
                    selectedTab: $selectedTab,
                    isShowingEditForm: $isShowingEditForm,
                    authService: authService,
                    onApprove: approveCurrentTerm
                )
            }
        }
        .navigationBarTitle("", displayMode: .inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                Text("Просмотр термина")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(Color.gray700)
            }
        }
        .onAppear {
            loadTermData()
            print("isAdmin: \(authService.isAdmin), isDebugAdminMode: \(authService.isDebugAdminMode)")
            if let user = authService.currentUser {
                print("User roles: \(user.roles)")
            }
        }
        .sheet(isPresented: $isShowingEditForm) {
            if let term = term {
                EditTermView(
                    term: term,
                    isPresented: $isShowingEditForm,
                    onTermUpdated: { updatedTerm in
                        self.term = updatedTerm
                    }
                )
            }
        }
    }
    
    private func loadTermData() {
        isLoading = true
        errorMessage = nil
        
        // Загружаем данные о термине
        termService.getTermById(id: termId)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    if case let .failure(error) = completion {
                        isLoading = false
                        errorMessage = "Ошибка загрузки термина: \(error.localizedDescription)"
                    }
                },
                receiveValue: { term in
                    self.term = term
                    
                    // Загружаем связанные документы
                    self.loadRelatedDocuments()
                }
            )
            .store(in: &subscriptions.cancellables)
    }
    
    private func loadRelatedDocuments() {
        termService.getDocumentsForTerm(id: termId)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case let .failure(error) = completion {
                        errorMessage = "Ошибка загрузки документов: \(error.localizedDescription)"
                    }
                },
                receiveValue: { documents in
                    self.relatedDocuments = documents
                }
            )
            .store(in: &subscriptions.cancellables)
    }
    
    private func formattedDate(_ dateString: String) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        
        if let date = dateFormatter.date(from: dateString) {
            let outputFormatter = DateFormatter()
            outputFormatter.dateFormat = "dd.MM.yyyy"
            return outputFormatter.string(from: date)
        }
        
        return dateString
    }
    
    private func approveCurrentTerm() {
        guard let term = term else { return }
        
        isLoading = true
        errorMessage = nil
        
        termService.approveTerm(id: term.id)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case let .failure(error) = completion {
                        errorMessage = "Ошибка при утверждении термина: \(error.localizedDescription)"
                        print("Ошибка утверждения: \(error)")
                    }
                },
                receiveValue: { updatedTerm in
                    self.term = updatedTerm
                    // Показываем временное уведомление об успешном утверждении
                    let generator = UINotificationFeedbackGenerator()
                    generator.notificationOccurred(.success)
                    print("Термин успешно утвержден: \(updatedTerm.id)")
                }
            )
            .store(in: &subscriptions.cancellables)
    }
}

// MARK: - Вспомогательные компоненты
struct TermDetailContent: View {
    let term: Term
    let relatedDocuments: [Document]
    @Binding var selectedTab: Int
    @Binding var isShowingEditForm: Bool
    let authService: AuthService
    let onApprove: () -> Void
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Заголовок и статус
                TermHeaderView(term: term)
                
                // Теги
                if !term.tags.isEmpty {
                    TermTagsView(tags: term.tags)
                }
                
                // Табы
                TabSelectionView(
                    selectedTab: $selectedTab,
                    showHistoryTab: authService.isAdmin
                )
                
                // Контент таба
                TermTabContentView(
                    selectedTab: selectedTab,
                    term: term,
                    relatedDocuments: relatedDocuments,
                    authService: authService
                )
            }
            .padding()
        }
        
        // Кнопки редактирования и утверждения для админа
        if authService.isAdmin {
            AdminActionButtonsView(
                term: term,
                isShowingEditForm: $isShowingEditForm,
                onApprove: onApprove
            )
        }
    }
}

struct TermHeaderView: View {
    let term: Term
    
    var body: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 4) {
                Text(term.name)
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(Color.gray700)
                    .fixedSize(horizontal: false, vertical: true)
                
                if let updatedAt = term.updatedAt {
                    Text("Обновлено: \(formattedDate(updatedAt))")
                        .font(.system(size: 12))
                        .foregroundColor(Color.gray500)
                }
            }
            
            Spacer()
            
            if term.isApproved {
                ApprovalStatusView(isApproved: true)
            } else {
                ApprovalStatusView(isApproved: false)
            }
        }
        .padding(.bottom, 4)
    }
    
    private func formattedDate(_ dateString: String) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        
        if let date = dateFormatter.date(from: dateString) {
            let outputFormatter = DateFormatter()
            outputFormatter.dateFormat = "dd.MM.yyyy"
            return outputFormatter.string(from: date)
        }
        
        return dateString
    }
}

struct ApprovalStatusView: View {
    let isApproved: Bool
    
    var body: some View {
        VStack {
            Image(systemName: isApproved ? "checkmark.seal.fill" : "hourglass")
                .foregroundColor(isApproved ? Color.teal : Color.coral)
                .font(.system(size: 20))
            
            Text(isApproved ? "Утвержден" : "На проверке")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(isApproved ? Color.teal : Color.coral)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(isApproved ? Color.teal.opacity(0.1) : Color.coral.opacity(0.1))
        .cornerRadius(8)
    }
}

struct TermTagsView: View {
    let tags: [String]
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(tags, id: \.self) { tag in
                    Text(tag)
                        .font(.system(size: 12, weight: .medium))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color.accentLight)
                        .foregroundColor(Color.accent)
                        .cornerRadius(12)
                }
            }
        }
        .padding(.bottom, 8)
    }
}

struct TabSelectionView: View {
    @Binding var selectedTab: Int
    let showHistoryTab: Bool
    
    var body: some View {
        HStack(spacing: 0) {
            TabButton(title: "Определение", isSelected: selectedTab == 0) {
                selectedTab = 0
            }
            
            TabButton(title: "ВНД", isSelected: selectedTab == 1) {
                selectedTab = 1
            }
            
            if showHistoryTab {
                TabButton(title: "История", isSelected: selectedTab == 2) {
                    selectedTab = 2
                }
            }
        }
        .background(Color.white)
        .cornerRadius(8)
        .padding(.bottom, 4)
    }
}

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 16, weight: isSelected ? .semibold : .medium))
                .foregroundColor(isSelected ? Color.accent : Color.gray500)
                .padding(.vertical, 10)
                .frame(maxWidth: .infinity)
        }
        .background(
            Rectangle()
                .fill(Color.clear)
                .overlay(
                    Rectangle()
                        .fill(isSelected ? Color.accent : Color.clear)
                        .frame(height: 2),
                    alignment: .bottom
                )
        )
    }
}

struct TermTabContentView: View {
    let selectedTab: Int
    let term: Term
    let relatedDocuments: [Document]
    let authService: AuthService
    
    var body: some View {
        VStack(alignment: .leading) {
            if selectedTab == 0 {
                DefinitionTabView(definition: term.currentDefinition)
            } else if selectedTab == 1 {
                DocumentsTabView(documents: relatedDocuments)
            } else if selectedTab == 2 && authService.isAdmin {
                HistoryTabView(history: term.definitionsHistory)
            }
        }
    }
}

struct DefinitionTabView: View {
    let definition: String
    
    var body: some View {
        Text(definition)
            .font(.system(size: 16))
            .foregroundColor(Color.gray700)
            .fixedSize(horizontal: false, vertical: true)
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white)
            .cornerRadius(12)
    }
}

struct DocumentsTabView: View {
    let documents: [Document]
    
    var body: some View {
        if documents.isEmpty {
            VStack(spacing: 8) {
                Image(systemName: "doc.text")
                    .font(.system(size: 40))
                    .foregroundColor(Color.gray400)
                    .padding(.bottom, 8)
                
                Text("Нет связанных документов")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(Color.gray600)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.white)
            .cornerRadius(12)
        } else {
            VStack(spacing: 0) {
                ForEach(documents) { document in
                    DocumentItemView(document: document)
                }
            }
        }
    }
}

struct DocumentItemView: View {
    let document: Document
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(document.title)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(Color.gray700)
            
            if let description = document.description {
                Text(description)
                    .font(.system(size: 14))
                    .foregroundColor(Color.gray600)
                    .lineLimit(3)
            }
            
            HStack {
                if let documentNumber = document.documentNumber {
                    Text("№ \(documentNumber)")
                        .font(.system(size: 12))
                        .foregroundColor(Color.gray500)
                }
                
                Spacer()
                
                if let approvalDate = document.approvalDate {
                    Text("От \(formattedDate(approvalDate))")
                        .font(.system(size: 12))
                        .foregroundColor(Color.gray500)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .padding(.bottom, 8)
    }
    
    private func formattedDate(_ dateString: String) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        
        if let date = dateFormatter.date(from: dateString) {
            let outputFormatter = DateFormatter()
            outputFormatter.dateFormat = "dd.MM.yyyy"
            return outputFormatter.string(from: date)
        }
        
        return dateString
    }
}

struct HistoryTabView: View {
    let history: [TermDefinition]?
    
    var body: some View {
        if let history = history, !history.isEmpty {
            VStack(spacing: 16) {
                ForEach(0..<history.count, id: \.self) { index in
                    HistoryItemView(
                        definition: history[index],
                        versionNumber: history.count - index
                    )
                }
            }
        } else {
            Text("История изменений отсутствует")
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(Color.gray600)
                .frame(maxWidth: .infinity, alignment: .center)
                .padding()
                .background(Color.white)
                .cornerRadius(12)
        }
    }
}

struct HistoryItemView: View {
    let definition: TermDefinition
    let versionNumber: Int
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Версия \(versionNumber)")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(Color.accent)
            
            Text(definition.definition)
                .font(.system(size: 14))
                .foregroundColor(Color.gray700)
                .fixedSize(horizontal: false, vertical: true)
            
            HStack {
                Text("Автор: \(definition.createdBy)")
                    .font(.system(size: 12))
                    .foregroundColor(Color.gray500)
                
                Spacer()
                
                Text(formattedDate(definition.createdAt))
                    .font(.system(size: 12))
                    .foregroundColor(Color.gray500)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .padding(.bottom, 4)
    }
    
    private func formattedDate(_ dateString: String) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        
        if let date = dateFormatter.date(from: dateString) {
            let outputFormatter = DateFormatter()
            outputFormatter.dateFormat = "dd.MM.yyyy"
            return outputFormatter.string(from: date)
        }
        
        return dateString
    }
}

struct AdminActionButtonsView: View {
    let term: Term
    @Binding var isShowingEditForm: Bool
    let onApprove: () -> Void
    
    @State private var isApproving: Bool = false
    @State private var showApproveTooltip: Bool = false
    
    var body: some View {
        VStack {
            Spacer()
            HStack {
                if !term.isApproved {
                    Button(action: {
                        isApproving = true
                        showApproveTooltip = true
                        
                        // Запускаем утверждение
                        onApprove()
                        
                        // Автоматически скрываем подсказку через 3 секунды
                        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                            showApproveTooltip = false
                            isApproving = false
                        }
                    }) {
                        if isApproving {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                .scaleEffect(0.7)
                        } else {
                            Image(systemName: "checkmark.seal.fill")
                        }
                    }
                    .buttonStyle(.approve)
                    .disabled(isApproving)
                    .padding(.trailing, 12)
                    .overlay(
                        Group {
                            if showApproveTooltip {
                                VStack {
                                    Text("Термин утверждён!")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .padding(8)
                                        .background(Color.teal)
                                        .cornerRadius(8)
                                }
                                .offset(y: -50)
                                .transition(.opacity)
                                .animation(.easeInOut, value: showApproveTooltip)
                            }
                        }
                    )
                }
                
                Spacer()
                
                Button {
                    isShowingEditForm = true
                } label: {
                    Image(systemName: "pencil")
                }
                .buttonStyle(.add)
                .padding(.trailing, 20)
            }
            .padding(.bottom, 20)
        }
    }
} 