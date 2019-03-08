from django.db import models
from django.contrib.auth.models import AbstractUser

class Class(models.Model):
    class_name = models.CharField(verbose_name="授業名", max_length=20)

    def __str__(self):
        return self.class_name

class User(AbstractUser):
    twitter_id = models.CharField(verbose_name="ツイッターid", max_length=20)
    classes = models.ManyToManyField(Class, verbose_name="履修科目")
    token = models.IntegerField(verbose_name="トークン")

    def __str__(self):
        return self.username
