#!/bin/bash

echo "=== Диагностика сервиса psapp ==="
echo ""

echo "1. Проверка доступности кластера:"
kubectl cluster-info 2>&1 | head -1
echo ""

echo "2. Проверка статуса сервиса:"
kubectl get svc psapp
echo ""

echo "3. Проверка подов:"
kubectl get pods -l app=psapp
echo ""

echo "4. Проверка endpoints (должны быть IP адреса подов):"
kubectl get endpoints psapp
echo ""

echo "5. Детали сервиса:"
kubectl describe svc psapp | grep -A 10 "Endpoints:"
echo ""

echo "6. Логи пода (если есть):"
POD_NAME=$(kubectl get pods -l app=psapp -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$POD_NAME" ]; then
    echo "Проверяю под: $POD_NAME"
    kubectl logs $POD_NAME --tail=10
else
    echo "Поды не найдены!"
fi
echo ""

echo "7. Попытка подключения:"
echo "Проверяю localhost:30011..."
curl -v http://localhost:30011/ 2>&1 | head -20
echo ""

echo "=== Рекомендации ==="
echo "Если endpoints пустые - поды не готовы или селектор не совпадает"
echo "Если кластер недоступен - запустите Docker Desktop или minikube"
echo "Для minikube используйте: minikube service psapp"
echo "Для Docker Desktop: проверьте, что Kubernetes включен в настройках"
