import json
import os
import re
import unicodedata

# Попытка импорта fitz (PyMuPDF), с обработкой ошибки импорта
try:
    import fitz
except ImportError:
    raise ImportError(
        "Модуль PyMuPDF (fitz) не установлен. "
        "Установите его с помощью команды: pip install pymupdf"
    )


def extract_text(path: str) -> list[list[str]]:
    """Извлекает текст из PDF файла по указанному пути."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден.")
 
    try:
        document = fitz.open(path)
    except Exception as e:
        raise RuntimeError(f"Не удалось открыть PDF: {path}. Ошибка: {str(e)}")
 
    pages = [
        [
            unicodedata.normalize("NFKC", block[4]) for block in page.get_text("blocks") if block[4].strip()
        ]
        for page in document
    ]
 
    document.close()
 
    return pages
 
 
def remove_redundant_pages(pages: list[list[str]]) -> list[list[str]]:
    """Удаляет избыточные страницы, такие как титульные листы."""
    if not pages:
        return pages
        
    first_page_text = "".join(pages[0]).replace(" ", "").replace("\n", "")
 
    has_header = (
            "МИНИСТЕРСТВО" in first_page_text and
            "Дальневосточныйфедеральныйуниверситет" in first_page_text
    )
    has_vladivostok_year = re.search(r"Владивосток20[1-9][0-9]", first_page_text)
 
    return pages[1:] if has_header and has_vladivostok_year else pages
 
 
def preprocess_page(pages: list[list[str]]) -> list[list[str]]:
    """Предобработка страниц: удаление колонтитулов и других служебных элементов."""
    full_patterns = [
        r"[А-Я]{2,3}-ДВФУ-\d+(?:/\d+)?-\d{4}",
        r"\d+из\d+",
        r"[А-Я]{2,3}-ДВФУ-\d+(?:/\d+)?-\d{4}\d+из\d+"
    ]
 
    fuzzy_pattern = (
        r"(?<=[А-Яа-я.;])"
        r"[-\s\n]*[А-Я]{2,3}"
        r"[-\s\n]*-?[-\s\n]*ДВФУ"
        r"[-\s\n]*-?[-\s\n]*\d+(?:/\d+)?"
        r"[-\s\n]*-?[-\s\n]*\d{4}"
        r"[-\s\n]*\d+"
        r"[-\s\n]*из"
        r"[-\s\n]*\d+"
    )
 
    cleaned_pages = []
 
    for page in pages:
        cleaned_page = []
 
        for paragraph in page:
            compressed = re.sub(r"[\s\n]+", "", paragraph.strip())
 
            if any(re.fullmatch(pat, compressed) for pat in full_patterns):
                continue
 
            cleaned_paragraph = re.sub(fuzzy_pattern, "", paragraph, flags=re.IGNORECASE)
            cleaned_page.append(cleaned_paragraph.strip())
 
        cleaned_pages.append([p for p in cleaned_page if p])
 
    return cleaned_pages
 
 
def remove_meaningless_text(paragraphs: list[str]) -> list[str]:
    """Удаляет бессмысленный текст, например, заголовки разделов управления."""
    pattern = re.compile(r"^\d+\.\s+Управление\s+\S+")
    dot_line_pattern = re.compile(r"\.{4,}")
    trailing_page_number = re.compile(r"\d{1,3}$")
 
    for i, para in enumerate(paragraphs):
        stripped = para.strip()
        if pattern.match(stripped):
            if dot_line_pattern.search(stripped) or trailing_page_number.search(stripped):
                continue
            return paragraphs[:i]
 
    return paragraphs
 
 
def merge_broken_lines(paragraphs: list[str]) -> list[str]:
    """Объединяет разорванные строки в связные параграфы."""
    merged = []
    buffer = ""
 
    def ends_with_terminal_punctuation(text: str) -> bool:
        return bool(re.search(r'[.!?…»";:]$', text.strip()))
 
    def is_paragraph_start(text: str) -> bool:
        return bool(re.match(r'^\d+(\.\d+)*\.', text.strip()))
 
    i = 0
    while i < len(paragraphs):
        current = paragraphs[i].strip()
        next_para = paragraphs[i + 1].strip() if i + 1 < len(paragraphs) else None
 
        if buffer:
            buffer += ' ' + current
        else:
            buffer = current
 
        if next_para and not ends_with_terminal_punctuation(current) and not is_paragraph_start(next_para):
            i += 1
            continue
 
        merged.append(buffer.strip())
        buffer = ""
        i += 1
 
    if buffer:
        merged.append(buffer.strip())
 
    return merged
 
 
def split_structure(paragraphs: list[str]) -> list[str]:
    """Разделяет текст по структурным элементам (нумерованным пунктам)."""
    pattern_lvl1_2 = re.compile(r'(?<!\d\.)\b\d+(?:\.\d+)?\.(?=\s|[А-Я(])')
    pattern_lvl3 = re.compile(r'\b\d+\.\d+\.\d\b')
 
    updated_paragraphs = []
    for para in paragraphs:
        para = pattern_lvl3.sub(lambda m: '\n' + m.group(0), para)
        para = pattern_lvl1_2.sub(lambda m: '\n' + m.group(0), para)
        updated_paragraphs.append(para)
 
    stripped_paragraphs = []
    for paragraph in updated_paragraphs:
        for stripped_paragraph in paragraph.split('\n'):
            stripped_paragraphs.append(stripped_paragraph)
 
    return [paragraph.strip() for paragraph in stripped_paragraphs if paragraph.strip()]
 
 
def split_on_semicolon(paragraphs: list[str]) -> list[str]:
    """Разделяет текст по точкам с запятой и маркированным спискам."""
    new_paragraphs = []
 
    for para in paragraphs:
        new_para = []
        in_brackets = False
 
        i = 0
        while i < len(para):
            if para[i] == '(':
                in_brackets = True
            elif para[i] == ')':
                in_brackets = False
 
            if para[i] == ';' and i < len(para) - 1 and not in_brackets:
                new_para.append('\n')
            elif para[i:i + 4] == ": - ":
                new_para.append(": \n-")
                i += 3
                continue
            else:
                new_para.append(para[i])
 
            i += 1
 
        new_paragraphs.append(''.join(new_para))
 
    stripped_paragraphs = []
 
    for paragraph in new_paragraphs:
        for para in paragraph.split('\n'):
            stripped_paragraphs.append(para)
 
    return stripped_paragraphs
 
 
def get_paragraphs(pages: list[list[str]]) -> list[str]:
    """Преобразует страницы в список параграфов, выполняя необходимую обработку."""
    paragraphs = [paragraph for page in pages for paragraph in page]
    paragraphs = [
        re.sub(r'\s{2,}', ' ', paragraph.replace('\n', ' ')) for paragraph in paragraphs
    ]
 
    paragraphs = remove_meaningless_text(paragraphs)
    paragraphs = merge_broken_lines(paragraphs)
    paragraphs = split_structure(paragraphs)
    paragraphs = split_on_semicolon(paragraphs)
 
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
 
 
def process_pdf(file_path: str) -> list[str]:
    """
    Обрабатывает PDF файл и возвращает список параграфов.
    
    Args:
        file_path: Полный путь к PDF файлу
        
    Returns:
        Список параграфов из PDF
    """
    pages = extract_text(file_path)
    pages = remove_redundant_pages(pages)
    pages = preprocess_page(pages)
    paragraphs = get_paragraphs(pages)
    return paragraphs
 
 
def is_table_of_contents_line(line: str) -> bool:
    """Проверяет, является ли строка частью оглавления."""
    line = line.strip()
    return (
            re.search(r"\.{4,}", line) or
            re.search(r"\s\d{1,3}$", line) or
            (re.match(r"^\d+(\.\d+)*", line) and
             not re.search(r"[-—:–]", line))
    )
 
 
def extract_glossary_automatically(paragraphs: list[str]) -> list[str]:
    """
    Автоматически извлекает раздел глоссария из списка параграфов.
    
    Args:
        paragraphs: Список параграфов документа
        
    Returns:
        Список строк, содержащих глоссарий
    """
    heading_re = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")
    keyword_re = re.compile(r"(термины|определения|сокращения)", re.I)
 
    result, capturing, base_prefix = [], False, None
 
    for para in paragraphs:
        line = para.strip()
        if is_table_of_contents_line(line):
            continue
 
        h = heading_re.match(line)
 
        if not capturing:
            if h and keyword_re.search(line):
                capturing, base_prefix = True, h.group(1)
                result.append(line)
        else:
            if h and not h.group(1).startswith(base_prefix):
                break
            result.append(line)
 
    return result
 
 
def first_spaced_dash(sentence: str):
    """Находит первое тире с пробелами, разделяющее термин и определение."""
    dash_chars = "-–—"
    paren = 0
    for i, ch in enumerate(sentence):
        if ch == '(':
            paren += 1
        elif ch == ')':
            paren = max(paren - 1, 0)
        elif ch in dash_chars and paren == 0:
            if i == 0:
                return None
            if sentence[i - 1].isspace() or sentence[i + 1].isspace():
                term = sentence[:i].strip()
                if term:
                    return term, sentence[i + 1:].strip()
    return None
 
 
def extract_pairs_from_line(line: str) -> list[tuple[str, str]]:
    """Извлекает пары (термин, определение) из строки текста."""
    pairs = []
    for sent in re.split(r'\.\s+|\.$', line):
        sent = sent.strip()
        if not sent:
            continue
        pair = first_spaced_dash(sent)
        if pair:
            pairs.append(pair)
        else:
            if pairs:
                t, d = pairs[-1]
                pairs[-1] = (t, f"{d} {sent}".strip())
    return pairs
 
 
def format_glossary(paragraphs: list[str]) -> list[tuple[str, str]]:
    """
    Форматирует параграфы глоссария в список пар (термин, определение).
    
    Args:
        paragraphs: Список параграфов из раздела глоссария
        
    Returns:
        Список пар (термин, определение)
    """
    num_prefix = re.compile(r'^\d+(?:\.\d+)*\s+')  # «1.4.1  …»
    kw_re = re.compile(r'(термины|определения|сокращения)', re.I)
 
    entries: list[tuple[str, str]] = []
 
    for raw in paragraphs:
        line = raw.strip().rstrip(';')
        if not line:
            continue
 
        line = num_prefix.sub('', line, 1)
 
        if kw_re.search(line):
            if ':' in line:
                line = line.split(':', 1)[1].lstrip()
                if not line:
                    continue
            else:
                continue
 
        pairs = extract_pairs_from_line(line)
        if pairs:
            entries.extend(pairs)
        else:
            if entries:
                t, d = entries[-1]
                entries[-1] = (t, f"{d} {line}".strip())
 
    return entries
 
 
def pairs_to_json(pairs: list[tuple[str, str]], filename=None, ensure_ascii=False, indent=2) -> str:
    """
    Преобразует список пар (термин, определение) в JSON строку.
    Опционально сохраняет в файл.
    
    Args:
        pairs: Список пар (термин, определение)
        filename: Путь к файлу для сохранения (опционально)
        ensure_ascii: Флаг для JSON.dumps
        indent: Отступ для JSON.dumps
        
    Returns:
        JSON строка
    """
    data = [{"term": term, "definition": definition} for term, definition in pairs]
    json_str = json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
 
    if filename is not None:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)
 
    return json_str
 
 
def get_glossary_entries(file_path: str, json_name=None) -> str:
    """
    Полная обработка PDF-файла: извлечение глоссария и преобразование в JSON.
    
    Args:
        file_path: Путь к PDF файлу
        json_name: Имя JSON файла для сохранения (опционально)
        
    Returns:
        JSON строка с данными глоссария
    """
    text = process_pdf(file_path)
 
    return pairs_to_json(format_glossary(extract_glossary_automatically(text)), json_name)
 
 
def extract_terms_from_pdf(file_path: str) -> list[tuple[str, str]]:
    """
    Извлекает термины и определения из PDF файла.
    
    Args:
        file_path: Путь к PDF файлу
        
    Returns:
        Список пар (термин, определение)
    """
    text = process_pdf(file_path)
    glossary_section = extract_glossary_automatically(text)
    return format_glossary(glossary_section) 