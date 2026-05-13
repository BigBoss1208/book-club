from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from members.models import Club, ClubMember
from events.models import ClubEvent
from datetime import timedelta
from django.db.models import Count, Q

@login_required
def recommend_clubs_view(request):
    user = request.user
    joined_club_ids = ClubMember.objects.filter(user=user).values_list('club_id', flat=True)
    clubs = Club.objects.filter(is_active=True).exclude(id__in=joined_club_ids)
    user_club_ids = ClubMember.objects.filter(user=user).values_list('club_id', flat=True)
    user_club_categories = Club.objects.filter(id__in=user_club_ids).values_list('category', flat=True)
    now = timezone.now()
    recent = now - timedelta(days=30)
    club_scores = []
    for club in clubs:
        member_count = ClubMember.objects.filter(club=club, status='APPROVED').count()
        event_count = ClubEvent.objects.filter(club=club, start_time__gte=recent).count()
        same_category = 1 if club.category in user_club_categories else 0
        score = member_count * 2 + event_count * 3 + same_category * 5
        club_scores.append((club, score))
    club_scores.sort(key=lambda x: x[1], reverse=True)
    top_clubs = [c for c, s in club_scores[:5]]
    return render(request, 'recommendations/recommend.html', {'clubs': top_clubs})
