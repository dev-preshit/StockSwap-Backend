from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from userauth.models import Shop
from ecommerce.models import Product, Order

class Command(BaseCommand):
    help = 'Seeds demo users, shops, products, and sample orders into StockSwap database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting StockSwap database seeding...'))

        with transaction.atomic():
            # 1. User 1 - TechVault
            u1, _ = User.objects.get_or_create(
                username='techstore@stockswap.com',
                defaults={
                    'email': 'techstore@stockswap.com',
                    'first_name': 'Alex Rivera'
                }
            )
            u1.set_password('pass1234')
            u1.save()

            s1, _ = Shop.objects.get_or_create(
                user=u1,
                defaults={
                    'shop_name': 'TechVault Electronics',
                    'phone': '+1-555-0192',
                    'address': '101 Silicon Way, San Jose, CA'
                }
            )

            # 2. User 2 - Urban Threads
            u2, _ = User.objects.get_or_create(
                username='apparelhub@stockswap.com',
                defaults={
                    'email': 'apparelhub@stockswap.com',
                    'first_name': 'Elena Rostova'
                }
            )
            u2.set_password('pass1234')
            u2.save()

            s2, _ = Shop.objects.get_or_create(
                user=u2,
                defaults={
                    'shop_name': 'Urban Threads Boutique',
                    'phone': '+1-555-0148',
                    'address': '450 Fashion Ave, New York, NY'
                }
            )

            # 3. User 3 - Cornerstone Living
            u3, _ = User.objects.get_or_create(
                username='homegoods@stockswap.com',
                defaults={
                    'email': 'homegoods@stockswap.com',
                    'first_name': 'Marcus Vance'
                }
            )
            u3.set_password('pass1234')
            u3.save()

            s3, _ = Shop.objects.get_or_create(
                user=u3,
                defaults={
                    'shop_name': 'Cornerstone Living',
                    'phone': '+1-555-0177',
                    'address': '88 Craft Street, Austin, TX'
                }
            )

            # Seed Products
            demo_products = [
                {
                    'shop': s1,
                    'name': 'Wireless Noise-Canceling Headphones',
                    'description': 'Premium over-ear studio headphones with active noise cancellation and 30-hour battery life.',
                    'category': 'Electronics',
                    'price': 149.99,
                    'quantity': 15,
                    'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600'
                },
                {
                    'shop': s1,
                    'name': 'Ergonomic Mechanical Keyboard',
                    'description': 'Tactile mechanical switches, RGB backlighting, and hot-swappable keys for ultimate typing comfort.',
                    'category': 'Electronics',
                    'price': 89.50,
                    'quantity': 8,
                    'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600'
                },
                {
                    'shop': s1,
                    'name': 'Ultra-Fast Portable SSD 1TB',
                    'description': 'Compact USB-C external solid state drive with up to 1050MB/s read speeds. Currently sold out.',
                    'category': 'Electronics',
                    'price': 110.00,
                    'quantity': 0, # Out of stock product for testing
                    'image_url': 'https://images.unsplash.com/photo-1597872250970-4566f1d244a3?w=600'
                },
                {
                    'shop': s2,
                    'name': 'Organic Cotton Oversized Hoodie',
                    'description': 'Heavyweight 100% organic cotton hoodie with brushed interior and relaxed unisex fit.',
                    'category': 'Apparel',
                    'price': 65.00,
                    'quantity': 20,
                    'image_url': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600'
                },
                {
                    'shop': s2,
                    'name': 'Handcrafted Leather Crossbody Bag',
                    'description': 'Full-grain Italian leather bag with adjustable strap and brass hardware.',
                    'category': 'Apparel',
                    'price': 120.00,
                    'quantity': 5,
                    'image_url': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600'
                },
                {
                    'shop': s3,
                    'name': 'Ceramic Handcrafted Espresso Cup Set',
                    'description': 'Set of 4 matte stoneware espresso cups with natural terracotta rim.',
                    'category': 'Home & Kitchen',
                    'price': 34.00,
                    'quantity': 12,
                    'image_url': 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600'
                },
                {
                    'shop': s3,
                    'name': 'Minimalist Oak Wood Desk Organizer',
                    'description': 'Solid oak tray with phone dock, pen slots, and cable management cutouts.',
                    'category': 'Home & Kitchen',
                    'price': 45.00,
                    'quantity': 10,
                    'image_url': 'https://images.unsplash.com/photo-1591129841117-3adfd313e34f?w=600'
                }
            ]

            created_products = []
            for pdata in demo_products:
                prod, created = Product.objects.get_or_create(
                    shop=pdata['shop'],
                    name=pdata['name'],
                    defaults=pdata
                )
                if not created:
                    for k, v in pdata.items():
                        setattr(prod, k, v)
                    prod.save()
                created_products.append(prod)

            # Seed a sample order: u2 buys 1 headphone from u1
            headphone = created_products[0]
            if not Order.objects.filter(buyer=u2, product_name=headphone.name).exists():
                Order.objects.create(
                    product=headphone,
                    product_name=headphone.name,
                    buyer=u2,
                    seller=u1,
                    quantity=1,
                    price_at_purchase=headphone.price,
                    total_amount=headphone.price,
                    status='paid'
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo users, shops, products, and orders!'))
        self.stdout.write(self.style.SUCCESS('Demo Credentials:'))
        self.stdout.write('  1. techstore@stockswap.com / pass1234 (Shop: TechVault Electronics)')
        self.stdout.write('  2. apparelhub@stockswap.com / pass1234 (Shop: Urban Threads Boutique)')
        self.stdout.write('  3. homegoods@stockswap.com / pass1234 (Shop: Cornerstone Living)')
