from celery.schedules import crontab
from .tasks import remind_upcoming_events, weekly_points_summary

CELERY_BEAT_SCHEDULE = {
    'remind-upcoming-events-every-morning': {
        'task': 'notifications.tasks.remind_upcoming_events',
        'schedule': crontab(hour=8, minute=0),
    },
    'weekly-points-summary-every-monday': {
        'task': 'notifications.tasks.weekly_points_summary',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}
