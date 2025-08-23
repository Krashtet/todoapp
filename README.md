### Запуск rest-бэкенда
## Windows

```bash
cd D:\Python\todoapp
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Linux
```bash
cd /opt/todoapp   # папка проекта
python3 -m venv .venv
source .venv/bin/activate
pip install -r requiremens.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
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