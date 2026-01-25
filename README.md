# Host Info API

Простое FastAPI приложение для получения информации о хосте и проверки работоспособности интернета.

## Возможности

- **GET /** - Главная страница со списком эндпоинтов
- **GET /health** - Health check для проверки работоспособности сервиса
- **GET /info** - Детальная информация о хосте (hostname, IP, системная информация)
- **GET /ping** - Проверка доступности внешних ресурсов (Google, Cloudflare DNS)

## Установка и запуск

### Локальный запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
python main.py
```

Или через uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Запуск в Docker

1. Соберите образ:
```bash
docker build -t host-info-api .
```

2. Запустите контейнер:
```bash
docker run -d -p 8000:8000 --name host-info-api host-info-api
```

### Использование в Kubernetes

Создайте deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: host-info-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: host-info-api
  template:
    metadata:
      labels:
        app: host-info-api
    spec:
      containers:
      - name: host-info-api
        image: futuro135/host-info-api:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Использование

После запуска приложение будет доступно по адресу `http://localhost:8000`

- Документация API: `http://localhost:8000/docs`
- Альтернативная документация: `http://localhost:8000/redoc`

### Примеры запросов

```bash
# Health check
curl http://localhost:8000/health

# Информация о хосте
curl http://localhost:8000/info

# Проверка интернета
curl http://localhost:8000/ping
```

