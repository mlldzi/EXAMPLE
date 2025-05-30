import SwiftUI

struct SplitViewContainer: View {
    @ObservedObject private var authService = AuthService.shared
    @StateObject private var navigationController = NavigationController()
    
    var body: some View {
        // Проверяем, авторизован ли пользователь
        if !authService.isLoggedIn {
            // Показываем экран входа для неавторизованных пользователей
            LoginView()
        } else {
            // Основной интерфейс для авторизованных пользователей
            NavigationView {
                // Левая панель - список терминов
                TermSidebarView(selectedTermId: $navigationController.selectedTermId)
                    .frame(minWidth: 320)
                
                // Правая панель - детали термина или граф связей
                if navigationController.showGraph {
                    TermsGraphView()
                        .environmentObject(navigationController)
                        .navigationTitle("Связи терминов")
                        .toolbar {
                            ToolbarItem(placement: .navigationBarTrailing) {
                                Button {
                                    navigationController.showGraph = false
                                } label: {
                                    Text("К детальному просмотру")
                                }
                            }
                        }
                } else {
                    if let termId = navigationController.selectedTermId {
                        iPadTermDetailView(termId: termId)
                            .toolbar {
                                ToolbarItem(placement: .navigationBarTrailing) {
                                    Button {
                                        navigationController.showGraph = true
                                    } label: {
                                        Label("Показать связи", systemImage: "network")
                                    }
                                }
                                
                                ToolbarItem(placement: .navigationBarLeading) {
                                    Button(action: {
                                        authService.logout()
                                    }) {
                                        Label("Выход", systemImage: "rectangle.portrait.and.arrow.right")
                                    }
                                }
                            }
                    } else {
                        // Заглушка при отсутствии выбора
                        VStack {
                            Image(systemName: "doc.text.magnifyingglass")
                                .font(.system(size: 70))
                                .foregroundColor(Color.accent.opacity(0.7))
                            
                            Text("Выберите термин для просмотра")
                                .font(.title2)
                                .foregroundColor(Color.gray600)
                                .padding(.top)
                            
                            // Добавляем кнопку выхода
                            Button(action: {
                                authService.logout()
                            }) {
                                HStack {
                                    Image(systemName: "rectangle.portrait.and.arrow.right")
                                    Text("Выйти")
                                }
                                .padding()
                            }
                            .buttonStyle(.bordered)
                            .padding(.top, 20)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.bgPrimary)
                    }
                }
            }
            .navigationViewStyle(DoubleColumnNavigationViewStyle())
            .environmentObject(navigationController)
            .onReceive(NotificationCenter.default.publisher(for: Notification.Name("navigateToTermNotification"))) { notification in
                if let termId = notification.object as? String {
                    navigationController.selectedTermId = termId
                    navigationController.showGraph = false
                }
            }
        }
    }
} 