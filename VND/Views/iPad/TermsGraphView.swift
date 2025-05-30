import SwiftUI
import Combine

struct TermsGraphView: View {
    @StateObject private var viewModel = TermsGraphViewModel()
    @State private var scale: CGFloat = 1.0
    @State private var offset = CGSize.zero
    @State private var dragOffset = CGSize.zero
    @State private var selectedNodeId: String? = nil
    @EnvironmentObject private var navigationController: NavigationController
    
    var body: some View {
        ZStack {
            Color.bgPrimary.ignoresSafeArea()
            
            if viewModel.isLoading {
                LoadingView()
            } else if let errorMessage = viewModel.errorMessage {
                ErrorView(message: errorMessage, retryAction: viewModel.loadTerms)
            } else if viewModel.nodes.isEmpty {
                iPadEmptyStateView(
                    title: "Нет данных для визуализации",
                    message: "Термины не найдены или между ними нет связей",
                    iconName: "network"
                )
            } else {
                VStack {
                    // Панель инструментов графа
                    HStack {
                        Text("Визуализация связей терминов")
                            .font(.headline)
                        
                        Spacer()
                        
                        // Кнопки управления масштабом
                        HStack(spacing: 12) {
                            Button {
                                withAnimation { scale -= 0.1 }
                            } label: {
                                Image(systemName: "minus.magnifyingglass")
                            }
                            .disabled(scale <= 0.5)
                            
                            Text("\(Int(scale * 100))%")
                                .font(.caption)
                                .frame(width: 50)
                            
                            Button {
                                withAnimation { scale += 0.1 }
                            } label: {
                                Image(systemName: "plus.magnifyingglass")
                            }
                            .disabled(scale >= 2.0)
                            
                            Button {
                                withAnimation {
                                    scale = 1.0
                                    offset = .zero
                                }
                            } label: {
                                Image(systemName: "arrow.counterclockwise")
                            }
                        }
                        .padding(8)
                        .background(Color.white)
                        .cornerRadius(8)
                        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
                    }
                    .padding()
                    
                    ZStack {
                        // Область графа с возможностью масштабирования и перемещения
                        GraphArea(
                            nodes: viewModel.nodes,
                            edges: viewModel.edges,
                            scale: scale,
                            offset: CGSize(width: offset.width + dragOffset.width, height: offset.height + dragOffset.height),
                            selectedNodeId: $selectedNodeId
                        )
                        .environmentObject(navigationController)
                        .gesture(
                            DragGesture()
                                .onChanged { value in
                                    dragOffset = value.translation
                                }
                                .onEnded { value in
                                    offset.width += value.translation.width
                                    offset.height += value.translation.height
                                    dragOffset = .zero
                                }
                        )
                        
                        // Отображение информации о выбранном термине
                        if let selectedNodeId = selectedNodeId,
                           let selectedNode = viewModel.nodes.first(where: { $0.id == selectedNodeId }) {
                            VStack {
                                Spacer()
                                
                                SelectedNodeInfo(node: selectedNode)
                                    .environmentObject(navigationController)
                                    .transition(.move(edge: .bottom))
                                    .animation(.spring(), value: selectedNodeId)
                            }
                            .padding(.bottom)
                        }
                    }
                    .clipped()
                }
            }
        }
        .onAppear {
            viewModel.loadTerms()
        }
    }
}

// MARK: - Компоненты графа
struct GraphArea: View {
    let nodes: [TermNode]
    let edges: [TermEdge]
    let scale: CGFloat
    let offset: CGSize
    @Binding var selectedNodeId: String?
    
    var body: some View {
        ZStack {
            // Отрисовка ребер
            ForEach(edges) { edge in
                if let sourceNode = nodes.first(where: { $0.id == edge.source }),
                   let targetNode = nodes.first(where: { $0.id == edge.target }) {
                    EdgeLine(
                        from: CGPoint(x: sourceNode.x, y: sourceNode.y),
                        to: CGPoint(x: targetNode.x, y: targetNode.y),
                        weight: edge.weight
                    )
                }
            }
            
            // Отрисовка узлов
            ForEach(nodes) { node in
                NodeCircle(
                    node: node,
                    isSelected: node.id == selectedNodeId,
                    onTap: {
                        selectedNodeId = node.id
                    }
                )
                .position(x: node.x, y: node.y)
            }
        }
        .scaleEffect(scale)
        .offset(offset)
    }
}

struct EdgeLine: View {
    let from: CGPoint
    let to: CGPoint
    let weight: Int
    
    var body: some View {
        Path { path in
            path.move(to: from)
            path.addLine(to: to)
        }
        .stroke(
            Color.gray.opacity(0.5),
            style: StrokeStyle(
                lineWidth: CGFloat(weight),
                lineCap: .round
            )
        )
    }
}

struct NodeCircle: View {
    let node: TermNode
    let isSelected: Bool
    let onTap: () -> Void
    
    var body: some View {
        Circle()
            .fill(node.isApproved ? Color.teal : Color.orange)
            .frame(width: node.size, height: node.size)
            .overlay(
                Circle()
                    .stroke(isSelected ? Color.accent : Color.clear, lineWidth: 3)
            )
            .overlay(
                Text(String(node.name.prefix(1)))
                    .font(.system(size: min(node.size/2, 18), weight: .bold))
                    .foregroundColor(.white)
            )
            .shadow(color: Color.black.opacity(0.2), radius: 2, x: 0, y: 2)
            .onTapGesture {
                onTap()
            }
    }
}

struct SelectedNodeInfo: View {
    let node: TermNode
    @Environment(\.presentationMode) var presentationMode
    @EnvironmentObject private var navigationController: NavigationController
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(node.name)
                    .font(.headline)
                    .foregroundColor(.gray700)
                
                Spacer()
                
                if node.isApproved {
                    HStack {
                        Image(systemName: "checkmark.seal.fill")
                            .foregroundColor(.teal)
                        Text("Утвержден")
                            .font(.caption)
                            .foregroundColor(.teal)
                    }
                } else {
                    HStack {
                        Image(systemName: "hourglass")
                            .foregroundColor(.orange)
                        Text("На проверке")
                            .font(.caption)
                            .foregroundColor(.orange)
                    }
                }
            }
            
            Text(node.definition)
                .font(.body)
                .foregroundColor(.gray600)
                .lineLimit(3)
            
            HStack {
                Button(action: {
                    navigationController.navigateToTerm(id: node.id)
                }) {
                    Text("Открыть термин")
                }
                .buttonStyle(.borderedProminent)
                
                Spacer()
                
                Text("Связей: \(node.connectionCount)")
                    .font(.caption)
                    .foregroundColor(.gray500)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
    }
}

// MARK: - Модели данных для графа
struct TermNode: Identifiable {
    let id: String
    let name: String
    let definition: String
    let isApproved: Bool
    let x: CGFloat
    let y: CGFloat
    let size: CGFloat
    let tags: [String]
    let connectionCount: Int
}

struct TermEdge: Identifiable {
    let id: String
    let source: String
    let target: String
    let weight: Int
}

// MARK: - ViewModel для управления данными графа
class TermsGraphViewModel: ObservableObject {
    private let termService = TermService.shared
    private var cancellables = Set<AnyCancellable>()
    
    @Published var nodes: [TermNode] = []
    @Published var edges: [TermEdge] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    func loadTerms() {
        isLoading = true
        errorMessage = nil
        
        termService.getTerms(limit: 100)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case let .failure(error) = completion {
                        self?.errorMessage = "Ошибка загрузки терминов: \(error.localizedDescription)"
                        
                        // Если ошибка - загрузим демо-данные
                        self?.createDemoGraph()
                    }
                },
                receiveValue: { [weak self] terms in
                    if terms.isEmpty {
                        // Если данных нет - загрузим демо-данные
                        self?.createDemoGraph()
                    } else {
                        self?.createGraphFromTerms(terms)
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    // Создаем демонстрационные данные для графа
    private func createDemoGraph() {
        // Очищаем существующие данные
        self.nodes = []
        self.edges = []
        
        // Демонстрационные термины
        let demoTerms = [
            DemoTerm(id: "1", name: "Кредитный договор", definition: "Договор между банком и заемщиком о предоставлении кредита", isApproved: true, tags: ["кредит", "договор", "финансы"]),
            DemoTerm(id: "2", name: "Поручительство", definition: "Обязательство отвечать за исполнение обязательств другого лица", isApproved: true, tags: ["кредит", "обеспечение", "договор"]),
            DemoTerm(id: "3", name: "Ипотека", definition: "Залог недвижимого имущества в обеспечение обязательства", isApproved: true, tags: ["кредит", "недвижимость", "залог"]),
            DemoTerm(id: "4", name: "Овердрафт", definition: "Форма краткосрочного кредита, предоставляемого по расчетному счету", isApproved: false, tags: ["кредит", "счет", "финансы"]),
            DemoTerm(id: "5", name: "Депозит", definition: "Денежные средства или ценные бумаги, размещённые в банке", isApproved: true, tags: ["счет", "вклад", "финансы"]),
            DemoTerm(id: "6", name: "Аккредитив", definition: "Способ расчетов, при котором банк обязуется произвести платеж", isApproved: false, tags: ["расчеты", "финансы"]),
            DemoTerm(id: "7", name: "Залог", definition: "Способ обеспечения исполнения обязательств", isApproved: true, tags: ["обеспечение", "кредит"]),
            DemoTerm(id: "8", name: "Рефинансирование", definition: "Процесс пересмотра условий погашения кредитов", isApproved: true, tags: ["кредит", "финансы"]),
            DemoTerm(id: "9", name: "Банковская гарантия", definition: "Обязательство банка-гаранта уплатить денежную сумму", isApproved: false, tags: ["обеспечение", "гарантия"]),
            DemoTerm(id: "10", name: "Ключевая ставка", definition: "Процентная ставка ЦБ для кредитования коммерческих банков", isApproved: true, tags: ["ставка", "финансы", "ЦБ"])
        ]
        
        // Задаем размеры графа
        let centerX: CGFloat = 500
        let centerY: CGFloat = 400
        let radius: CGFloat = 300
        
        // Создаем узлы
        for (index, term) in demoTerms.enumerated() {
            let angle = 2 * .pi * Double(index) / Double(demoTerms.count)
            let x = centerX + radius * cos(angle)
            let y = centerY + radius * sin(angle)
            
            // Определяем размер узла в зависимости от количества тегов
            let size: CGFloat = CGFloat(30 + min(term.tags.count * 5, 20))
            
            // Подсчитываем количество связей для демонстрационного термина
            let connectionCount = demoTerms.filter { otherTerm in
                if term.id != otherTerm.id {
                    return !Set(term.tags).intersection(Set(otherTerm.tags)).isEmpty
                }
                return false
            }.count
            
            let node = TermNode(
                id: term.id,
                name: term.name,
                definition: term.definition,
                isApproved: term.isApproved,
                x: x,
                y: y,
                size: size,
                tags: term.tags,
                connectionCount: connectionCount
            )
            
            self.nodes.append(node)
        }
        
        // Создаем ребра между терминами с общими тегами
        for i in 0..<demoTerms.count {
            for j in (i+1)..<demoTerms.count {
                let term1 = demoTerms[i]
                let term2 = demoTerms[j]
                
                // Находим общие теги
                let commonTags = Set(term1.tags).intersection(Set(term2.tags))
                
                if !commonTags.isEmpty {
                    let edge = TermEdge(
                        id: "\(term1.id)-\(term2.id)",
                        source: term1.id,
                        target: term2.id,
                        weight: commonTags.count
                    )
                    
                    self.edges.append(edge)
                }
            }
        }
    }
    
    // Вспомогательная структура для демонстрационных терминов
    private struct DemoTerm {
        let id: String
        let name: String
        let definition: String
        let isApproved: Bool
        let tags: [String]
    }
    
    private func createGraphFromTerms(_ terms: [Term]) {
        // Если термины есть, но их меньше 3, все равно покажем демо-данные
        if terms.count < 3 {
            createDemoGraph()
            return
        }
        
        // Очищаем существующие данные
        self.nodes = []
        self.edges = []
        
        // Задаем размеры графа
        let centerX: CGFloat = 500
        let centerY: CGFloat = 400
        let radius: CGFloat = 300
        
        // Создаем узлы
        let nodeCount = terms.count
        for (index, term) in terms.enumerated() {
            let angle = 2 * .pi * Double(index) / Double(nodeCount)
            let x = centerX + radius * cos(angle)
            let y = centerY + radius * sin(angle)
            
            // Определяем размер узла в зависимости от количества тегов
            let size: CGFloat = CGFloat(30 + min(term.tags.count * 5, 20))
            
            // Подсчитываем количество связей
            let connectionCount = calculateConnectionCount(term: term, allTerms: terms)
            
            let node = TermNode(
                id: term.id,
                name: term.name,
                definition: term.currentDefinition,
                isApproved: term.isApproved,
                x: x,
                y: y,
                size: size,
                tags: term.tags,
                connectionCount: connectionCount
            )
            
            self.nodes.append(node)
        }
        
        // Создаем ребра между терминами с общими тегами
        for i in 0..<terms.count {
            for j in (i+1)..<terms.count {
                let term1 = terms[i]
                let term2 = terms[j]
                
                // Находим общие теги
                let commonTags = Set(term1.tags).intersection(Set(term2.tags))
                
                if !commonTags.isEmpty {
                    let edge = TermEdge(
                        id: "\(term1.id)-\(term2.id)",
                        source: term1.id,
                        target: term2.id,
                        weight: commonTags.count
                    )
                    
                    self.edges.append(edge)
                }
            }
        }
        
        // Если реальные данные есть, но связей между терминами нет, добавим искусственные связи
        if self.edges.isEmpty && self.nodes.count > 1 {
            // Создаем базовые связи через теги
            for i in 0..<self.nodes.count {
                for j in (i+1)..<self.nodes.count {
                    // Связываем узлы с весом 1, чтобы показать хотя бы какие-то связи
                    let edge = TermEdge(
                        id: "\(self.nodes[i].id)-\(self.nodes[j].id)",
                        source: self.nodes[i].id,
                        target: self.nodes[j].id,
                        weight: 1
                    )
                    
                    self.edges.append(edge)
                    
                    // Обновим счетчик связей
                    if let index = self.nodes.firstIndex(where: { $0.id == self.nodes[i].id }) {
                        let oldNode = self.nodes[index]
                        let newNode = TermNode(
                            id: oldNode.id,
                            name: oldNode.name,
                            definition: oldNode.definition,
                            isApproved: oldNode.isApproved,
                            x: oldNode.x,
                            y: oldNode.y,
                            size: oldNode.size,
                            tags: oldNode.tags,
                            connectionCount: oldNode.connectionCount + 1
                        )
                        self.nodes[index] = newNode
                    }
                    
                    if let index = self.nodes.firstIndex(where: { $0.id == self.nodes[j].id }) {
                        let oldNode = self.nodes[index]
                        let newNode = TermNode(
                            id: oldNode.id,
                            name: oldNode.name,
                            definition: oldNode.definition,
                            isApproved: oldNode.isApproved,
                            x: oldNode.x,
                            y: oldNode.y,
                            size: oldNode.size,
                            tags: oldNode.tags,
                            connectionCount: oldNode.connectionCount + 1
                        )
                        self.nodes[index] = newNode
                    }
                }
            }
        }
    }
    
    private func calculateConnectionCount(term: Term, allTerms: [Term]) -> Int {
        var count = 0
        
        for otherTerm in allTerms {
            if term.id != otherTerm.id {
                let commonTags = Set(term.tags).intersection(Set(otherTerm.tags))
                if !commonTags.isEmpty {
                    count += 1
                }
            }
        }
        
        return count
    }
} 