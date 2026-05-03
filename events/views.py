import io
import qrcode
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import ClubEvent, EventCheckin
from members.models import ClubMember

is_admin = lambda u: u.is_staff


@login_required
@user_passes_test(is_admin)
def event_list_view(request):
    events = ClubEvent.objects.filter(is_active=True).prefetch_related('checkins')
    return render(request, 'events/event_list.html', {'events': events})


@login_required
@user_passes_test(is_admin)
def event_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        event_date = request.POST.get('event_date', '')
        if not title or not event_date:
            messages.error(request, 'Vui lòng nhập đủ thông tin.')
            return render(request, 'events/event_form.html')
        event = ClubEvent.objects.create(
            title=title,
            description=request.POST.get('description', ''),
            event_date=event_date,
            location=request.POST.get('location', ''),
            points_reward=int(request.POST.get('points_reward', 10)),
            checkin_window_minutes=int(request.POST.get('checkin_window_minutes', 60)),
            created_by=request.user,
        )
        messages.success(request, f'Đã tạo buổi "{event.title}"!')
        return redirect('events:event_detail', pk=event.pk)
    return render(request, 'events/event_form.html')


@login_required
@user_passes_test(is_admin)
def event_detail_view(request, pk):
    event = get_object_or_404(ClubEvent, pk=pk)
    checkins = event.checkins.select_related('member__user').order_by('-checked_in_at')
    checkin_url = request.build_absolute_uri(f'/events/checkin/{event.qr_token}/')
    return render(request, 'events/event_detail.html', {
        'event': event, 'checkins': checkins, 'checkin_url': checkin_url,
    })


@login_required
@user_passes_test(is_admin)
def event_qr_view(request, pk):
    event = get_object_or_404(ClubEvent, pk=pk)
    checkin_url = request.build_absolute_uri(f'/events/checkin/{event.qr_token}/')
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')


@login_required
def checkin_view(request, token):
    event = get_object_or_404(ClubEvent, qr_token=token, is_active=True)
    try:
        member = request.user.club_member
    except Exception:
        messages.error(request, 'Bạn chưa là thành viên CLB.')
        return redirect('members:join_club')

    if member.status != 'APPROVED':
        messages.error(request, 'Tài khoản thành viên chưa được duyệt.')
        return redirect('members:my_membership')

    deadline = event.event_date + timedelta(minutes=event.checkin_window_minutes)
    if timezone.now() > deadline:
        return render(request, 'events/checkin_result.html', {
            'event': event, 'success': False, 'reason': 'expired'
        })

    if EventCheckin.objects.filter(event=event, member=member).exists():
        return render(request, 'events/checkin_result.html', {
            'event': event, 'success': False, 'reason': 'already'
        })

    EventCheckin.objects.create(event=event, member=member)
    return render(request, 'events/checkin_result.html', {
        'event': event, 'success': True,
        'points_earned': event.points_reward,
        'total_points': member.total_points,
    })


@login_required
def public_event_list_view(request):
    events = ClubEvent.objects.filter(is_active=True).order_by('event_date')
    member = ClubMember.objects.filter(user=request.user, status='APPROVED').first()
    checked_in_ids = set(
        EventCheckin.objects.filter(member=member).values_list('event_id', flat=True)
    ) if member else set()
    return render(request, 'events/public_event_list.html', {
        'events': events, 'member': member, 'checked_in_ids': checked_in_ids,
    })