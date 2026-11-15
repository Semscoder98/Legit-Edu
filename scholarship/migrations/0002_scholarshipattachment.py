# Generated manually to add downloadable scholarship documents.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarship', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScholarshipAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=150)),
                ('file', models.FileField(upload_to='scholarships/attachments/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('scholarship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='scholarship.scholarship')),
            ],
        ),
    ]
