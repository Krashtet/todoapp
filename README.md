### Запуск rest-бэкенда
## Windows

```bash
cd D:\Python\todoapp
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Linux
```bash
# При запуске впервые
sudo apt update
sudo apt install python2.12-venv
# rm -rf .venv удалить папку .venv после неудачной попытки

# настройка скрин сессии (выходить с виртульного окружения не обязательно deactivate)
sudo apt update
sudo apt install screen
cd /opt/todoapp
screen -S todo_backend
source .venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# После запуска отсоединение от сессии Cntr+A(отпустить), затем D(detach)
# Проверка скрин сессий
screen -ls
# Подключиться к сессий
screen -r todo_backend

# Проверить что бэкенд в работе
curl http://localhost:8000   # {"detail":"Not Found"}


cd /opt/todoapp   # папка проекта
python3 -m venv .venv
source .venv/bin/activate
pip install -r requiremens.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Перевод скрин сессии на автоматический запуск .service
```bash

# 1. Рекурсивно меняем владельца всей папки проекта на www-data
sudo chown -R www-data:www-data /opt/todoapp
# Даем право на исполнение для папок (чтобы можно было в них зайти)
sudo find /opt/todoapp -type d -exec chmod 755 {} \;
# Даем право на чтение для файлов
sudo find /opt/todoapp -type f -exec chmod 644 {} \;
# Особо даем права на исполнение для бинарников в venv (python, uvicorn)
sudo chmod +x /opt/todoapp/.venv/bin/python
sudo chmod +x /opt/todoapp/.venv/bin/uvicorn

# 2. Останавливаем screen-сессию
screen -r todo_backend
# Нажимаем Ctrl+C чтобы остановить сервер
# Вводим exit чтобы закрыть сессию screen
exit

# 3. добавим .service в системную папку
sudo cp /opt/todoapp/todoapp.service /etc/systemd/system/
# установим права
sudo chmod 644 /etc/systemd/system/todoapp.service
# перезагрузим конфигурацию
sudo systemctl daemon-reload

# Включаем автозапуск при загрузке системы
sudo systemctl enable todoapp.service
# Запускаем сервис
sudo systemctl start todoapp.service

# Проверяем статус — тут вы должны увидеть 'active (running)'
sudo systemctl status todoapp.service  # :q - Для выхода

# 4. Проверяем работу
curl http://localhost:8000
```

### Тестирование
## Windows
```bash
# пингование бэкенда
iwr http://127.0.0.1:8000/openapi.json -UseBasicParsing | select StatusCode
# открытие интерфейса созданной БД
start http://127.0.0.1:8000/docs

# TG user = 777; список незавершённых задач (создаст пользователя)
irm 'http://127.0.0.1:8000/api/tasks/777'

# добавить задачу
irm -Method Post -ContentType 'application/json' `
  -Body '{"tg_id":777,"title":"test task"}' `
  'http://127.0.0.1:8000/api/add'

# убедиться, что задача появилась и взять её id
$tasks = irm 'http://127.0.0.1:8000/api/tasks/777'
$tasks
$id = $tasks[0].id

# отметить завершённой
irm -Method Patch -ContentType 'application/json' `
  -Body (@{ id = $id } | ConvertTo-Json) `
  'http://127.0.0.1:8000/api/completed'

# список незавершённых должен опустеть
irm 'http://127.0.0.1:8000/api/tasks/777'

# счётчик завершённых должен быть > 0
irm 'http://127.0.0.1:8000/api/main/777'
```

## Linux
```bash
# Swagger
xdg-open http://127.0.0.1:8000/docs 2>/dev/null || true

# OpenAPI (ожидаем 200)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/openapi.json

# Список незавершённых задач (создаст пользователя 123 при первом вызове)
curl http://127.0.0.1:8000/api/tasks/123

# Добавить задачу
curl -X POST -H 'Content-Type: application/json' \
  -d '{"tg_id":123,"title":"test task"}' \
  http://127.0.0.1:8000/api/add

# Отметить завершённой (подставь реальный id)
curl -X PATCH -H 'Content-Type: application/json' \
  -d '{"id":1}' \
  http://127.0.0.1:8000/api/completed

# Счётчик завершённых
curl http://127.0.0.1:8000/api/main/123
```

### То же самое тестирование, только через интерфейс OpenAPI:

    GET /api/tasks/{tg_id} с tg_id=777
    POST /api/add с {"tg_id":777,"title":"test task"}
    GET /api/tasks/{tg_id} → возьми id
    PATCH /api/completed с {"id": <id>}
    GET /api/main/{tg_id}


### todoapp.service
# файл-сервис, для автомаческого поднятия фронта в случае падения
# НУЖНО разместить по пути /etc/systemd/system/todoapp.service