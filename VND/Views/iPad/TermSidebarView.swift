import SwiftUI
import Combine

struct TermSidebarView: View {
    @Binding var selectedTermId: String?
    @ObservedObject private var authService = AuthService.shared
    
    @State private var terms: [Term] = []
    @State private var searchQuery: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var isShowingAddTermForm = false
    @State private var filterType: TermFilterType = .all
    @State private var expandedCategories: Set<String> = []
    
    @StateObject private var subscriptions = TermCancellableStorage()
    private let termService = TermService.shared
    
    var body: some View {
        VStack(spacing: 0) {
            // Поисковая строка с улучшенным дизайном
            iPadSearchBar(text: $searchQuery, onSubmit: loadTerms)
                .padding()
            
            // Кнопки фильтров
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    FilterButton(title: "Все", isSelected: filterType == .all) {
                        filterType = .all
                        loadTerms()
                    }
                    
                    FilterButton(title: "Утвержденные", isSelected: filterType == .approved) {
                        filterType = .approved
                        loadTerms()
                    }
                    
                    FilterButton(title: "На проверке", isSelected: filterType == .pending) {
                        filterType = .pending
                        loadTerms()
                    }
                    
                    if authService.isAdmin {
                        FilterButton(title: "Для утверждения", isSelected: filterType == .toApprove) {
                            filterType = .toApprove
                            loadTerms()
                        }
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 8)
            }
            
            Divider()
            
            if isLoading && terms.isEmpty {
                LoadingView()
            } else if let errorMessage = errorMessage, terms.isEmpty {
                ErrorView(message: errorMessage, retryAction: loadTerms)
            } else if terms.isEmpty {
                iPadEmptyStateView(
                    title: "Термины не найдены",
                    message: "В глоссарии нет терминов, соответствующих поисковому запросу",
                    iconName: "magnifyingglass"
                )
            } else {
                // Группируем термины по первой букве или категориям
                let groupedTerms = groupTerms(terms)
                
                List {
                    ForEach(Array(groupedTerms.keys.sorted()), id: \.self) { key in
                        Section(header: Text(key)) {
                            ForEach(groupedTerms[key] ?? []) { term in
                                TermRow(term: term, isSelected: selectedTermId == term.id)
                                    .contentShape(Rectangle())
                                    .onTapGesture {
                                        selectedTermId = term.id
                                    }
                            }
                        }
                    }
                }
                .listStyle(SidebarListStyle())
            }
            
            Spacer()
            
            // Кнопка добавления термина
            if authService.isLoggedIn {
                Button {
                    isShowingAddTermForm = true
                } label: {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Добавить термин")
                    }
                    .font(.headline)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .foregroundColor(.white)
                    .background(Color.accent)
                    .cornerRadius(10)
                    .padding(.horizontal)
                    .padding(.bottom)
                }
            }
        }
        .background(Color.bgPrimary.ignoresSafeArea())
        .navigationTitle("Глоссарий терминов")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    authService.toggleDebugAdminMode()
                } label: {
                    Label("Режим админа", systemImage: "person.fill.badge.plus")
                        .foregroundColor(authService.isAdmin ? .teal : .gray)
                }
            }
        }
        .sheet(isPresented: $isShowingAddTermForm) {
            NavigationView {
                iPadAddTermForm(isPresented: $isShowingAddTermForm)
            }
            .onDisappear {
                loadTerms()
            }
        }
        .onChange(of: searchQuery) {
            loadTerms()
        }
        .onAppear {
            loadTerms()
        }
    }
    
    private func loadTerms() {
        isLoading = true
        errorMessage = nil
        
        var queryParams: [String: String] = [:]
        
        if !searchQuery.isEmpty {
            queryParams["query"] = searchQuery
        }
        
        // Добавляем фильтры в зависимости от выбранного типа
        switch filterType {
        case .approved:
            queryParams["approved"] = "true"
        case .pending:
            queryParams["approved"] = "false"
        case .toApprove:
            queryParams["pending_approval"] = "true"
        case .all:
            break
        }
        
        termService.getTerms(query: searchQuery.isEmpty ? nil : searchQuery)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case let .failure(error) = completion {
                        errorMessage = "Ошибка загрузки терминов: \(error.localizedDescription)"
                    }
                },
                receiveValue: { terms in
                    self.terms = terms
                }
            )
            .store(in: &subscriptions.cancellables)
    }
    
    private func groupTerms(_ terms: [Term]) -> [String: [Term]] {
        var groupedTerms: [String: [Term]] = [:]
        
        for term in terms {
            let firstChar = String(term.name.prefix(1).uppercased())
            if groupedTerms[firstChar] != nil {
                groupedTerms[firstChar]!.append(term)
            } else {
                groupedTerms[firstChar] = [term]
            }
        }
        
        // Сортируем термины в каждой группе по алфавиту
        for key in groupedTerms.keys {
            groupedTerms[key]?.sort { $0.name < $1.name }
        }
        
        return groupedTerms
    }
}

// Тип фильтра для терминов
enum TermFilterType {
    case all
    case approved
    case pending
    case toApprove
}

// Кнопка фильтра
struct FilterButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.accent.opacity(0.2) : Color.gray200)
                .foregroundColor(isSelected ? Color.accent : Color.gray700)
                .cornerRadius(20)
                .overlay(
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(isSelected ? Color.accent : Color.clear, lineWidth: 1)
                )
        }
    }
}

// Строка термина в списке
struct TermRow: View {
    let term: Term
    let isSelected: Bool
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(term.name)
                    .font(.headline)
                
                if !term.tags.isEmpty {
                    Text(term.tags.joined(separator: ", "))
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
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
        .padding(.vertical, 4)
        .contentShape(Rectangle())
        .background(isSelected ? Color.accent.opacity(0.1) : Color.clear)
    }
} 