from django.db import models
from django.contrib.auth.models import User


class ClubMember(models.Model):
    STATUS_CHOICES = [
        ('PENDING',  'Chờ duyệt'),
        ('APPROVED', 'Thành viên'),
        ('REJECTED', 'Từ chối'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='club_member')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    motivation = models.TextField(blank=True)
    total_points = models.IntegerField(default=0)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_members'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'club_members'
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} ({self.get_status_display()})"


class PointLog(models.Model):
    REASON_CHOICES = [
        ('CHECKIN', 'Điểm danh sinh hoạt'),
        ('MANUAL',  'Admin điều chỉnh'),
    ]
    member = models.ForeignKey(ClubMember, on_delete=models.CASCADE, related_name='point_logs')
    points = models.IntegerField()
    reason = models.CharField(max_length=10, choices=REASON_CHOICES)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'point_logs'
        ordering = ['-created_at']