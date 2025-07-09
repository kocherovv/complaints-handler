# 📣 Система обработки жалоб клиентов

> Сервис, который принимает жалобы от клиентов, анализирует их тональность, определяет категорию с помощью ИИ, сохраняет в базу данных и предоставляет API для работы с обращениями.

---

## 🧩 Основные функции

- ✅ Принимает текстовые жалобы от клиентов
- 🔍 Анализирует **тональность** через [APILayer Sentiment Analysis](https://apilayer.com/marketplace/sentiment_analysis-api)
- 🤖 Определяет **категорию** с помощью OpenAI GPT-3.5 Turbo
- 💾 Сохраняет данные в **SQLite**
- 🕒 Автоматическое проставление времени создания
- 🔄 Возможность закрытия жалобы через API

---

## 📦 Требования

- Python 3.10+
- FastAPI
- SQLite
- OpenAI API ключ
- APILayer API ключ

---

## 🔐 Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
SENTIMENT_API_KEY=your_apilayer_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## 📦 Запуск

Выполните в корне проекта

```bash
docker-compose up
```

---

## 🗃️ База данных

Создается автоматически при запуске сервиса:

```sql
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    timestamp INTEGER NOT NULL,
    sentiment TEXT DEFAULT 'unknown',
    category TEXT DEFAULT 'другое'
);
```

Файловая база хранится как `complaints.db`.

---

## 🌐 Доступные API-эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/complaint` | Принять новую жалобу |
| GET | `/complaints` | Получить список жалоб за период с фильтром по статусу |
| POST | `/closeComplaint` | Закрыть жалобу по ID |

---

## 📝 Модели запросов и ответов

### `POST /complaint`

```json
{
  "text": "Не могу войти в аккаунт"
}
```

### Ответ:

```json
{
  "id": 1,
  "status": "open",
  "sentiment": "negative",
  "category": "техническая"
}
```

### `GET /complaints`

```json
{
  "status": "open",
  "hours": 1
}
```

Возвращает массив записей:

```json
{
  "complaints": [
    {
      "id": 1,
      "text": "Не могу войти в аккаунт",
      "status": "open",
      "timestamp": 1719823456,
      "sentiment": "negative",
      "category": "техническая"
    }
  ]
}
```

### `POST /closeComplaint

```json
{
    "complaint_id": 13
}
```

Возвращает массив записей:

```json
{
  "message": "Жалоба с ID 13 успешно закрыта"
}
```