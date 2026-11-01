# ⌨️ Typing Trainer API

Веб-приложение для практики слепого ввода свободного текста на английском и русском языках.

Проект реализован на **FastAPI** и подходит для учебного портфолио: JSON API, JWT-авторизация, база данных, миграции, импорт текстов из файлов, Jinja2-интерфейс и автоматические тесты.

## Возможности

- Регистрация и вход пользователей
- JWT-авторизация через `Authorization: Bearer <token>`
- Личный профиль пользователя
- Практика свободного текста на английском (`en`) и русском (`ru`)
- Случайный выбор текста с учётом языка и сложности
- Расчёт WPM, точности, правильных, неверных и пропущенных символов
- История тренировок
- Статистика по выбранному языку
- Добавление текстов через API
- Импорт текстов из `.txt` и `.md` файлов
- Jinja2 HTML-интерфейс
- Alembic-миграции
- Тесты API через pytest и TestClient

## Стек

| Слой | Технология |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite, SQLModel |
| Migrations | Alembic |
| Authentication | OAuth2 Password Flow, JWT, bcrypt |
| Templates | Jinja2 |
| Frontend | HTML, CSS, vanilla JavaScript |
| Testing | pytest, FastAPI TestClient |

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone [https://github.com/your-username/typing-trainer.git](https://github.com/your-username/typing-trainer.git)
cd typing-trainer
```

### 2. Создайте виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
```

Для Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

```bash
cp .env.example .env
```

Пример `.env`:

```env
SECRET_KEY=replace-this-with-a-long-random-secret
DATABASE_URL=sqlite:///./typing_trainer.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Никогда не публикуйте реальный `SECRET_KEY` и файл `.env` в Git.

### 5. Примените миграции

```bash
alembic upgrade head
```

### 6. Запустите сервер

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресам:

- Интерфейс: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Структура проекта

```text
typing-trainer/
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── dependencies.py
│   ├── services.py
│   ├── text_import.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── pages.py
│   │   ├── sessions.py
│   │   ├── texts.py
│   │   └── users.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── practice.html
│       ├── profile.html
│       │── login.html
│       │── register.html
│       └── texts/
│           └── import.html
├── static/
│   ├── css/style.css
│   └── js/practice.js
├── uploads/
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

## Основные страницы

| Страница | URL | Описание |
|---|---|---|
| Главная | `/` | Описание проекта и навигация |
| Регистрация | `/auth/register` | Создание аккаунта |
| Вход | `/auth/login` | Получение JWT |
| Практика | `/practice` | Тренажёр слепого ввода |
| Импорт текстов | `/texts/import` | Загрузка `.txt` или `.md` |
| Профиль | `/profile` | Статистика и история тренировок |

## API

Интерактивная документация доступна в Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Основные эндпоинты

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| `GET` | `/health` | Нет | Проверка работоспособности |
| `POST` | `/auth/register` | Нет | Регистрация пользователя |
| `POST` | `/auth/token` | Нет | Получение JWT access token |
| `GET` | `/auth/me` | Да | Данные текущего пользователя |
| `GET` | `/users/me` | Да | Профиль пользователя |
| `GET` | `/users/me/sessions` | Да | История тренировок |
| `GET` | `/users/me/stats` | Да | Статистика по языку |
| `GET` | `/texts/random` | Да | Случайный текст для практики |
| `POST` | `/texts/` | Да | Добавление текста |
| `POST` | `/texts/import` | Да | Импорт текстов из файла |
| `POST` | `/sessions/` | Да | Сохранение результата тренировки |
| `GET` | `/sessions/` | Да | Список тренировок |
| `GET` | `/sessions/stats` | Да | Статистика тренировок |

## Авторизация

Проект использует OAuth2 Password Flow с JWT.

1. Пользователь регистрируется через `POST /auth/register`.
2. Получает access token через `POST /auth/token`.
3. Отправляет токен в заголовке:

```http
Authorization: Bearer <access_token>
```

4. Сервер проверяет подпись JWT, срок действия и существование пользователя.
5. Пароли хранятся только в виде bcrypt-хешей.

Пример запроса токена:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=developer&password=supersecret123"
```

Пример защищённого запроса:

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

## Работа с текстами

### Добавить текст

```bash
curl -X POST http://127.0.0.1:8000/texts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "language": "en",
    "content": "The quick brown fox jumps over the lazy dog near the river.",
    "difficulty": 1
  }'
```

### Получить случайный текст

```bash
curl "http://127.0.0.1:8000/texts/random?language=en&difficulty=1" \
  -H "Authorization: Bearer <access_token>"
```

### Импортировать тексты из файла

```bash
curl -X POST "http://127.0.0.1:8000/texts/import?language=en&difficulty=1" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@english.txt"
```

Поддерживаются:

- `.txt`
- `.md`
- кодировка UTF-8
- максимальный размер файла: 2 МБ

Каждая непустая строка файла становится отдельным текстом для практики.

Пример `english.txt`:

```text
The quick brown fox jumps over the lazy dog near the quiet river.
Typing regularly improves muscle memory and helps you focus on the screen.
Consistent practice matters more than a single long training session.
```

## Сохранение результата тренировки

```bash
curl -X POST http://127.0.0.1:8000/sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "text_id": 1,
    "typed_text": "The quick brown fox jumps over the lazy dog.",
    "duration_seconds": 24.5
  }'
```

Сервер самостоятельно рассчитывает:

- WPM;
- точность;
- количество правильных символов;
- количество неправильных символов;
- количество пропущенных символов.

Поэтому клиент не может отправить поддельные значения метрик.

## Метрики тренировки

### WPM

WPM — words per minute, слов в минуту.

\[
\text{WPM} = \frac{\text{количество символов} / 5}{\text{минуты}}
\]

Пять символов условно считаются одним словом.

### Точность

\[
\text{Accuracy} =
\frac{\text{правильные символы}}
{\text{правильные} + \text{неправильные} + \text{пропущенные}}
\times 100
\]

## Миграции

Создать новую миграцию после изменения моделей:

```bash
alembic revision --autogenerate -m "describe your change"
```

Применить миграции:

```bash
alembic upgrade head
```

Откатить последнюю миграцию:

```bash
alembic downgrade -1
```

Перед применением autogenerated-миграции рекомендуется просмотреть сгенерированный файл в `alembic/versions/`.


Тесты используют отдельную in-memory SQLite-базу и не затрагивают файл основной базы данных.

## Безопасность

- Пароли хранятся только в виде bcrypt-хешей.
- JWT подписывается секретным ключом и имеет ограниченный срок жизни.
- Доступ к тренировкам, текстам и статистике требует валидного токена.
- Файлы ограничены по расширению, размеру и кодировке.
- Метрики тренировок рассчитываются на сервере.
- `.env`, база данных и загруженные файлы исключены из Git.
