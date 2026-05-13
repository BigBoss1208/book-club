from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import ClubMember, PointLog, Club

# Bảng xếp hạng thành viên CLB
from django.db.models import Sum
from datetime import datetime, timedelta

@login_required
def leaderboard_view(request):
    club_id = request.GET.get('club_id')
    period = request.GET.get('period', 'month')
    now = timezone.now()
    if period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'semester':
        # Giả sử học kỳ 1: 1/1-30/6, học kỳ 2: 1/7-31/12
        if now.month <= 6:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now.replace(month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = None

    members = ClubMember.objects.filter(status='APPROVED')
    club = None
    if club_id:
        members = members.filter(club_id=club_id)
        club = Club.objects.filter(id=club_id).first()

    if start:
        # Tính tổng điểm theo kỳ
        members = members.annotate(
            period_points=Sum('point_logs__points', filter=models.Q(point_logs__created_at__gte=start))
        ).order_by('-period_points')
    else:
        members = members.order_by('-total_points')

    members = members[:10]
    clubs = Club.objects.filter(is_active=True)
    max_points = 0
    if members:
        if start:
            max_points = max([getattr(m, 'period_points', 0) or 0 for m in members])
        else:
            max_points = max([m.total_points for m in members])
    context = {
        'members': members,
        'period': period,
        'club': club,
        'clubs': clubs,
        'max_points': max_points or 1,
    }
    return render(request, 'leaderboard/leaderboard.html', context)

is_admin = lambda u: u.is_staff


@login_required
def join_club_view(request):
    existing = ClubMember.objects.filter(user=request.user).first()
    if existing and existing.status in ('APPROVED', 'PENDING'):
        return redirect('members:my_membership')

    if request.method == 'POST':
        motivation = request.POST.get('motivation', '').strip()
        if existing and existing.status == 'REJECTED':
            existing.status = 'PENDING'
            existing.motivation = motivation
            existing.reject_reason = ''
            existing.reviewed_by = None
            existing.reviewed_at = None
            existing.save()
        else:
            ClubMember.objects.create(user=request.user, motivation=motivation)
        messages.success(request, 'Đã gửi đơn! Vui lòng chờ admin duyệt.')
        return redirect('members:my_membership')

    return render(request, 'members/join_club.html', {'existing': existing})


@login_required
def my_membership_view(request):
    member = ClubMember.objects.filter(user=request.user).first()
    point_logs = member.point_logs.all()[:30] if member else []
    return render(request, 'members/my_membership.html', {
        'member': member,
        'point_logs': point_logs,
    })


@login_required
@user_passes_test(is_admin)
def admin_member_list_view(request):
    members = ClubMember.objects.filter(status='APPROVED').select_related('user')
    search = request.GET.get('search', '').strip()
    if search:
        members = members.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )
    sort = request.GET.get('sort', '-total_points')
    if sort in ['-total_points', 'total_points', '-joined_at', 'joined_at']:
        members = members.order_by(sort)
    return render(request, 'members/admin_member_list.html', {
        'members': members, 'search': search, 'sort': sort,
    })


@login_required
@user_passes_test(is_admin)
def admin_pending_view(request):
    pending = ClubMember.objects.filter(status='PENDING').select_related('user')
    return render(request, 'members/admin_pending.html', {'pending': pending})


@login_required
@user_passes_test(is_admin)
def approve_member_view(request, pk):
    member = get_object_or_404(ClubMember, pk=pk, status='PENDING')
    if request.method == 'POST':
        member.status = 'APPROVED'
        member.reviewed_by = request.user
        member.reviewed_at = timezone.now()
        member.save()
        messages.success(request, f'Đã duyệt {member.user.username} vào CLB!')
        return redirect('members:admin_pending')
    return render(request, 'members/confirm_action.html', {
        'member': member, 'action': 'approve'
    })


@login_required
@user_passes_test(is_admin)
def reject_member_view(request, pk):
    member = get_object_or_404(ClubMember, pk=pk, status='PENDING')
    if request.method == 'POST':
        member.status = 'REJECTED'
        member.reviewed_by = request.user
        member.reviewed_at = timezone.now()
        member.reject_reason = request.POST.get('reject_reason', '').strip()
        member.save()
        messages.success(request, f'Đã từ chối đơn của {member.user.username}.')
        return redirect('members:admin_pending')
    return render(request, 'members/confirm_action.html', {
        'member': member, 'action': 'reject'
    })


@login_required
@user_passes_test(is_admin)
def adjust_points_view(request, pk):
    member = get_object_or_404(ClubMember, pk=pk, status='APPROVED')
    if request.method == 'POST':
        try:
            delta = int(request.POST.get('points', 0))
        except ValueError:
            messages.error(request, 'Số điểm không hợp lệ.')
            return redirect('members:admin_members')
        note = request.POST.get('note', '').strip()
        member.total_points = max(0, member.total_points + delta)
        member.save(update_fields=['total_points'])
        PointLog.objects.create(
            member=member, points=delta, reason='MANUAL',
            note=note or 'Admin điều chỉnh', created_by=request.user
        )
        messages.success(request, f'Đã điều chỉnh điểm cho {member.user.username}.')
        return redirect('members:admin_members')
    return render(request, 'members/adjust_points.html', {'member': member})