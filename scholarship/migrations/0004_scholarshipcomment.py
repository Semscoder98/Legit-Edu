# Generated manually for scholarship comments

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scholarship', '0003_alter_scholarship_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScholarshipComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(blank=True, default='', max_length=80)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='scholarship.scholarshipcomment')),
                ('scholarship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='scholarship.scholarship')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
