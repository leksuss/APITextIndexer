# APITextIndexer
Приложение сканирует указанную папку и подпапки, находит текстовые файлы и индексирует их. После чего запускается API-сервер, выдающий по HTTP запросам статистику по словам и файлам.

### Возможности
 - поддерживает русский и английский языки
 - сканирует txt, md, docx файлов на выбор
 - обрабатывает также текстовые файлы с кодировками отличными от UTF-8
 - пропускает файлы, если их содержимое не текстовое, даже если расширение говорит об обратном

### Установка
Для работы приложения необходимо установить следующие пакеты:
`pip install argparse pymongo flask_restful chardet`

либо установить зависимости из файла requirements.txt:
`pip install -r requirements.txt`

### Запуск
`python run.py`
По умолчанию приложение сканирует текующую директорию со всеми поддиректориями и ищет файлы c расширением `txt`
Для задания другой директории укажите ее с ключом `-d`. Наличие слэша на конце не имеет значения:
`python run.py -d /library/`
Чтобы укзаать нужные для индексации типы файлов, перечислите их расширения в ключе `-t`:
`python run.py -d /library/ -t txt docx`
Поддерживаются типы `txt`, `md` и `docx`. Без ключа индексируются только `txt` файлы.

## Описание запросов и результатов выдачи API
### Статистика по всем файлам
`/files/` - список всех файлов и общей статистикой по ним. Результаты:
`max_size` - максимальный размер файла
`min_size`  - минимальный разме рфайла
`avg_size` - средний размер файла
`max_total_words` - максимальное кол-во слов в одном файле
`min_total_words`  - минимальное кол-во слов в одном файле
`avg_total_words` - среднее кол-во слов в файлах
`max_uniq_words` - максимальное кол-во уникальных слов в одном файле
`min_uniq_words`  - минимальное кол-во уникальных слов в одном файле
`avg_uniq_words`  - среднее кол-во уникальных слов в одном файле
`count_files`  - кол-во файлов
`list_files` - список всех файлов, где `_id` - уникальный идентификатор, `path_file` - полный путь к файлу

### Статистика по файлу
`/files/{id}` - статистика по файлу с уникальным идентификатором `id`. Результаты:
`_id` - уникальный идентификатор
`name` - имя файла
`path` - путь к файлу
`ext` - расширение файла
`size` - размер файла в байтах
`total_words` - общее кол-во слов в файле
`frequent_word` - самое частое слово в файле, словарь где `word` - слово, `count` - кол-во вхождений слова
`rare_word` - самое редкое слово в файле, словарь где `word` - слово, `count` - кол-во вхождений слова
`avglen_word` - средняя длина слова в файле среди всех слов
`avglen_uniqword` - средняя длина слова в файле среди уникальных слов
`vowel_count` - количество гласных букв в файле
`consonant_count` - количество согласных букв в файле
`vowel_count_uniqword`  - количество гласных букв в файле среди уникальных слов
`consonant_count_uniqword`  - количество согласных букв в файле среди уникальных слов

### Статистика по всем словам
`/words/` - общая статистика по словам. Результаты:
`total_words` - общее кол-во слов во всех файлах
`uniq_words` - кол-во уникальных слов во всех файлах
`avglen_word` - средняя длина слова во всех файлах
`avglen_uniqword` - средняя длина уникальных слов во всех файлах
`vowel_count` - кол-во гласных во всех словах всех файлов
`cons_count` - кол-во согласных во всех словах всех файлов
`vowel_count_uniqword` - кол-во гласных во всех уникальных словах всех файлов
`cons_count_uniqword` - кол-во согласных во всех уникальных словах всех файлов
`rare_word` - самое редкое слово во всех файлах, словарь, возвращающий немного более краткий вариант объекта слово (см.ниже)
`frequent_word` - самое частое слово во всех файлах, аналогично `rare_word`

### Статистика по слову
Есть два варианта получения статистики по слову: по id и по текстовому представлению.
`/words/{id}` - статистика по слову с уникальным идентификатором `id`. Например:
`/words/5e29eca6c57cbcaeeba1e74b`
`/words/text/{word}` - статистика по слову с текстовым представлением. Например:
`/words/text/привет`
Результат не зависит от типа запроса.
`_id` - уникальный идентификатор слова
`word` - текстовое представление слова
`count` - кол-во вхождений слова во всех файлах
`len` - длина слова
`vowel` - кол-во гласных в слове
`consonant` - кол-во согласных в слове
`files_stat` - список объектов файлов краткого формата, где нашлось это слово. Состоит из словарей, где `_id` - уникальный идентификатор файла,  `name` - путь к файлу с именем и  `count` - количество вхождений данного слова в этом файле.

## Описание реализации
Приложение разделено на 2 части. `folderparser.py` перебирает файлы, проверяет, обрабатывает если нужно, вычленяет слова, собирает их все в один большой словарь и вставляет в MongoDB. Каждое уникальное слово - документ в коллекции. `responces.py` отвечает за выдачу результатов через API. Статистика по каждому ресурсу собирается через запросы к БД и выдается пользователю API. Для удобного добавления новых форматов для индексации, функции чтения и предварительной обработки файлов были вынесены в отдельный модуль `IOfile.py`. Собирает весь функционал и является точкой входа `run.py`