"""
Celery configuration and app creation
"""
from celery import Celery
from ..config import settings
import os

def make_celery():
    """Create and configure Celery app"""
    celery = Celery(
        "ai_printer",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            'app.celery_app.tasks.audio_processing',
            'app.celery_app.tasks.document_generation',
            'app.celery_app.tasks.google_drive',
            'app.celery_app.tasks.analytics',
        ]
    )

    # Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task routing
        task_routes={
            'app.celery_app.tasks.audio_processing.*': {'queue': 'audio_processing'},
            'app.celery_app.tasks.document_generation.*': {'queue': 'document_generation'},
            'app.celery_app.tasks.google_drive.*': {'queue': 'google_drive'},
            'app.celery_app.tasks.analytics.*': {'queue': 'analytics'},
        },
        
        # Worker configuration
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=100,
        
        # Result backend settings
        result_expires=3600,  # 1 hour
        
        # Task execution settings
        task_time_limit=300,  # 5 minutes
        task_soft_time_limit=240,  # 4 minutes
        
        # Retry settings
        task_default_retry_delay=60,  # 1 minute
        task_max_retries=3,
        
        # Beat schedule for periodic tasks
        beat_schedule={
            'cleanup-old-files': {
                'task': 'app.celery_app.tasks.analytics.cleanup_old_files',
                'schedule': 86400.0,  # Daily
            },
            'generate-usage-reports': {
                'task': 'app.celery_app.tasks.analytics.generate_daily_usage_report',
                'schedule': 86400.0,  # Daily
            },
        },
    )

    return celery

# Create celery app instance
celery_app = make_celery()