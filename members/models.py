from django.db import models
from django.contrib.auth.models import User



# --- CLB ---
class Club(models.Model):
    CATEGORY_CHOICES = [
        ("SACH", "Sách"),
        ("AM_NHAC", "Âm nhạc"),
        ("THE_THAO", "Thể thao"),
        ("IT", "CNTT"),
        ("KHAC", "Khác"),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    logo = models.ImageField(upload_to="club_logos/", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_clubs")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "clubs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# --- Thành viên CLB ---
class ClubMember(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Chờ duyệt"),
        ("APPROVED", "Thành viên"),
        ("REJECTED", "Từ chối"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="club_member")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="members", null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    motivation = models.TextField(blank=True)
    total_points = models.IntegerField(default=0)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_members"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "club_members"
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.get_status_display()})"


# --- Điểm thành viên ---
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


# --- Chat CLB ---
class ChatRoom(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE, related_name="chat_room")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_rooms"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Phòng chat {self.club.name}"


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "messages"
        ordering = ["sent_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"