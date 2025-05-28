# Отчёт по моделям данных и CRUD операциям глоссария терминов

## Модели данных

*   **Term**: Представляет собой термин глоссария. Включает поля `name`, `current_definition`, `definitions_history` (список версий определений), `is_approved`, `approved_by`, `approved_at`, `tags`.
*   **TermDefinition**: Вложенная модель для хранения истории определений термина. Содержит `definition`, `created_at`, `created_by`.
*   **Document**: Представляет нормативный документ. Включает поля `title`, `document_number`, `approval_date`, `status`, `description`, `document_url`, `document_file_path`, `owner_id`, `approved_by`, `term_ids` (список ID связанных терминов), `department`, `tags`.
*   **TermDocumentRelation**: Представляет связь между термином и документом, описывая, как именно термин определен или используется в конкретном документе. Содержит `term_id`, `document_id`, `term_definition_in_document`, `context`, `locations` (список мест использования), `conflict_status`, `conflict_description`, `verified_by`, `verified_at`.
*   **Base Models (`MongoBaseModel`, `TimeStampedModel`)**: Обеспечивают базовую структуру для всех моделей MongoDB, включая UUID в качестве ID и автоматические поля `created_at` и `updated_at` с учетом временной зоны (UTC).

## CRUD Операции

*   **CRUDTerm**: Реализованы основные операции для терминов: создание (`create`), получение по ID (`get_by_id`) и имени (`get_by_name`), получение нескольких (`get_multiple`), обновление (`update`) с добавлением новой версии определения в историю, удаление (`delete`), поиск (`search`).
*   **CRUDDocument**: Реализованы операции для документов: создание (`create`), получение по ID (`get_by_id`) и номеру (`get_by_document_number`), получение нескольких (`get_multiple`), обновление (`update`), удаление (`delete`), добавление (`add_term`) и удаление (`remove_term`) терминов из списка связанных терминов документа, поиск (`search`).
*   **CRUDTermDocument**: Реализованы операции для связей: создание (`create`), получение по ID (`get_by_id`), по ID термина и документа (`get_by_term_and_document`), получение всех связей для термина (`get_by_term_id`) и документа (`get_by_document_id`), получение нескольких (`get_multiple`), обновление (`update`), удаление по ID (`delete`) и по ID термина и документа (`delete_by_term_and_document`).
