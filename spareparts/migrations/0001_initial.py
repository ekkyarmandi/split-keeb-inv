# Generated by Django 4.1.3 on 2022-12-21 03:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("arrival", models.DateField(blank=True, null=True)),
                ("arrival_days", models.IntegerField(blank=True, default=0, null=True)),
                ("origin", models.CharField(max_length=100)),
                (
                    "shopping_platform",
                    models.CharField(
                        blank=True, default="offline", max_length=100, null=True
                    ),
                ),
                ("is_usd", models.BooleanField(default=False)),
                ("usd_to_idr", models.FloatField(default=0)),
                ("shipping_fee", models.FloatField(default=0)),
                ("total_tax", models.IntegerField(default=0)),
                ("sum_product_price", models.FloatField(default=0)),
                ("total_order", models.IntegerField(default=0)),
                ("track_order_link", models.CharField(default="#", max_length=700)),
                ("notes", models.TextField(blank=True, default="", null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Sparepart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("added", models.DateField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=125)),
                ("kind", models.CharField(blank=True, max_length=125, null=True)),
                ("in_stock", models.IntegerField(default=0)),
                ("price", models.FloatField(default=0)),
                ("price_perunit", models.FloatField(default=0)),
                ("link", models.CharField(default="#", max_length=700)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_stock", "In Stock"),
                            ("out_of_stock", "Out of Stock"),
                            ("on_delivery", "On Delivery"),
                        ],
                        default="on_delivery",
                        max_length=15,
                    ),
                ),
            ],
            options={
                "ordering": ["kind"],
            },
        ),
        migrations.CreateModel(
            name="OrderSparepart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("unit", models.IntegerField(default=0)),
                ("qty", models.IntegerField(default=0)),
                ("price", models.FloatField(default=0)),
                (
                    "order",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spareparts.order",
                    ),
                ),
                (
                    "sparepart",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spareparts.sparepart",
                    ),
                ),
            ],
            options={
                "ordering": ["order__date", "order"],
            },
        ),
    ]
