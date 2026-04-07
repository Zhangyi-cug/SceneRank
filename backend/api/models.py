from django.db import models


class SurveyConfig(models.Model):
    data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Survey Config'


class ComparisonResult(models.Model):
    image_a = models.CharField(max_length=64)
    image_b = models.CharField(max_length=64)
    selections = models.JSONField()
    background = models.JSONField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
