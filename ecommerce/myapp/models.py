from django.db import models

# Create your models here.

class Products(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.FloatField()
    image = models.ImageField(upload_to='index/')