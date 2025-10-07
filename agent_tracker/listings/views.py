from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Agent, AgentStats, Listing
from datetime import datetime, timedelta
from collections import defaultdict
from .ai_service import generate_outreach_email

@login_required
def agent_list(request):
    agent_list_query = Agent.objects.select_related('agentstats').order_by('-agentstats__sales_volume_12mo')
    
    paginator = Paginator(agent_list_query, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'listings/agent_list.html', context)

@login_required
def agent_detail(request, mls_id):
    agent = get_object_or_404(Agent, mls_id=mls_id)
    stats = agent.agentstats
    
    one_year_ago = datetime.now().date() - timedelta(days=365)
    sales_for_chart = (agent.list_sides.all() | agent.buy_sides.all()).filter(status='SLD', settled_date__gte=one_year_ago).distinct()

    monthly_data = defaultdict(lambda: {'volume': 0.0, 'sides': 0})
    for sale in sales_for_chart:
        if sale.settled_date and sale.sale_price:
            month_key = sale.settled_date.strftime('%Y-%m')
            monthly_data[month_key]['volume'] += float(sale.sale_price)
            monthly_data[month_key]['sides'] += 1
            
    sorted_months = sorted(monthly_data.keys())
    chart_labels = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months]
    chart_volume_data = [monthly_data[month]['volume'] for month in sorted_months]
    chart_sides_data = [monthly_data[month]['sides'] for month in sorted_months]

    all_listings = (agent.list_sides.all() | agent.buy_sides.all()).distinct().order_by('-settled_date')

    context = {
        'agent': agent,
        'stats': stats,
        'listings': all_listings[:50],  # Show latest 50 transactions
        'chart_labels': chart_labels,
        'chart_volume_data': chart_volume_data,
        'chart_sides_data': chart_sides_data,
        'preserved_filters': request.GET.urlencode(),
    }
    return render(request, 'listings/agent_detail.html', context)

@login_required
def generate_email(request, mls_id):
    agent = get_object_or_404(Agent, mls_id=mls_id)
    email_content = generate_outreach_email(agent)
    return HttpResponse(f"<pre>{email_content}</pre>")

@login_required
def add_favorite(request, mls_id):
    agent = get_object_or_404(Agent, mls_id=mls_id)
    agent.favorites.add(request.user)
    return redirect('agent-detail', mls_id=agent.mls_id)

@login_required
def remove_favorite(request, mls_id):
    agent = get_object_or_404(Agent, mls_id=mls_id)
    agent.favorites.remove(request.user)
    return redirect('agent-detail', mls_id=agent.mls_id)

@login_required
def favorite_list(request):
    favorite_agents = request.user.favorite_agents.select_related('agentstats').all()
    context = {'agents': favorite_agents}
    return render(request, 'listings/favorite_list.html', context)
