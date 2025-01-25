"""Health check monitoring for system components."""

from typing import Dict, Any, Optional
import time
import psutil
from ..utils.metrics import record_metric, track_error
from ..utils.logger import logger

async def check_system_health() -> Dict[str, Any]:
    """Check overall system health metrics.
    
    Returns:
        Dictionary containing system health metrics
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        record_metric("system.health.cpu_percent", cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        record_metric("system.health.memory_percent", memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        record_metric("system.health.disk_percent", disk.percent)
        
        return {
            "status": "healthy" if all([
                cpu_percent < 90,
                memory.percent < 90,
                disk.percent < 90
            ]) else "degraded",
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
        }
    except Exception as e:
        track_error(
            error_type="health_check",
            error_message=str(e),
            additional_context={"component": "system"}
        )
        return {
            "status": "error",
            "error": str(e)
        }

async def check_component_health(
    component: str,
    check_func: callable,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """Check health of a specific system component.
    
    Args:
        component: Name of component to check
        check_func: Async function that performs the health check
        timeout: Maximum time to wait for check (seconds)
        
    Returns:
        Dictionary containing component health status
    """
    try:
        start_time = time.time()
        result = await check_func()
        duration = time.time() - start_time
        
        record_metric(
            f"health.{component}.duration",
            duration,
            tags={"component": component}
        )
        
        if duration > timeout:
            track_error(
                error_type="health_timeout",
                error_message=f"{component} health check timed out",
                additional_context={
                    "component": component,
                    "duration": duration,
                    "timeout": timeout
                }
            )
            
        return {
            "component": component,
            "status": "healthy" if result else "unhealthy",
            "response_time": duration
        }
        
    except Exception as e:
        track_error(
            error_type="health_check",
            error_message=str(e),
            additional_context={"component": component}
        )
        return {
            "component": component,
            "status": "error",
            "error": str(e)
        }