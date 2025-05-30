import SwiftUI
import Combine

struct iPadTermDetailView: View {
    let termId: String
    
    @ObservedObject private var authService = AuthService.shared
    @State private var term: Term?
    @State private var relatedDocuments: [Document] = []
    @State private var relatedTerms: [Term] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var isShowingEditForm: Bool = false
    @State private var selectedTab: Int = 0
    @State private var showAnnotationView: Bool = false
    @State private var annotations: [Annotation] = []
    @State private var isCreatingNewAnnotation: Bool = false
    @State private var newAnnotationText: String = ""
    
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
                if showAnnotationView {
                    AnnotationView(
                        term: term,
                        annotations: $annotations,
                        isCreatingNew: $isCreatingNewAnnotation,
                        newAnnotationText: $newAnnotationText,
                        onClose: { showAnnotationView = false }
                    )
                } else {
                    iPadTermContent(
                        term: term,
                        relatedDocuments: relatedDocuments,
                        relatedTerms: relatedTerms,
                        selectedTab: $selectedTab,
                        isShowingEditForm: $isShowingEditForm,
                        authService: authService,
                        onApprove: approveCurrentTerm,
                        onShowAnnotations: { showAnnotationView = true }
                    )
                }
            }
        }
        .navigationTitle(term?.name ?? "Загрузка...")
        .navigationBarTitleDisplayMode(.large)
        .onAppear {
            loadTermData()
        }
        .sheet(isPresented: $isShowingEditForm) {
            if let term = term {
                NavigationView {
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
    }
    
    private func loadTermData() {
        isLoading = true
        errorMessage = nil
        
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
                    loadRelatedDocuments()
                    
                    // Загружаем "похожие" термины (на основе тегов)
                    loadRelatedTerms(tags: term.tags)
                    
                    // Загружаем сохраненные аннотации (в реальном приложении здесь был бы API-запрос)
                    loadAnnotations()
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
    
    private func loadRelatedTerms(tags: [String]) {
        // В реальном приложении здесь был бы API-запрос для получения связанных терминов
        // Для демонстрации мы просто имитируем загрузку связанных терминов
        isLoading = true
        
        termService.getTerms()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                },
                receiveValue: { allTerms in
                    // Фильтруем термины, у которых есть общие теги с текущим термином
                    self.relatedTerms = allTerms.filter { term in
                        if term.id == termId { return false } // Исключаем текущий термин
                        
                        // Ищем хотя бы один общий тег
                        return !Set(term.tags).intersection(Set(tags)).isEmpty
                    }
                }
            )
            .store(in: &subscriptions.cancellables)
    }
    
    private func loadAnnotations() {
        // В реальном приложении здесь был бы API-запрос для загрузки аннотаций
        // Для демонстрации используем локальное хранилище или имитируем загрузку
        
        // Проверяем, есть ли сохраненные аннотации для данного термина
        if let savedAnnotations = UserDefaults.standard.array(forKey: "annotations_\(termId)") as? [[String: Any]] {
            self.annotations = savedAnnotations.compactMap { dict in
                guard let text = dict["text"] as? String,
                      let date = dict["date"] as? Date else {
                    return nil
                }
                return Annotation(text: text, date: date)
            }
        } else {
            // Для демонстрации создаем пример аннотации
            self.annotations = [
                Annotation(text: "Это важный термин для изучения основ банковского дела", date: Date().addingTimeInterval(-86400))
            ]
        }
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
                    }
                },
                receiveValue: { updatedTerm in
                    self.term = updatedTerm
                    
                    // Добавляем тактильную обратную связь
                    let generator = UINotificationFeedbackGenerator()
                    generator.notificationOccurred(.success)
                }
            )
            .store(in: &subscriptions.cancellables)
    }
}

// MARK: - iPad расширенное представление содержимого термина
struct iPadTermContent: View {
    let term: Term
    let relatedDocuments: [Document]
    let relatedTerms: [Term]
    @Binding var selectedTab: Int
    @Binding var isShowingEditForm: Bool
    let authService: AuthService
    let onApprove: () -> Void
    let onShowAnnotations: () -> Void
    
    var body: some View {
        VStack(spacing: 0) {
            // Верхняя информационная панель
            HStack(alignment: .center, spacing: 16) {
                // Статус термина
                HStack {
                    if term.isApproved {
                        Image(systemName: "checkmark.seal.fill")
                            .foregroundColor(.teal)
                            .font(.system(size: 22))
                        
                        Text("Утвержден")
                            .font(.headline)
                            .foregroundColor(.teal)
                    } else {
                        Image(systemName: "hourglass")
                            .foregroundColor(.orange)
                            .font(.system(size: 22))
                        
                        Text("На проверке")
                            .font(.headline)
                            .foregroundColor(.orange)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(term.isApproved ? Color.teal.opacity(0.1) : Color.orange.opacity(0.1))
                .cornerRadius(10)
                
                // Теги
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(term.tags, id: \.self) { tag in
                            Text(tag)
                                .font(.system(size: 14, weight: .medium))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(Color.accentLight)
                                .foregroundColor(Color.accent)
                                .cornerRadius(12)
                        }
                    }
                }
                
                Spacer()
                
                // Кнопки действий
                HStack(spacing: 16) {
                    Button(action: onShowAnnotations) {
                        Label("Заметки", systemImage: "note.text")
                    }
                    .buttonStyle(.bordered)
                    
                    if authService.isAdmin && !term.isApproved {
                        Button(action: onApprove) {
                            Label("Утвердить", systemImage: "checkmark.seal")
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(.teal)
                    }
                    
                    if authService.isAdmin {
                        Button {
                            isShowingEditForm = true
                        } label: {
                            Label("Редактировать", systemImage: "pencil")
                        }
                        .buttonStyle(.bordered)
                    }
                }
            }
            .padding()
            .background(Color.white)
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 2)
            .padding([.horizontal, .top])
            
            // Основное содержимое в колонках
            HStack(alignment: .top, spacing: 20) {
                // Левая колонка - определение
                VStack(alignment: .leading, spacing: 16) {
                    Text("Определение")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.gray700)
                    
                    Text(term.currentDefinition)
                        .font(.body)
                        .foregroundColor(.gray700)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white)
                        .cornerRadius(12)
                    
                    if let history = term.definitionsHistory, !history.isEmpty && authService.isAdmin {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("История изменений")
                                .font(.title3)
                                .fontWeight(.bold)
                                .foregroundColor(.gray700)
                            
                            ForEach(0..<min(history.count, 3), id: \.self) { index in
                                HistoryCard(
                                    definition: history[index],
                                    versionNumber: history.count - index
                                )
                            }
                            
                            if history.count > 3 {
                                Button("Показать все \(history.count) версий") {
                                    selectedTab = 2
                                }
                                .font(.subheadline)
                                .foregroundColor(.accent)
                                .padding(.top, 4)
                            }
                        }
                        .padding()
                        .background(Color.white)
                        .cornerRadius(12)
                    }
                }
                .frame(maxWidth: .infinity)
                
                // Правая колонка - связанные документы и термины
                VStack(alignment: .leading, spacing: 16) {
                    // Связанные документы
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Связанные документы")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundColor(.gray700)
                        
                        if relatedDocuments.isEmpty {
                            Text("Нет связанных документов")
                                .font(.body)
                                .foregroundColor(.gray500)
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .center)
                                .background(Color.white)
                                .cornerRadius(12)
                        } else {
                            ForEach(relatedDocuments.prefix(3)) { document in
                                DocumentCard(document: document)
                            }
                            
                            if relatedDocuments.count > 3 {
                                Button("Показать все \(relatedDocuments.count) документов") {
                                    selectedTab = 1
                                }
                                .font(.subheadline)
                                .foregroundColor(.accent)
                                .padding(.top, 4)
                            }
                        }
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    
                    // Связанные термины
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Похожие термины")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundColor(.gray700)
                        
                        if relatedTerms.isEmpty {
                            Text("Нет похожих терминов")
                                .font(.body)
                                .foregroundColor(.gray500)
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .center)
                                .background(Color.white)
                                .cornerRadius(12)
                        } else {
                            ForEach(relatedTerms.prefix(5)) { relatedTerm in
                                RelatedTermCard(term: relatedTerm)
                            }
                        }
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                }
                .frame(maxWidth: .infinity)
            }
            .padding()
        }
    }
}

// MARK: - Вспомогательные компоненты для iPad-интерфейса

struct HistoryCard: View {
    let definition: TermDefinition
    let versionNumber: Int
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Версия \(versionNumber)")
                    .font(.headline)
                    .foregroundColor(.accent)
                
                Spacer()
                
                Text(formattedDate(definition.createdAt))
                    .font(.caption)
                    .foregroundColor(.gray500)
            }
            
            Text(definition.definition)
                .font(.body)
                .foregroundColor(.gray700)
                .lineLimit(3)
            
            HStack {
                Text("Автор: \(definition.createdBy)")
                    .font(.caption)
                    .foregroundColor(.gray500)
            }
        }
        .padding()
        .background(Color.gray100)
        .cornerRadius(8)
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

struct DocumentCard: View {
    let document: Document
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(document.title)
                .font(.headline)
                .foregroundColor(.gray700)
            
            if let description = document.description {
                Text(description)
                    .font(.body)
                    .foregroundColor(.gray600)
                    .lineLimit(2)
            }
            
            HStack {
                if let documentNumber = document.documentNumber {
                    Text("№ \(documentNumber)")
                        .font(.caption)
                        .foregroundColor(.gray500)
                }
                
                Spacer()
                
                if let approvalDate = document.approvalDate {
                    Text("От \(formattedDate(approvalDate))")
                        .font(.caption)
                        .foregroundColor(.gray500)
                }
            }
        }
        .padding()
        .background(Color.gray100)
        .cornerRadius(8)
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

struct RelatedTermCard: View {
    let term: Term
    
    var body: some View {
        NavigationLink(destination: iPadTermDetailView(termId: term.id)) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(term.name)
                        .font(.headline)
                        .foregroundColor(.gray700)
                    
                    Text(term.currentDefinition)
                        .font(.caption)
                        .foregroundColor(.gray600)
                        .lineLimit(2)
                }
                
                Spacer()
                
                if term.isApproved {
                    Image(systemName: "checkmark.seal.fill")
                        .foregroundColor(.teal)
                } else {
                    Image(systemName: "hourglass")
                        .foregroundColor(.orange)
                }
            }
            .padding()
            .background(Color.gray100)
            .cornerRadius(8)
        }
    }
}

// MARK: - Модель и представление для аннотаций

struct Annotation: Identifiable {
    let id = UUID()
    let text: String
    let date: Date
}

struct AnnotationView: View {
    let term: Term
    @Binding var annotations: [Annotation]
    @Binding var isCreatingNew: Bool
    @Binding var newAnnotationText: String
    let onClose: () -> Void
    
    var body: some View {
        VStack {
            HStack {
                Button {
                    onClose()
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.gray500)
                }
                
                Spacer()
                
                Text("Заметки к термину")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Spacer()
                
                Button {
                    isCreatingNew.toggle()
                } label: {
                    Image(systemName: isCreatingNew ? "checkmark.circle.fill" : "plus.circle.fill")
                        .font(.title2)
                        .foregroundColor(isCreatingNew ? .green : .accent)
                }
            }
            .padding()
            
            if isCreatingNew {
                VStack {
                    TextEditor(text: $newAnnotationText)
                        .padding()
                        .frame(minHeight: 100)
                        .background(Color.gray100)
                        .cornerRadius(12)
                    
                    HStack {
                        Spacer()
                        
                        Button {
                            isCreatingNew = false
                            newAnnotationText = ""
                        } label: {
                            Text("Отмена")
                        }
                        .buttonStyle(.bordered)
                        
                        Button {
                            // Сохраняем новую аннотацию
                            let newAnnotation = Annotation(text: newAnnotationText, date: Date())
                            annotations.append(newAnnotation)
                            
                            // Сохраняем в UserDefaults (в реальном приложении - на сервер)
                            saveAnnotations()
                            
                            // Сбрасываем форму
                            isCreatingNew = false
                            newAnnotationText = ""
                        } label: {
                            Text("Сохранить")
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(newAnnotationText.isEmpty)
                    }
                }
                .padding()
            } else {
                if annotations.isEmpty {
                    VStack(spacing: 12) {
                        Image(systemName: "note.text")
                            .font(.system(size: 60))
                            .foregroundColor(Color.gray300)
                        
                        Text("Нет заметок")
                            .font(.title3)
                            .foregroundColor(Color.gray600)
                        
                        Text("Добавьте заметки к этому термину для личного использования")
                            .font(.body)
                            .foregroundColor(Color.gray500)
                            .multilineTextAlignment(.center)
                        
                        Button {
                            isCreatingNew = true
                        } label: {
                            Text("Добавить заметку")
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.top, 8)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List {
                        ForEach(annotations.sorted(by: { $0.date > $1.date })) { annotation in
                            VStack(alignment: .leading, spacing: 8) {
                                Text(annotation.text)
                                    .font(.body)
                                    .foregroundColor(.gray700)
                                
                                Text(formattedDate(annotation.date))
                                    .font(.caption)
                                    .foregroundColor(.gray500)
                            }
                            .padding()
                            .background(Color.gray100)
                            .cornerRadius(12)
                            .padding(.vertical, 4)
                        }
                        .onDelete { indexSet in
                            annotations.remove(atOffsets: indexSet)
                            saveAnnotations()
                        }
                    }
                    .listStyle(PlainListStyle())
                }
            }
        }
        .background(Color.bgPrimary.ignoresSafeArea())
    }
    
    private func saveAnnotations() {
        // Преобразуем аннотации в формат для сохранения
        let annotationsData = annotations.map { annotation -> [String: Any] in
            return [
                "text": annotation.text,
                "date": annotation.date
            ]
        }
        
        // Сохраняем в UserDefaults
        UserDefaults.standard.set(annotationsData, forKey: "annotations_\(term.id)")
    }
    
    private func formattedDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - Форма добавления термина для iPad
struct iPadAddTermForm: View {
    @Binding var isPresented: Bool
    @ObservedObject private var authService = AuthService.shared
    
    @State private var name: String = ""
    @State private var definition: String = ""
    @State private var tags: String = ""
    @State private var selectedDocumentId: String?
    @State private var isSubmitting: Bool = false
    @State private var errorMessage: String?
    @State private var documents: [Document] = []
    @State private var isLoadingDocuments: Bool = false
    @State private var previewEnabled: Bool = true
    
    @StateObject private var subscriptions = TermCancellableStorage()
    
    private let termService = TermService.shared
    private let documentService = DocumentService.shared
    
    var body: some View {
        HStack(spacing: 0) {
            // Левая панель - форма
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
                                .frame(minHeight: 200)
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
                    
                    Toggle("Предпросмотр", isOn: $previewEnabled)
                        .toggleStyle(SwitchToggleStyle(tint: Color.accent))
                    
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
            .frame(maxWidth: 500)
            
            // Правая панель - предпросмотр
            if previewEnabled {
                VStack {
                    Text("Предпросмотр")
                        .font(.title2)
                        .padding()
                    
                    ScrollView {
                        VStack(alignment: .leading, spacing: 16) {
                            // Заголовок
                            HStack {
                                Text(name.isEmpty ? "Название термина" : name)
                                    .font(.system(size: 28, weight: .bold))
                                    .foregroundColor(name.isEmpty ? .gray400 : .gray700)
                                
                                Spacer()
                                
                                VStack {
                                    Image(systemName: "hourglass")
                                        .foregroundColor(.orange)
                                        .font(.system(size: 20))
                                    
                                    Text("На проверке")
                                        .font(.system(size: 12, weight: .medium))
                                        .foregroundColor(.orange)
                                }
                                .padding(.vertical, 8)
                                .padding(.horizontal, 12)
                                .background(Color.orange.opacity(0.1))
                                .cornerRadius(8)
                            }
                            
                            // Теги
                            if !tags.isEmpty {
                                ScrollView(.horizontal, showsIndicators: false) {
                                    HStack(spacing: 8) {
                                        ForEach(tags.split(separator: ",").map { String($0.trimmingCharacters(in: .whitespacesAndNewlines)) }, id: \.self) { tag in
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
                            }
                            
                            // Определение
                            Text("Определение")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.gray700)
                                .padding(.top, 8)
                            
                            Text(definition.isEmpty ? "Определение термина будет отображаться здесь" : definition)
                                .font(.system(size: 16))
                                .foregroundColor(definition.isEmpty ? .gray400 : .gray700)
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.white)
                                .cornerRadius(12)
                        }
                        .padding()
                    }
                    .background(Color.gray100)
                    .cornerRadius(12)
                    .padding()
                }
                .frame(maxWidth: .infinity)
                .background(Color.bgPrimary)
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
        
        let tagArray = tags.isEmpty ? [] : tags.split(separator: ",").map { String($0.trimmingCharacters(in: .whitespacesAndNewlines)) }
        
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
                    // Добавляем тактильную обратную связь
                    let generator = UINotificationFeedbackGenerator()
                    generator.notificationOccurred(.success)
                    
                    isPresented = false
                }
            )
            .store(in: &subscriptions.cancellables)
    }
} 