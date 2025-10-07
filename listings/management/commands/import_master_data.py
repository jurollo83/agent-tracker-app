import csv
from django.core.management.base import BaseCommand
from listings.models import Brokerage, Agent

class Command(BaseCommand):
    help = 'Imports master data for brokerages and agents from text files'

    def add_arguments(self, parser):
        parser.add_argument('brokerage_file', type=str, help='The path to the brokerage text file.')
        parser.add_argument('agent_file', type=str, help='The path to the agent text file.')

    def handle(self, *args, **options):
        # Import Brokerages
        with open(options['brokerage_file'], 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                Brokerage.objects.update_or_create(
                    office_code=row[0],
                    defaults={'office_name': row[1]}
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported brokerages.'))

        # Import Agents
        with open(options['agent_file'], 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                Agent.objects.update_or_create(
                    mls_id=row[0],
                    defaults={'agent_name': row[1]}
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported agents.'))
