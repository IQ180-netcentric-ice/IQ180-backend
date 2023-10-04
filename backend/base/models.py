from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.IntegerField(primary_key=True, verbose_name='user_id')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.name


class Detail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
