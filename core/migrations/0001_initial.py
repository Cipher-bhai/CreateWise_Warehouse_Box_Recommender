import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('length', models.DecimalField(decimal_places=2, help_text='Length in cm', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('width', models.DecimalField(decimal_places=2, help_text='Width in cm', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('height', models.DecimalField(decimal_places=2, help_text='Height in cm', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('weight', models.DecimalField(decimal_places=2, help_text='Weight in kg', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('length', models.DecimalField(decimal_places=2, help_text='Interior length in cm', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('width', models.DecimalField(decimal_places=2, help_text='Interior width in cm', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('height', models.DecimalField(decimal_places=2, help_text='Interior height in cm', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('max_weight', models.DecimalField(decimal_places=2, help_text='Maximum weight capacity in kg', max_digits=6, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('cost', models.DecimalField(decimal_places=2, help_text='Cost of this box', max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['cost']},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('packed', 'Packed'), ('shipped', 'Shipped')], default='pending', max_length=20)),
                ('ai_explanation', models.TextField(blank=True, default='', help_text='AI-generated explanation of why the box was recommended.')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_created', to=settings.AUTH_USER_MODEL)),
                ('products', models.ManyToManyField(related_name='orders', to='core.product')),
                ('recommended_box', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='core.box')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
