# 🦷 Stomatology - Система управления стоматологией

## Быстрый старт

### 1. Клонирование и запуск
Клонируем репозиторий и переходим в директорию:
```bash
git clone https://github.com/RomaKlyukin/stomatology-app
cd stomatology-app
```

Запускаем проект (собираются образы и запускается все сервисы):
```bash
docker compose up --build -d
```

### 2. Настройка базы данных
Применяем миграции (создается структура БД):
```bash
docker compose exec stomatology python manage.py migrate
```

Загружаем тестовые данные
```bash
docker compose exec stomatology python manage.py loaddata db.json
```
