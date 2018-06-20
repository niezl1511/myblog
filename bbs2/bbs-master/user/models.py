from django.db import models


class User(models.Model):
    SEX = (
        ('M', '男'),
        ('F', '女'),
        ('U', '未知'),
    )

    nickname = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    openid = models.CharField(max_length=32, unique=True, null=True, blank=True)
    icon = models.ImageField()
    openicon = models.CharField(max_length=256, null=True, blank=True)
    sex = models.CharField(max_length=8, choices=SEX)
    age = models.IntegerField()

    @property
    def avatar(self):
        if self.icon:
            return self.icon.url
        else:
            return self.openicon
