# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sabores', '0010_alter_compras_fecha_alter_gastos_fecha_de_pago_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ventas',
            name='devuelta',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
