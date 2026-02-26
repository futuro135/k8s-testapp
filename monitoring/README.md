# Мониторинг: Grafana, Prometheus, Pyroscope (Helm)

Установка через Helm в namespace `monitoring`.

## Что ставится

| Компонент   | Чарт                     | Репозиторий |
|------------|---------------------------|-------------|
| Prometheus + Grafana | kube-prometheus-stack | prometheus-community |
| Pyroscope  | pyroscope                 | grafana     |

Вместе с kube-prometheus-stack также устанавливаются Alertmanager, node-exporter, kube-state-metrics и готовые дашборды.

## Быстрый старт

```bash
cd monitoring
chmod +x install.sh
./install.sh
```

Переменная окружения `MONITORING_NAMESPACE` задаёт namespace (по умолчанию `monitoring`).

## Доступ к UI

После установки можно пробросить порты:

```bash
# Grafana (логин admin, пароль в values-kube-prometheus-stack.yaml)
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80

# Prometheus
kubectl -n monitoring port-forward svc/kube-prometheus-stack-kube-prom-prometheus 9090:9090

# Pyroscope
kubectl -n monitoring port-forward svc/pyroscope 4040:4040
```

Открыть в браузере: http://localhost:3000 (Grafana), http://localhost:9090 (Prometheus), http://localhost:4040 (Pyroscope).

## Ручная установка

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl create namespace monitoring

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring -f values-kube-prometheus-stack.yaml --wait

helm upgrade --install pyroscope grafana/pyroscope \
  -n monitoring -f values-pyroscope.yaml --wait
```

## Кастомизация

- **values-kube-prometheus-stack.yaml** — Prometheus (retention, объём PVC), Grafana (пароль, persistence). Закомментированы примеры Ingress для Grafana.
- **values-pyroscope.yaml** — persistence, размер PVC. Закомментирован пример Ingress для Pyroscope.

Для продакшена обязательно смените `adminPassword` в values Grafana и при необходимости включите Ingress (раскомментируйте и поправьте hosts).
