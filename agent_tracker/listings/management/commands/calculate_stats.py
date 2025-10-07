from django.core.management.base import BaseCommand
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from listings.models import Agent, Listing, AgentStats
from decimal import Decimal

class Command(BaseCommand):
    help = 'Calculates statistics for each agent.'

    def handle(self, *args, **options):
        self.stdout.write("Starting agent statistics calculation...")
        now = datetime.now().date()
        one_year_ago = now - timedelta(days=365)
        two_years_ago = now - timedelta(days=730)
        
        agents = Agent.objects.all()
        total_agents = agents.count()
        
        for i, agent in enumerate(agents):
            all_sold_listings = (agent.list_sides.all() | agent.buy_sides.all()).filter(status='SLD').distinct()

            # 12-month volume and sides
            sold_last_12_mo = all_sold_listings.filter(settled_date__gte=one_year_ago)
            volume_12mo = sold_last_12_mo.aggregate(total=Sum('sale_price'))['total'] or Decimal(0)
            count_12mo = sold_last_12_mo.count()

            # Previous 12-month volume for YoY calculation
            sold_prev_12_mo = all_sold_listings.filter(settled_date__gte=two_years_ago, settled_date__lt=one_year_ago)
            volume_prev_12mo = sold_prev_12_mo.aggregate(total=Sum('sale_price'))['total'] or Decimal(0)

            yoy_volume_change = 0.0
            if volume_prev_12_mo > 0:
                yoy_volume_change = float((volume_12mo - volume_prev_12_mo) / volume_prev_12_mo) * 100

            # Buy vs Sell side breakdown
            sell_side_volume_12mo = agent.list_sides.filter(status='SLD', settled_date__gte=one_year_ago).aggregate(total=Sum('sale_price'))['total'] or Decimal(0)
            buy_side_volume_12mo = agent.buy_sides.filter(status='SLD', settled_date__gte=one_year_ago).aggregate(total=Sum('sale_price'))['total'] or Decimal(0)
            sell_side_count_12mo = agent.list_sides.filter(status='SLD', settled_date__gte=one_year_ago).count()
            buy_side_count_12mo = agent.buy_sides.filter(status='SLD', settled_date__gte=one_year_ago).count()

            # Listing success rate
            agent_listings_total = agent.list_sides.filter(Q(settled_date__gte=one_year_ago) | Q(status__in=['ACT', 'NEW'])).distinct()
            total_outcomes = agent_listings_total.filter(status__in=['SLD', 'EXP', 'WTH', 'CAN']).count()
            sold_outcomes = agent_listings_total.filter(status='SLD').count()
            success_rate = (sold_outcomes / total_outcomes) * 100 if total_outcomes > 0 else 0

            # Churn Risk Score
            score = 0
            if yoy_volume_change < -10:
                score += min(abs(yoy_volume_change), 40)
            if 0 < success_rate < 75:
                score += (75 - success_rate) * 0.4
            if agent.list_sides.filter(status__in=['ACT', 'NEW']).count() > (count_12mo / 2) and count_12mo > 0:
                score += 15
            
            AgentStats.objects.update_or_create(
                agent=agent,
                defaults={
                    'sales_volume_12mo': volume_12mo,
                    'sales_count_12mo': count_12mo,
                    'sell_side_volume_12mo': sell_side_volume_12mo,
                    'buy_side_volume_12mo': buy_side_volume_12mo,
                    'sell_side_count_12mo': sell_side_count_12mo,
                    'buy_side_count_12mo': buy_side_count_12mo,
                    'yoy_volume_change': yoy_volume_change,
                    'listing_success_rate': success_rate,
                    'churn_risk_score': min(int(score), 100)
                }
            )

            if (i + 1) % 500 == 0:
                self.stdout.write(f"Processed {i + 1} / {total_agents} agents...")

        self.stdout.write(self.style.SUCCESS('Agent stats calculated successfully.'))
