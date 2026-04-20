from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sabores', '0019_productos_codigobarras'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='proveniencia',
            field=models.CharField(
                choices=[('mesa', 'Mesa'), ('web', 'Web')],
                default='mesa',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='mesa',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='pedidos',
                to='sabores.mesa',
            ),
        ),
    ]
