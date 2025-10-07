import csv
from django.core.management.base import BaseCommand
from listings.models import Listing, Agent, Brokerage
from datetime import datetime

class Command(BaseCommand):
    help = 'Imports listings from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file.')

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    listing_obj, created = Listing.objects.update_or_create(
                        list_no=row['List #'],
                        defaults={
                            'address': row['Address'],
                            'town': row['City'],
                            'status': row['Status'],
                        }
                    )

                    if row.get('Sale Price'):
                        listing_obj.sale_price = float(row['Sale Price'].replace(',', ''))
                    
                    if row.get('List Price'):
                        listing_obj.list_price = float(row['List Price'].replace(',', ''))

                    if row.get('Settled Date'):
                        try:
                            listing_obj.settled_date = datetime.strptime(row['Settled Date'], '%m/%d/%Y').date()
                        except (ValueError, TypeError):
                            listing_obj.settled_date = None
                    
                    listing_obj.save()

                    if row.get('List Agent'):
                        agent, _ = Agent.objects.get_or_create(mls_id=row['List Agent'], defaults={'agent_name': 'Name not available'})
                        listing_obj.listing_agents.add(agent)

                    if row.get('Sell Agent'):
                        agent, _ = Agent.objects.get_or_create(mls_id=row['Sell Agent'], defaults={'agent_name': 'Name not available'})
                        listing_obj.selling_agents.add(agent)

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing row {row['List #']}: {e}"))
        self.stdout.write(self.style.SUCCESS('Successfully imported listings.'))
