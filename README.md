# 🌊 Маяк

**Сервис мониторинга для малого бизнеса.** Следит за сайтами, кассами и другими сервисами и присылает **понятные алерты в Telegram**.

[![GitHub](https://img.shields.io/badge/GitHub-yahortsiukhai%2Fmayak-blue)](https://github.com/yahortsiukhai/mayak)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 📸 Скриншоты

### Дашборд — список мониторов
![Дашборд](docs/screenshots/dashboard.png)

### Детали монитора — история и статистика
![Монитор](docs/screenshots/monitor.png)

### Настройки — привязка Telegram
![Настройки](docs/screenshots/settings.png)

### Telegram-алерты
![Telegram](docs/screenshots/telegram.png)

---

## 💡 Идея

У малого бизнеса нет IT-специалиста. Когда сайт падает — узнают через 2 дня от злых клиентов. **«Маяк»** решает это: проверяет сервисы каждую минуту и говорит **человеческим языком**, что не так.

**Пример алерта:**
```
🔴 ВНИМАНИЕ
Сайт кофейни не работает!
🌐 URL: https://coffee-shop.ru
⚠️ Причина: Ошибка подключения

Что делать:
1. Проверьте хостинг
2. Не закончился ли домен
3. Не истёк ли SSL-сертификат
```

---

## 🎯 Возможности

- ✅ **Мониторинг сайтов** — проверка каждые 5 минут
- ✅ **Автоматические проверки** — через Celery (работает 24/7)
- ✅ **Telegram-алерты** — при падении и восстановлении
- ✅ **Привязка Telegram в 1 клик** — через бота (не надо вводить chat_id)
- ✅ **История проверок** — с детальной статистикой
- ✅ **Uptime %** — процент доступности
- ✅ **Красивый UI** — минимализм, на русском
- ✅ **Мониторинг сервиса** — Prometheus + Grafana

---

## 🛠️ Стек технологий

### Backend
- **Python 3.13** — язык
- **FastAPI** — асинхронный веб-фреймворк
- **PostgreSQL 16** — база данных
- **SQLAlchemy 2.0** — ORM
- **Alembic** — миграции
- **Pydantic 2** — валидация данных
- **JWT + bcrypt** — аутентификация
- **Redis 7** — кэш и брокер

### Фоновые задачи
- **Celery 5.3** — очередь задач
- **Celery Beat** — планировщик

### Интеграции
- **Telegram Bot API** — алерты и автопривязка
- **HTTPX** — HTTP-клиент для проверок
- **Prometheus** — сбор метрик
- **Grafana** — дашборды

### Frontend
- **Jinja2** — шаблоны
- **HTMX** — интерактивность без JS
- **Tailwind CSS** — стили

### DevOps
- **Docker + Docker Compose** — контейнеризация
- **Git + GitHub** — версии
- **Linux (Ubuntu)** — среда

---

## 📁 Структура проекта

```
mayak/
├── app/                       # Код приложения
│   ├── main.py                # Точка входа FastAPI
│   ├── config.py              # Настройки (Pydantic)
│   ├── database.py            # Подключение к БД
│   ├── celery_app.py          # Конфиг Celery
│   ├── models/                # Модели SQLAlchemy
│   │   ├── user.py
│   │   ├── monitor.py
│   │   └── check.py
│   ├── schemas/               # Pydantic-схемы
│   ├── routers/               # API-эндпоинты + UI-страницы
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── monitors.py
│   │   └── pages.py           # UI (HTML)
│   ├── services/              # Бизнес-логика
│   │   ├── security.py        # JWT + bcrypt
│   │   ├── checker.py         # HTTP-проверка
│   │   ├── telegram.py        # Telegram Bot API
│   │   └── deps.py            # FastAPI-зависимости
│   ├── tasks/                 # Celery-задачи
│   │   ├── monitoring.py      # Проверки мониторов
│   │   ├── alerts.py          # Отправка алертов
│   │   └── telegram_poll.py   # Polling Telegram
│   ├── templates/             # Jinja2-шаблоны
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── dashboard.html
│   │   ├── monitor_detail.html
│   │   ├── settings.html
│   │   └── auth/
│   └── static/                # CSS, JS
├── alembic/                   # Миграции
├── monitoring/                # Конфиги Prometheus
├── docs/                      # Скриншоты, документация
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md
```

---

## 🚀 Запуск локально

### Требования
- **Python 3.13+**
- **Docker + Docker Compose**
- **Make** (опционально)
- **Ubuntu / WSL / macOS / Linux**

### Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yahortsiukhai/mayak.git
cd mayak

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Установить зависимости
make install  # или pip install -r requirements.txt

# 4. Скопировать .env
cp .env.example .env
# Отредактируй .env (см. ниже)

# 5. Поднять инфраструктуру (Postgres, Redis, Prometheus, Grafana)
make up

# 6. Применить миграции
alembic upgrade head

# 7. Запустить FastAPI
make run
```

Приложение: **http://localhost:8000**

### Настройка `.env`

**Обязательные переменные:**

```env
# Приложение
APP_NAME=Маяк
SECRET_KEY=change-me-in-production-use-random-64-chars

# База данных
DATABASE_URL=postgresql+psycopg://mayak:mayak@localhost:5432/mayak

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=change-me-in-production-use-random-64-chars

# Telegram (получить у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_CHAT_ID=your_chat_id
```

### Запуск Celery (фоновые задачи)

**Терминал 2:**
```bash
make worker
```

**Терминал 3:**
```bash
make beat
```

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    ИНФРАСТРУКТУРА                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │Postgres  │  │  Redis   │  │Prometheus│  │ Grafana  ││
│  │  :5432   │  │  :6379   │  │  :9090   │  │  :3000   ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐         ┌─────────────────┐        │
│  │  FastAPI       │◀────────│  Celery Worker  │        │
│  │  :8000         │         │                 │        │
│  │  /metrics      │         │  + Beat         │        │
│  └────────────────┘         └─────────────────┘        │
│         ▲                            ▲                  │
│         │                            │                  │
│  ┌──────┴───────┐            ┌───────┴────────┐        │
│  │  Браузер     │            │  Telegram Bot  │        │
│  │  (UI)        │            │  API           │        │
│  └──────────────┘            └────────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Как работает:**

1. **Celery Beat** — каждые 5 минут запускает `check_all_monitors`
2. **Celery Worker** — берёт задачу → проверяет URL через HTTPX → сохраняет результат
3. **При падении** — отправляет **Telegram-алерт**
4. **При восстановлении** — отправляет **сообщение об успехе**
5. **Prometheus** — собирает метрики с FastAPI каждые 15 секунд
6. **Grafana** — визуализирует метрики

---

## 🔒 Безопасность

- ✅ **Пароли** — хэшируются **bcrypt**
- ✅ **JWT-токены** — для API и UI (cookie httpOnly)
- ✅ **Привязка Telegram** — через **одноразовый токен** (24 байта, urlsafe)
- ✅ **Изоляция данных** — юзер видит **только свои** мониторы
- ✅ **`.env`** — не коммитится в Git

---

## 📊 Мониторинг

**Prometheus:** http://localhost:9090
- Метрики FastAPI: `http_requests_total`, `http_request_duration_seconds`
- Targets: `prometheus`, `mayak-api`

**Grafana:** http://localhost:3000 (admin/admin)
- Дашборд **«Маяк»** — RPS, время ответа, ошибки

---

## 🗺️ Roadmap

- [x] **MVP** — мониторинг сайтов + Telegram-алерты
- [x] **UI** — дашборд, страница монитора, настройки
- [x] **Автопривязка Telegram** — через бота
- [x] **Мониторинг** — Prometheus + Grafana
- [ ] **Платежи** — ЮKassa / Tinkoff
- [ ] **Деплой** — на VPS с HTTPS
- [ ] **CI/CD** — GitHub Actions
- [ ] **Дополнительные типы проверок** — SQL, TCP, SSL
- [ ] **Мобильное приложение**

---

## 📄 Лицензия

MIT — свободно используйте, модифицируйте, распространяйте.

---

## 👤 Автор

**Егор Тюхай** — [@yahortsiukhai](https://github.com/yahortsiukhai)

Проект делается в рамках изучения DevOps и как реальный продукт для малого бизнеса.

**Стек:** Python, FastAPI, PostgreSQL, Celery, Docker, Prometheus, Grafana.

---

⭐ Если проект полезен — поставь **звезду** на GitHub!