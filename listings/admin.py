from django.contrib import admin
from .models import Agent, Listing, Brokerage, AgentStats

admin.site.register(Agent)
admin.site.register(Listing)
admin.site.register(Brokerage)
admin.site.register(AgentStats)
