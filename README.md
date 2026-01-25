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

#### Создание Service

После создания Deployment создайте Service для доступа к приложению:

**ClusterIP (внутренний доступ):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: host-info-api
spec:
  type: ClusterIP
  selector:
    app: host-info-api
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
```

**NodePort (доступ через порт на нодах):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: host-info-api
spec:
  type: NodePort
  selector:
    app: host-info-api
  ports:
  - port: 80
    targetPort: 8000
    nodePort: 30080
    protocol: TCP
```

После создания NodePort сервиса приложение будет доступно по адресу `http://<NODE_IP>:30080`, где `<NODE_IP>` - IP адрес любой ноды кластера.

**LoadBalancer (внешний доступ через балансировщик):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: host-info-api
spec:
  type: LoadBalancer
  selector:
    app: host-info-api
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
```

LoadBalancer автоматически создаст внешний IP адрес (если поддерживается вашим кластером). После создания проверьте внешний IP:

```bash
kubectl get svc host-info-api
```

#### Применение манифестов

```bash
# Создать Deployment
kubectl apply -f deployment.yaml

# Создать Service (выберите нужный тип)
kubectl apply -f service.yaml

# Проверить статус
kubectl get pods -l app=host-info-api
kubectl get svc host-info-api
```

#### Когда использовать ClusterIP, NodePort, LoadBalancer или Ingress?

**Сравнение типов доступа:**

| Тип | Доступ | Использование | Плюсы | Минусы |
|-----|--------|---------------|-------|--------|
| **ClusterIP** | Только внутри кластера | Внутренние сервисы, микросервисы | Безопасно, быстро | Нет внешнего доступа |
| **NodePort** | Внешний доступ через IP:порт | Разработка, тестирование | Просто, не требует дополнительных компонентов | Нужно знать IP ноды, неудобные порты |
| **LoadBalancer** | Внешний доступ через IP | Продакшн в облаке | Простой внешний доступ | Дорого (каждый Service = свой LoadBalancer), только в облаке |
| **Ingress** | Внешний доступ через домен | Продакшн, несколько сервисов | Один IP для многих сервисов, домены, SSL, маршрутизация | Требует Ingress Controller |

**Когда использовать ClusterIP:**

✅ **Используйте для:**
- Внутренних сервисов, которые не должны быть доступны извне
- Микросервисов, общающихся друг с другом внутри кластера
- Базового Service для Ingress (Ingress использует ClusterIP Service)

❌ **Не используйте для:**
- Внешнего доступа к приложению
- Публичных API

**Пример:** База данных, внутренний API, сервис очередей

---

**Когда использовать NodePort:**

✅ **Используйте для:**
- Разработки и тестирования
- Быстрого доступа без настройки Ingress
- Когда нужен прямой доступ по IP и порту
- Временного доступа к сервису

❌ **Не используйте для:**
- Продакшн окружения
- Когда нужны доменные имена
- Когда нужно много сервисов (каждый требует свой порт)

**Пример:** `http://192.168.1.100:30080` - доступ напрямую по IP и порту

---

**Когда использовать LoadBalancer:**

✅ **Используйте для:**
- Продакшн в облачных провайдерах (AWS, GCP, Azure)
- Когда нужен простой внешний доступ без настройки
- Когда нужен статический внешний IP
- Для критичных сервисов, которым нужен выделенный балансировщик

❌ **Не используйте для:**
- Локальных кластеров (Minikube, Kind, Docker Desktop)
- Когда нужно много сервисов (дорого)
- Когда нужна маршрутизация по доменам/путям

**Пример:** Публичный API, который должен быть доступен по статическому IP

---

**Когда использовать Ingress:**

✅ **Используйте для:**
- **Продакшн окружения** - стандартный способ доступа
- **Несколько сервисов** - один Ingress Controller для многих приложений
- **Доменные имена** - `api.example.com`, `app.example.com`
- **SSL/TLS сертификаты** - автоматическая настройка HTTPS
- **Маршрутизация по пути** - `/api`, `/app`, `/admin`
- **Логирование и мониторинг** - централизованное управление трафиком
- **Rate limiting и аутентификация** - дополнительные возможности

❌ **Не используйте для:**
- Простых тестовых окружений (проще NodePort)
- Когда нужен только один сервис без домена (можно LoadBalancer)
- Когда нет возможности установить Ingress Controller

**Примеры использования Ingress:**

```yaml
# Один Ingress для нескольких сервисов
rules:
- host: api.example.com
  http:
    paths:
    - path: /users
      backend:
        service:
          name: user-service
    - path: /orders
      backend:
        service:
          name: order-service

# Разные домены для разных сервисов
rules:
- host: api.example.com
  http:
    paths:
    - path: /
      backend:
        service:
          name: api-service
- host: app.example.com
  http:
    paths:
    - path: /
      backend:
        service:
          name: app-service
```

**Преимущества Ingress перед NodePort:**

1. **Один IP для всех сервисов** - не нужно открывать порты для каждого сервиса
2. **Доменные имена** - `api.example.com` вместо `192.168.1.100:30080`
3. **SSL/TLS** - автоматическая настройка HTTPS
4. **Маршрутизация** - разные пути ведут к разным сервисам
5. **Централизованное управление** - один Ingress Controller для всего кластера
6. **Дополнительные функции** - rate limiting, аутентификация, переписывание URL

**Преимущества Ingress перед LoadBalancer:**

1. **Экономия** - один LoadBalancer вместо множества
2. **Гибкость** - маршрутизация по доменам и путям
3. **Удобство** - централизованное управление

**Рекомендации:**

- **Разработка:** NodePort или Port Forward
- **Тестирование:** NodePort или Ingress
- **Продакшн:** Ingress (рекомендуется) или LoadBalancer для критичных сервисов
- **Внутренние сервисы:** ClusterIP

**Типичная архитектура:**

```
Internet
   ↓
Ingress Controller (LoadBalancer или NodePort)
   ↓
Ingress (правила маршрутизации)
   ↓
ClusterIP Services (внутренние сервисы)
   ↓
Pods (приложения)
```

#### Создание Ingress

Ingress позволяет маршрутизировать HTTP/HTTPS трафик в кластер. Для работы Ingress необходим Ingress Controller (например, nginx-ingress, traefik).

**Важно:** Сначала создайте Service типа ClusterIP (см. выше), так как Ingress использует Service для маршрутизации.

#### Установка Ingress Controller

Перед созданием Ingress необходимо установить Ingress Controller. Самый популярный вариант - **NGINX Ingress Controller**.

**Установка NGINX Ingress Controller:**

**Для стандартного Kubernetes кластера:**

```bash
# Установка через официальный манифест
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Или для более новой версии
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
```

**Для Minikube:**

```bash
# Включить Ingress addon
minikube addons enable ingress

# Проверить статус
kubectl get pods -n ingress-nginx
```

**Для Docker Desktop (Kubernetes):**

```bash
# Включить Ingress в настройках Docker Desktop
# Settings -> Kubernetes -> Enable ingress

# Или через kubectl
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

**Для Kind (Kubernetes in Docker):**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

**Проверка установки:**

```bash
# Проверить, что поды Ingress Controller запущены
kubectl get pods -n ingress-nginx

# Проверить Service Ingress Controller
kubectl get svc -n ingress-nginx

# Проверить IngressClass
kubectl get ingressclass

# Должен быть создан ingressclass с именем "nginx"
```

**Ожидаемый вывод:**

```bash
$ kubectl get pods -n ingress-nginx
NAME                                        READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-xxxxxxxxx-xxxxx    1/1     Running   0          2m

$ kubectl get ingressclass
NAME    CONTROLLER             PARAMETERS   AGE
nginx   k8s.io/ingress-nginx   <none>       2m
```

**Получение IP адреса Ingress Controller:**

IP адрес зависит от типа Service Ingress Controller:

```bash
# Проверить тип Service и его IP
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

**Как определить IP для hosts файла:**

- **LoadBalancer:** Используйте значение из колонки `EXTERNAL-IP`
- **NodePort:** Используйте IP адрес любой ноды кластера (`kubectl get nodes -o wide`)
- **Minikube:** Используйте `minikube ip` (обычно что-то вроде `192.168.49.2`)
- **Docker Desktop/Kind:** Обычно `127.0.0.1` или `localhost`

**Примеры команд:**

```bash
# Для Minikube
minikube ip

# Для NodePort - получить IP ноды
kubectl get nodes -o wide

# Для LoadBalancer - получить EXTERNAL-IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

**Альтернативные Ingress Controller:**

**Traefik:**
```bash
helm repo add traefik https://traefik.github.io/charts
helm install traefik traefik/traefik
```

**Kong:**
```bash
kubectl apply -f https://raw.githubusercontent.com/Kong/kubernetes-ingress-controller/main/deploy/single/all-in-one-dbless.yaml
```

**После установки Ingress Controller можно создавать Ingress ресурсы.**

**Базовый Ingress (HTTP):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-info-api
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: host-info-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: host-info-api
            port:
              number: 80
```

**Ingress с несколькими путями:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-info-api
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /host-info
        pathType: Prefix
        backend:
          service:
            name: host-info-api
            port:
              number: 80
```

**Ingress с TLS/HTTPS:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-info-api
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - host-info-api.example.com
    secretName: host-info-api-tls
  rules:
  - host: host-info-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: host-info-api
            port:
              number: 80
```

**Применение Ingress:**

```bash
# Создать Ingress
kubectl apply -f ingress.yaml

# Проверить статус
kubectl get ingress host-info-api

# Посмотреть детали
kubectl describe ingress host-info-api
```

**Проверка работы Ingress:**

После создания Ingress проверьте адрес:

```bash
# Получить внешний IP или адрес Ingress
kubectl get ingress host-info-api

# Если используется LoadBalancer, будет показан EXTERNAL-IP
# Если используется NodePort, используйте IP ноды кластера
```

**Настройка DNS:**

Для работы с доменным именем добавьте A-запись в DNS:

```
host-info-api.example.com -> <EXTERNAL-IP>
```

Или для тестирования добавьте в `/etc/hosts` (Linux/Mac) или `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
<EXTERNAL-IP> host-info-api.example.com
```

**Проверка доступности:**

```bash
# Через доменное имя
curl http://host-info-api.example.com/health

# Или через IP
curl http://<EXTERNAL-IP>/health
```

**Пример для приложения psapp с хостом asus.loc:**

**Важно:** Сначала убедитесь, что у вас есть Service для приложения `psapp`.

Создайте файл `service-psapp.yaml` (если Service еще не создан):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: psapp
  namespace: default
spec:
  type: ClusterIP
  selector:
    app: psapp
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
```

Создайте файл `ingress-psapp.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: psapp
  namespace: default
spec:
  ingressClassName: nginx
  rules:
  - host: asus.loc
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: psapp
            port:
              number: 80
```

Примените:
```bash
# Сначала Service (если еще не создан)
kubectl apply -f service-psapp.yaml

# Затем Ingress
kubectl apply -f ingress-psapp.yaml

# Проверьте статус
kubectl get ingress psapp
```

**Диагностика проблем с Ingress:**

Если Ingress не работает, выполните пошаговую диагностику:

**1. Проверьте статус Ingress:**

```bash
# Проверить статус Ingress
kubectl get ingress psapp

# Посмотреть детали (важно - здесь будут ошибки)
kubectl describe ingress psapp
```

**2. Проверьте наличие Ingress Controller:**

```bash
# Проверить, установлен ли Ingress Controller
kubectl get pods -n ingress-nginx
# или
kubectl get pods -n kube-system | grep ingress

# Проверить IngressClass
kubectl get ingressclass
```

Если Ingress Controller отсутствует, установите его:
```bash
# Для nginx-ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

**3. Проверьте Service:**

```bash
# Убедитесь, что Service существует и имеет правильное имя
kubectl get svc psapp

# Проверьте, что Service указывает на правильные поды
kubectl get svc psapp -o yaml

# Проверьте endpoints Service
kubectl get endpoints psapp
```

Service должен быть типа ClusterIP и иметь endpoints (подключенные поды).

**4. Проверьте поды приложения:**

```bash
# Проверьте, что поды запущены
kubectl get pods -l app=psapp

# Проверьте логи пода
kubectl logs -l app=psapp

# Проверьте, что поды отвечают на запросы
kubectl exec -it <POD_NAME> -- curl http://localhost:8000/health
```

**5. Проверьте DNS/hosts файл:**

Для локального домена `asus.loc` добавьте запись в hosts файл.

**Сначала определите IP адрес Ingress Controller:**

```bash
# Проверьте Service Ingress Controller
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

**В зависимости от типа Service используйте:**

1. **Если Service типа LoadBalancer** - используйте EXTERNAL-IP:
   ```bash
   kubectl get svc -n ingress-nginx ingress-nginx-controller
   # Используйте значение из колонки EXTERNAL-IP
   ```

2. **Если Service типа NodePort** - используйте IP адрес любой ноды кластера:
   ```bash
   kubectl get nodes -o wide
   # Используйте INTERNAL-IP или EXTERNAL-IP любой ноды
   ```

3. **Для Minikube** - используйте IP адрес Minikube:
   ```bash
   minikube ip
   # Или
   minikube service -n ingress-nginx ingress-nginx-controller --url
   ```

4. **Для Docker Desktop / Kind** - обычно используется `127.0.0.1` или `localhost`:
   ```bash
   # Проверьте порт NodePort
   kubectl get svc -n ingress-nginx ingress-nginx-controller
   # Используйте 127.0.0.1:<NODEPORT>
   ```

**Добавьте запись в hosts файл:**

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
```
127.0.0.1 asus.loc
```
или
```
<IP_НОДЫ> asus.loc
```

**Linux/Mac:** `/etc/hosts`
```
127.0.0.1 asus.loc
```
или
```
<IP_НОДЫ> asus.loc
```

**Примеры:**

- **Minikube:** Если `minikube ip` вернул `192.168.49.2`, добавьте:
  ```
  192.168.49.2 asus.loc
  ```

- **Docker Desktop:** Обычно:
  ```
  127.0.0.1 asus.loc
  ```

- **Облачный кластер с LoadBalancer:** Используйте EXTERNAL-IP из `kubectl get svc -n ingress-nginx`

**6. Проверьте логи Ingress Controller:**

```bash
# Найти под Ingress Controller
kubectl get pods -n ingress-nginx

# Посмотреть логи
kubectl logs -n ingress-nginx <INGRESS_CONTROLLER_POD_NAME>
```

**7. Проверьте конфигурацию Ingress:**

```bash
# Посмотреть полную конфигурацию Ingress
kubectl get ingress psapp -o yaml

# Проверить, что ingressClassName правильный
kubectl get ingressclass
```

**8. Тестирование доступа:**

```bash
# Проверить доступность через curl с заголовком Host
curl -H "Host: asus.loc" http://<INGRESS_IP>/health

# Или через доменное имя (если настроен hosts)
curl http://asus.loc/health

# Проверить с подробным выводом
curl -v http://asus.loc/health
```

**9. Частые проблемы и решения:**

- **Проблема:** Ingress не имеет адреса (ADDRESS пустой)
  - **Решение:** Проверьте Ingress Controller и его Service

- **Проблема:** 502 Bad Gateway
  - **Решение:** Проверьте, что Service существует и поды работают

- **Проблема:** 404 Not Found
  - **Решение:** Проверьте путь (path) и pathType в Ingress

- **Проблема:** Неправильный ingressClassName
  - **Решение:** Проверьте доступные ingressClass: `kubectl get ingressclass`

- **Проблема:** Service не находит поды
  - **Решение:** Проверьте labels в Deployment и selector в Service

**10. Быстрая проверка всех компонентов:**

```bash
# Все в одной команде
echo "=== Pods ===" && kubectl get pods -l app=psapp && \
echo "=== Service ===" && kubectl get svc psapp && \
echo "=== Endpoints ===" && kubectl get endpoints psapp && \
echo "=== Ingress ===" && kubectl get ingress psapp && \
echo "=== Ingress Details ===" && kubectl describe ingress psapp
```

#### Port Forwarding (для локального доступа)

Port forwarding позволяет пробросить порт из пода в Kubernetes на ваш локальный компьютер. Это удобно для разработки и тестирования без создания Service.

**Проброс порта напрямую из Pod:**

```bash
# Найти имя пода
kubectl get pods -l app=host-info-api

# Пробросить порт (замените <POD_NAME> на имя вашего пода)
kubectl port-forward <POD_NAME> 8000:8000
```

**Проброс порта через Service:**

```bash
# Пробросить порт через Service
kubectl port-forward svc/host-info-api 8000:80
```

После выполнения команды приложение будет доступно на `http://localhost:8000` на вашем локальном компьютере.

**Проброс в фоновом режиме:**

```bash
# Запустить port-forward в фоне
kubectl port-forward svc/host-info-api 8000:80 &

# Остановить port-forward
# Найти процесс
ps aux | grep port-forward
# Или использовать
pkill -f "port-forward"
```

**Проброс на другой локальный порт:**

```bash
# Пробросить на порт 8080 вместо 8000
kubectl port-forward svc/host-info-api 8080:80
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

