from fastapi import FastAPI
from fastapi.responses import JSONResponse
import socket
import platform
import psutil
import time
import requests
from datetime import datetime
from typing import Dict, Any

app = FastAPI(
    title="Host Info API",
    description="API для получения информации о хосте и проверки работоспособности",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Главная страница"""
    return {
        "message": "Host Info API",
        "endpoints": {
            "/health": "Проверка работоспособности",
            "/info": "Информация о хосте",
            "/ping": "Проверка доступности внешних ресурсов"
        }
    }


@app.get("/health")
async def health_check():
    """Health check эндпоинт для проверки работоспособности"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "host-info-api"
    }


@app.get("/info")
async def get_host_info():
    """Получить информацию о хосте"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Получаем все IP адреса
        ip_addresses = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_addresses.append({
                        "interface": interface,
                        "ip": addr.address,
                        "netmask": addr.netmask
                    })
        
        # Системная информация
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_hours = uptime_seconds / 3600
        
        info: Dict[str, Any] = {
            "hostname": hostname,
            "local_ip": local_ip,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "network": {
                "ip_addresses": ip_addresses
            },
            "system": {
                "boot_time": boot_time.isoformat(),
                "uptime_hours": round(uptime_hours, 2),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "memory_used_percent": psutil.virtual_memory().percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(content=info)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "timestamp": datetime.utcnow().isoformat()}
        )


@app.get("/ping")
async def ping_check():
    """Проверка доступности внешних ресурсов"""
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Список ресурсов для проверки
    test_urls = [
        {"name": "google_dns", "url": "https://8.8.8.8", "timeout": 3},
        {"name": "google", "url": "https://www.google.com", "timeout": 5},
        {"name": "cloudflare_dns", "url": "https://1.1.1.1", "timeout": 3},
    ]
    
    for test in test_urls:
        try:
            start_time = time.time()
            response = requests.get(test["url"], timeout=test["timeout"], allow_redirects=False)
            elapsed_time = round((time.time() - start_time) * 1000, 2)  # в миллисекундах
            
            results["checks"][test["name"]] = {
                "status": "success" if response.status_code < 500 else "failed",
                "status_code": response.status_code,
                "response_time_ms": elapsed_time,
                "url": test["url"]
            }
        except requests.exceptions.Timeout:
            results["checks"][test["name"]] = {
                "status": "timeout",
                "response_time_ms": None,
                "url": test["url"],
                "error": "Request timeout"
            }
        except requests.exceptions.RequestException as e:
            results["checks"][test["name"]] = {
                "status": "failed",
                "response_time_ms": None,
                "url": test["url"],
                "error": str(e)
            }
    
    # Общий статус
    all_success = all(
        check.get("status") == "success" 
        for check in results["checks"].values()
    )
    results["overall_status"] = "healthy" if all_success else "degraded"
    
    return JSONResponse(content=results)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

