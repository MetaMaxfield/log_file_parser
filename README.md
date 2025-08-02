# Скрипт для обработки лог-файлов

## ✅ Функционал:
- **Формирование отчёта** со списком эндпоинтов:
  - количество запросов по каждому эндпоинту;
  - среднее время ответа.
  
  ![Пример отчёта с 1 файлом](https://github.com/MetaMaxfield/log_file_processing/blob/master/screen_1file.png)

- **Поддержка передачи пути к файлам** (одного или нескольких):

  ![Пример с указанием пути](https://github.com/MetaMaxfield/log_file_processing/blob/master/screen_path_file.png)
  ![Пример с 2 файлами](https://github.com/MetaMaxfield/log_file_processing/blob/master/screen_2files.png)

- **Выбор типа отчёта** (по умолчанию: `average`).

- **Полное тестирование с помощью pytest**  
  Покрытие: **99%**

  ![Скриншот тестов](https://github.com/MetaMaxfield/log_file_processing/blob/master/screen_tests.png)

---

## 🚀 Запуск:
```bash
python main.py --file file1.log file2.log --report average
