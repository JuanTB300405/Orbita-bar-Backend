import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ('sabores', '0001_initial'),
    ]

    operations = [ 
        migrations.CreateModel(
            name='Notificaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('leida', models.BooleanField(default=False)),
                ('productoId', models.ForeignKey(db_column='productoId', on_delete=django.db.models.deletion.DO_NOTHING, to='sabores.productos')),
            ],
            options={
                'db_table': 'notificaciones',
                'managed': True,
            },
        ),
    ]

