"""
Prometheus metrics middleware for AI Printer
"""
import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests',
    ['method', 'endpoint']
)

AUDIO_PROCESSING_TIME = Histogram(
    'audio_processing_duration_seconds',
    'Audio processing duration in seconds',
    ['processing_type']
)

DOCUMENT_GENERATION_TIME = Histogram(
    'document_generation_duration_seconds',
    'Document generation duration in seconds',
    ['document_type']
)

TRANSCRIPTION_ACCURACY = Histogram(
    'transcription_accuracy_score',
    'Transcription accuracy score',
    ['model']
)

CELERY_TASK_COUNT = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'state']
)

CELERY_TASK_DURATION = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name']
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

USER_SESSIONS = Gauge(
    'user_sessions_active',
    'Number of active user sessions'
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint']
)

GOOGLE_DRIVE_OPERATIONS = Counter(
    'google_drive_operations_total',
    'Total Google Drive operations',
    ['operation', 'result']
)

OPENAI_API_CALLS = Counter(
    'openai_api_calls_total',
    'Total OpenAI API calls',
    ['model', 'operation', 'result']
)

OPENAI_API_DURATION = Histogram(
    'openai_api_duration_seconds',
    'OpenAI API call duration in seconds',
    ['model', 'operation']
)

AUDIO_FILE_SIZE = Histogram(
    'audio_file_size_bytes',
    'Audio file size in bytes',
    buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600]  # 1KB to 100MB
)

DOCUMENT_LENGTH = Histogram(
    'document_length_words',
    'Document length in words',
    ['document_type'],
    buckets=[10, 50, 100, 500, 1000, 5000, 10000]
)


class PrometheusMiddleware:
    """Middleware to collect Prometheus metrics"""
    
    def __init__(self, app_name: str = "ai_printer"):
        self.app_name = app_name
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics collection for the metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        endpoint = self._get_endpoint_name(request)
        
        # Track active requests
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            API_ERRORS.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            raise
        
        finally:
            # Decrease active requests
            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
    
    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name from request"""
        path = request.url.path
        
        # Normalize paths to avoid high cardinality
        if path.startswith("/api/"):
            path_parts = path.split("/")
            if len(path_parts) >= 3:
                # Keep first two parts after /api/
                return f"/api/{path_parts[2]}"
        
        return path


class MetricsCollector:
    """Utility class for collecting custom metrics"""
    
    @staticmethod
    def record_audio_processing(processing_type: str, duration: float):
        """Record audio processing metrics"""
        AUDIO_PROCESSING_TIME.labels(processing_type=processing_type).observe(duration)
    
    @staticmethod
    def record_document_generation(document_type: str, duration: float, word_count: int):
        """Record document generation metrics"""
        DOCUMENT_GENERATION_TIME.labels(document_type=document_type).observe(duration)
        DOCUMENT_LENGTH.labels(document_type=document_type).observe(word_count)
    
    @staticmethod
    def record_transcription_accuracy(model: str, accuracy_score: float):
        """Record transcription accuracy metrics"""
        TRANSCRIPTION_ACCURACY.labels(model=model).observe(accuracy_score)
    
    @staticmethod
    def record_celery_task(task_name: str, state: str, duration: float = None):
        """Record Celery task metrics"""
        CELERY_TASK_COUNT.labels(task_name=task_name, state=state).inc()
        
        if duration is not None:
            CELERY_TASK_DURATION.labels(task_name=task_name).observe(duration)
    
    @staticmethod
    def record_cache_operation(operation: str, result: str):
        """Record cache operation metrics"""
        CACHE_OPERATIONS.labels(operation=operation, result=result).inc()
    
    @staticmethod
    def record_google_drive_operation(operation: str, result: str):
        """Record Google Drive operation metrics"""
        GOOGLE_DRIVE_OPERATIONS.labels(operation=operation, result=result).inc()
    
    @staticmethod
    def record_openai_api_call(model: str, operation: str, result: str, duration: float):
        """Record OpenAI API call metrics"""
        OPENAI_API_CALLS.labels(model=model, operation=operation, result=result).inc()
        OPENAI_API_DURATION.labels(model=model, operation=operation).observe(duration)
    
    @staticmethod
    def record_audio_file_size(size_bytes: int):
        """Record audio file size metrics"""
        AUDIO_FILE_SIZE.observe(size_bytes)
    
    @staticmethod
    def update_database_connections(count: int):
        """Update database connection count"""
        DATABASE_CONNECTIONS.set(count)
    
    @staticmethod
    def update_user_sessions(count: int):
        """Update active user session count"""
        USER_SESSIONS.set(count)


async def metrics_endpoint() -> Response:
    """Endpoint to expose Prometheus metrics"""
    try:
        metrics_data = generate_latest()
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return Response(
            content="# Failed to generate metrics\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )


# Custom metrics for application-specific monitoring
class ApplicationMetrics:
    """Application-specific metrics collector"""
    
    def __init__(self):
        self.user_activity = Counter(
            'user_activity_total',
            'Total user activities',
            ['user_id', 'activity_type']
        )
        
        self.subscription_metrics = Gauge(
            'subscription_users_total',
            'Total users by subscription tier',
            ['tier']
        )
        
        self.storage_usage = Gauge(
            'storage_usage_bytes',
            'Storage usage in bytes',
            ['storage_type']
        )
        
        self.api_quota_usage = Gauge(
            'api_quota_usage_ratio',
            'API quota usage ratio (0-1)',
            ['service', 'user_tier']
        )
    
    def record_user_activity(self, user_id: str, activity_type: str):
        """Record user activity"""
        self.user_activity.labels(user_id=user_id, activity_type=activity_type).inc()
    
    def update_subscription_metrics(self, tier_counts: dict):
        """Update subscription tier metrics"""
        for tier, count in tier_counts.items():
            self.subscription_metrics.labels(tier=tier).set(count)
    
    def update_storage_usage(self, storage_type: str, usage_bytes: int):
        """Update storage usage metrics"""
        self.storage_usage.labels(storage_type=storage_type).set(usage_bytes)
    
    def update_api_quota_usage(self, service: str, user_tier: str, usage_ratio: float):
        """Update API quota usage metrics"""
        self.api_quota_usage.labels(service=service, user_tier=user_tier).set(usage_ratio)


# Global metrics collector instance
app_metrics = ApplicationMetrics()