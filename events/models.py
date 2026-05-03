import uuid
from django.db import models
from django.contrib.auth.models import User
from members.models import ClubMember, PointLog


class ClubEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    points_reward = models.IntegerField(default=10)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    checkin_window_minutes = models.IntegerField(default=60)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'club_events'
        ordering = ['-event_date']

    def __str__(self):
        return self.title


class EventCheckin(models.Model):
    event = models.ForeignKey(ClubEvent, on_delete=models.CASCADE, related_name='checkins')
    member = models.ForeignKey(ClubMember, on_delete=models.CASCADE, related_name='checkins')
    checked_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_checkins'
        unique_together = [['event', 'member']]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.member.total_points += self.event.points_reward
            self.member.save(update_fields=['total_points'])
            PointLog.objects.create(
                member=self.member,
                points=self.event.points_reward,
                reason='CHECKIN',
                note=f"Điểm danh: {self.event.title}",
            )