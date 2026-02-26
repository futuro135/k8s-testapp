#!/usr/bin/env bash
# Установка Grafana, Prometheus и Pyroscope через Helm в namespace monitoring

set -e
NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"

echo "=== Добавление Helm-репозиториев ==="
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

echo "=== Создание namespace $NAMESPACE ==="
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Установка kube-prometheus-stack (Prometheus + Grafana) ==="
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n "$NAMESPACE" \
  -f "$SCRIPT_DIR/values-kube-prometheus-stack.yaml" \
  --wait

echo "=== Установка Pyroscope ==="
helm upgrade --install pyroscope grafana/pyroscope \
  -n "$NAMESPACE" \
  -f "$SCRIPT_DIR/values-pyroscope.yaml" \
  --wait

echo ""
echo "=== Готово. Проверка подов ==="
kubectl -n "$NAMESPACE" get pods

echo ""
echo "Локальный доступ (port-forward):"
echo "  Grafana:    kubectl -n $NAMESPACE port-forward svc/kube-prometheus-stack-grafana 3000:80"
echo "  Prometheus: kubectl -n $NAMESPACE port-forward svc/kube-prometheus-stack-kube-prom-prometheus 9090:9090"
echo "  Pyroscope:  kubectl -n $NAMESPACE port-forward svc/pyroscope 4040:4040"
echo ""
echo "Grafana логин по умолчанию: admin / admin (см. values-kube-prometheus-stack.yaml)"
