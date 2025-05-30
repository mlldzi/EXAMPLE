import SwiftUI
import Combine

struct TermsListView: View {
    @ObservedObject private var authService = AuthService.shared
    
    @State private var terms: [Term] = []
    @State private var searchQuery: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var isShowingAddTermForm = false
    
    @StateObject private var subscriptions = TermCancellableStorage()
    
    private let termService = TermService.shared
    
    var body: some View {
        ZStack {
            Color.bgPrimary.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Заголовок и поисковая строка
                VStack(spacing: 16) {
                    HStack {
                        Text("Глоссарий терминов")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(Color.gray700)
                        
                        Spacer()
                        
                        // Кнопка режима администратора
                        Button {
                            authService.toggleDebugAdminMode()
                        } label: {
                            HStack(spacing: 4) {
                                Image(systemName: "person.fill")
                                    .font(.system(size: 12))
                                Text("Админ")
                                    .font(.system(size: 12, weight: .medium))
                            }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                        }
                        .buttonStyle(.admin(isActive: authService.isAdmin))
                    }
                    
                    SearchBar(text: $searchQuery, onSubmit: loadTerms)
                }
                .padding(.horizontal, 16)
                .padding(.top, 16)
                .padding(.bottom, 12)
                .background(Color.bgPrimary)
                
                // Контент
                ZStack {
                    if isLoading && terms.isEmpty {
                        LoadingView()
                    } else if let errorMessage = errorMessage, terms.isEmpty {
                        ErrorView(message: errorMessage, retryAction: loadTerms)
                    } else if terms.isEmpty {
                        EmptyStateView(
                            title: "Термины не найдены",
                            message: "В глоссарии нет терминов, соответствующих поисковому запросу",
                            iconName: "magnifyingglass"
                        )
                    } else {
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                ForEach(terms) { term in
                                    NavigationLink(destination: TermDetailView(termId: term.id)) {
                                        TermCard(term: term)
                                            .foregroundColor(.primary)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                    .contentShape(Rectangle())
                                }
                            }
                            .padding(16)
                        }
                    }
                }
            }
            
            // Кнопка добавления термина
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    Button {
                        isShowingAddTermForm = true
                    } label: {
                        Image(systemName: "plus")
                    }
                    .buttonStyle(.add)
                    .padding(.trailing, 20)
                    .padding(.bottom, 20)
                }
            }
        }
        .sheet(isPresented: $isShowingAddTermForm) {
            AddTermForm(isPresented: $isShowingAddTermForm)
                .onDisappear {
                    loadTerms()
                }
        }
        .onChange(of: searchQuery) { _ in
            loadTerms()
        }
        .onAppear {
            loadTerms()
        }
    }
    
    private func loadTerms() {
        isLoading = true
        errorMessage = nil
        
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
} 