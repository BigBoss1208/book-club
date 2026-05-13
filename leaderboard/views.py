from django.shortcuts import render
from django.shortcuts import render

def leaderboard_view(request):
    return render(request, 'leaderboard/leaderboard.html', {})
