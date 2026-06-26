
# TeamFinder (Вариант 3)

Платформа для поиска команды для pet-проектов. Реализован функционал навыков проектов и фильтрации.

## Запуск проекта

### Требования
- Python 3.10+
- Docker Desktop (для PostgreSQL)

### Шаги для запуска

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Vmr396/team-finder-ad.git
   cd team-finder-ad
   python -m venv venv
2. Создайте и активируйте виртуальное окружение:

python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
или venv\Scripts\activate  # Windows cmd
3. Установите зависимости:
pip install -r requirements.txt
4. Запустите PostgreSQL в Docker:
docker compose up -d
5. Выполните миграции:
python manage.py migrate
6. Создайте суперпользователя:
python manage.py createsuperuser
7. Запустите сервер:
python manage.py runserver
8. Откройте сайт: http://127.0.0.1:8000

пароль суперпользоваеля
maria@yandex.ru
password
12@mail.ru
password