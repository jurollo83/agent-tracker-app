from django.db import models
from django.contrib.auth.models import User

class Brokerage(models.Model):
    office_code = models.CharField(max_length=50, primary_key=True, unique=True)
    office_name = models.CharField(max_length=255)

    def __str__(self):
        return self.office_name

class Agent(models.Model):
    mls_id = models.CharField(max_length=50, primary_key=True, unique=True)
    agent_name = models.CharField(max_length=255)
    favorites = models.ManyToManyField(User, related_name='favorite_agents', blank=True)

    def __str__(self):
        return f"{self.agent_name} ({self.mls_id})"

class Listing(models.Model):
    STATUS_CHOICES = [('ACT', 'Active'), ('SLD', 'Sold'), ('EXP', 'Expired'), ('CAN', 'Cancelled'), ('WTH', 'Withdrawn')]
    list_no = models.CharField(max_length=50, unique=True, primary_key=True)
    address = models.CharField(max_length=255)
    town = models.CharField(max_length=100)
    list_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    settled_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    listing_agents = models.ManyToManyField(Agent, related_name='list_sides')
    selling_agents = models.ManyToManyField(Agent, related_name='buy_sides', blank=True)

    def __str__(self):
        return f"{self.address}, {self.town} - {self.status}"

class AgentStats(models.Model):
    agent = models.OneToOneField(Agent, on_delete=models.CASCADE, primary_key=True)
    sales_volume_12mo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sales_count_12mo = models.IntegerField(default=0)
    sell_side_count_12mo = models.IntegerField(default=0)
    buy_side_count_12mo = models.IntegerField(default=0)
    yoy_volume_change = models.FloatField(default=0.0)
    listing_success_rate = models.FloatField(default=0.0)
    churn_risk_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.agent.agent_name}"
