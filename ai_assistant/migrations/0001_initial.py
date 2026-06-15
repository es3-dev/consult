import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="AIInteractionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=40)),
                ("question_preview", models.CharField(max_length=160)),
                ("response_time_ms", models.PositiveIntegerField(default=0)),
                ("estimated_tokens", models.PositiveIntegerField(default=0)),
                ("success", models.BooleanField(default=False)),
                ("error_message", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_interactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="aiinteractionlog", index=models.Index(fields=["user", "-created_at"], name="ai_assistan_user_id_424014_idx")),
        migrations.AddIndex(model_name="aiinteractionlog", index=models.Index(fields=["provider", "success"], name="ai_assistan_provide_c4e0d5_idx")),
    ]
