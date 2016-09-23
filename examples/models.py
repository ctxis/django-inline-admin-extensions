from django.db import models


class Author(models.Model):
   name = models.CharField(max_length=100)


class Book(models.Model):
   author = models.ForeignKey(Author, on_delete=models.CASCADE)
   wololol = models.CharField(max_length=100)
   title = models.CharField(max_length=100)
   isbn = models.CharField(max_length=100)
