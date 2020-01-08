from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)


class Tag(models.Model):
    name = models.CharField(max_length=64)


class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name="articles", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="articles",
                                 null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, related_name="articles")
