import SwiftUI
import Combine

struct MainView: View {
    @ObservedObject private var authService = AuthService.shared
    @EnvironmentObject private var appState: AppState
    @StateObject private var tabViewModel = TabViewModel()
    
    var body: some View {
        Group {
            if authService.isLoggedIn {
                TabView(selection: $tabViewModel.selectedTab) {
                    NavigationView {
                        TermsListView()
                    }
                    .tabItem {
                        Label(
                            TabViewModel.Tab.terms.title,
                            systemImage: tabViewModel.selectedTab == TabViewModel.Tab.terms.rawValue
                                ? TabViewModel.Tab.terms.selectedIcon
                                : TabViewModel.Tab.terms.icon
                        )
                    }
                    .tag(TabViewModel.Tab.terms.rawValue)
                    
                    NavigationView {
                        Text("Документы ВНД")
                            .font(.largeTitle)
                    }
                    .tabItem {
                        Label(
                            TabViewModel.Tab.documents.title,
                            systemImage: tabViewModel.selectedTab == TabViewModel.Tab.documents.rawValue
                                ? TabViewModel.Tab.documents.selectedIcon
                                : TabViewModel.Tab.documents.icon
                        )
                    }
                    .tag(TabViewModel.Tab.documents.rawValue)
                    
                    NavigationView {
                        ProfileView()
                    }
                    .tabItem {
                        Label(
                            TabViewModel.Tab.profile.title,
                            systemImage: tabViewModel.selectedTab == TabViewModel.Tab.profile.rawValue
                                ? TabViewModel.Tab.profile.selectedIcon
                                : TabViewModel.Tab.profile.icon
                        )
                    }
                    .tag(TabViewModel.Tab.profile.rawValue)
                }
                .accentColor(Color.accent)
            } else {
                LoginView()
            }
        }
        .onReceive(authService.$isDebugAdminMode) { _ in
            // Обновление интерфейса при изменении режима администратора
            // Используем небольшую задержку для гарантии обновления
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                print("Обновление интерфейса: isAdmin = \(authService.isAdmin)")
            }
        }
    }
}

// Заглушки для пока не реализованных экранов
struct DocumentsListView: View {
    var body: some View {
        ZStack {
            Color.bgPrimary.ignoresSafeArea()
            
            VStack(spacing: 20) {
                Image(systemName: "folder")
                    .font(.system(size: 50))
                    .foregroundColor(Color.accent)
                
                Text("Список документов")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(Color.gray700)
                
                Text("Здесь будет отображаться список ВНД")
                    .font(.system(size: 16))
                    .foregroundColor(Color.gray600)
                    .multilineTextAlignment(.center)
            }
            .padding()
        }
        .navigationTitle("Документы")
    }
}

struct ProfileView: View {
    @ObservedObject private var authService = AuthService.shared
    
    var body: some View {
        ZStack {
            Color.bgPrimary.ignoresSafeArea()
            
            VStack(spacing: 24) {
                VStack(spacing: 8) {
                    Image(systemName: "person.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(Color.accent)
                        .padding(.bottom, 16)
                    
                    if let user = authService.currentUser {
                        Text(user.fullName ?? user.username ?? user.email)
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(Color.gray700)
                        
                        Text(user.email)
                            .font(.system(size: 16))
                            .foregroundColor(Color.gray600)
                        
                        HStack(spacing: 8) {
                            ForEach(user.roles, id: \.self) { role in
                                Text(role)
                                    .font(.system(size: 12, weight: .medium))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.accentLight)
                                    .foregroundColor(Color.accent)
                                    .cornerRadius(12)
                            }
                        }
                        .padding(.top, 8)
                    }
                }
                .padding()
                
                Button(action: {
                    authService.logout()
                }) {
                    Text("Выйти из аккаунта")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.primary)
                .padding(.horizontal, 20)
                .padding(.top, 40)
                
                Spacer()
            }
            .padding(.top, 40)
        }
        .navigationTitle("Профиль")
    }
} 