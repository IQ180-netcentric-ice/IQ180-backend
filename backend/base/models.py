from django.utils import timezone
from django.db import models

    # created_at = models.DateTimeField(default=timezone.now,blank=True, null=True)

class User(models.Model):
    username = models.CharField(max_length=255,blank=True, null=True)

class Review(models.Model):
    review = models.CharField(max_length=255, blank=True, null=True)
    star = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now,blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)

# class ProfilePic(models.Model):
#     # pic_id = models.BigAutoField(primary_key=True, auto_created=True)
#     url = models.CharField(max_length=255,blank=True, null=True)

# class UserDetail(models.Model):
#     # id = models.BigAutoField(primary_key=True, auto_created=True)
#     name = models.CharField(max_length=255,blank=True, null=True)
#     email = models.CharField(max_length=255,blank=True, null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
#     pic = models.ForeignKey(ProfilePic, on_delete=models.CASCADE,blank=True, null=True)

# class RoundStat(models.Model):
#     # round_id = models.SmallIntegerField(primary_key=True, auto_created=True)
#     time_length = models.SmallIntegerField(blank=True, null=True)
#     answer = models.CharField(max_length=255,blank=True, null=True)
#     result = models.CharField(max_length=255,blank=True, null=True)
#     evaluate = models.CharField(max_length=255,blank=True, null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)

# class GameStat(models.Model):
#     # game_id = models.BigAutoField(primary_key=True, auto_created=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
#     round = models.ForeignKey(RoundStat, on_delete=models.CASCADE, blank=True, null=True)
#     point = models.SmallIntegerField(blank=True, null=True)

    # class Meta:
        # unique_together = ('user', 'round')
