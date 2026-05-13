from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from events.models import ClubEvent
from members.models import ClubMember
from django.conf import settings
from datetime import timedelta

@shared_task
def remind_upcoming_events():
    now = timezone.now()
    soon = now + timedelta(hours=24)
    events = ClubEvent.objects.filter(start_time__gte=now, start_time__lte=soon)
    for event in events:
        members = ClubMember.objects.filter(club=event.club, status='APPROVED').select_related('user')
        for m in members:
            if m.user.email:
                send_mail(
                    subject=f"Nhắc nhở sự kiện: {event.name}",
                    message=f"CLB {event.club.name} sẽ tổ chức sự kiện '{event.name}' vào {event.start_time:%d/%m/%Y %H:%M}. Đừng quên tham gia!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[m.user.email],
                    fail_silently=True,
                )

@shared_task
def weekly_points_summary():
    now = timezone.now()
    last_week = now - timedelta(days=7)
    clubs = ClubMember.objects.values_list('club', flat=True).distinct()
    for club_id in clubs:
        members = ClubMember.objects.filter(club_id=club_id, status='APPROVED').select_related('user')
        ranked = sorted(members, key=lambda m: m.total_points, reverse=True)
        for idx, m in enumerate(ranked, 1):
            week_points = m.point_logs.filter(created_at__gte=last_week).aggregate(total=Sum('points'))['total'] or 0
            if m.user.email:
                send_mail(
                    subject=f"Báo cáo điểm tuần CLB {m.club.name}",
                    message=f"Chào {m.user.get_full_name() or m.user.username},\n\nĐiểm tuần qua: {week_points}\nTổng điểm: {m.total_points}\nXếp hạng: {idx}/{len(ranked)}\n\nHãy tiếp tục tham gia tích cực nhé!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[m.user.email],
                    fail_silently=True,
                )
