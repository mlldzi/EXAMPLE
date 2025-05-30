import SwiftUI
import Combine

struct LoginView: View {
    @ObservedObject private var authService = AuthService.shared
    
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    
    @StateObject private var subscriptions = TermCancellableStorage()
    
    var body: some View {
        ZStack {
            Color.bgPrimary.ignoresSafeArea()
            
            VStack(spacing: 24) {
                Spacer()
                
                VStack(spacing: 16) {
                    Image(systemName: "doc.text.magnifyingglass")
                        .font(.system(size: 60))
                        .foregroundColor(Color.accent)
                    
                    Text("Единый глоссарий терминов ВНД")
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(Color.gray700)
                        .multilineTextAlignment(.center)
                }
                .padding(.bottom, 40)
                
                VStack(spacing: 16) {
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.gray300, lineWidth: 1)
                        )
                    
                    SecureField("Пароль", text: $password)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.gray300, lineWidth: 1)
                        )
                    
                    if let errorMessage = errorMessage {
                        Text(errorMessage)
                            .font(.system(size: 14))
                            .foregroundColor(.red)
                            .padding(.top, 8)
                    }
                    
                    Button(action: login) {
                        if isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Войти")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .buttonStyle(.primary)
                    .padding(.top, 16)
                    .disabled(isLoading || email.isEmpty || password.isEmpty)
                }
                .padding(.horizontal, 20)
                
                Spacer()
                
                VStack {
                    Text("Нет учетной записи?")
                        .font(.system(size: 14))
                        .foregroundColor(Color.gray600)
                    
                    Text("Обратитесь к администратору")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(Color.accent)
                }
                .padding(.bottom, 20)
                
                Button(action: toggleDebugMode) {
                    Text("Режим админа (для тестирования)")
                        .font(.system(size: 12))
                        .foregroundColor(authService.isDebugAdminMode ? .teal : .gray500)
                }
                .padding(.bottom, 20)
            }
            .padding()
        }
    }
    
    private func login() {
        guard !email.isEmpty && !password.isEmpty else { return }
        
        isLoading = true
        errorMessage = nil
        
        authService.login(email: email, password: password)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case let .failure(error) = completion {
                        switch error {
                        case let .httpError(statusCode, _):
                            if statusCode == 401 {
                                errorMessage = "Неверный email или пароль"
                            } else {
                                errorMessage = "Ошибка сервера: \(statusCode)"
                            }
                        default:
                            errorMessage = "Ошибка: \(error.localizedDescription)"
                        }
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &subscriptions.cancellables)
    }
    
    private func toggleDebugMode() {
        authService.toggleDebugAdminMode()
    }
} 