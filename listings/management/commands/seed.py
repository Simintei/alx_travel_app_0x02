from django.core.management.base import BaseCommand
from listings.models import Listing
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seed the database with sample listings data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        self.stdout.write(self.style.SUCCESS("Seeding listings..."))

        for _ in range(10):  # create 10 sample listings
            Listing.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                price_per_night=random.randint(50, 500),
                location=fake.city(),
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
