from django.db import models



# Create your models here.

from django.contrib.auth.models import User

class UserClient(models.Model):
    user = models.OneToOneField(User, unique=True)
    nickname = models.CharField(max_length=10)
    signature = models.CharField(max_length=50)
    #headshot = models.ImageField(upload_to='headshot/%Y/%m/%d')
    headshot = models.CharField(max_length=100)

    class Admin():
        pass

class Photo(models.Model):
    description = models.CharField(max_length=120)
    ip_addr = models.IPAddressField()
    praise = models.IntegerField()
    upload_date = models.DateField(auto_now_add=True)
    upload_user = models.ForeignKey(UserClient)
    #upload_photo = models.ImageField(upload_to='photo/%Y/%m/%d')
    upload_photo = models.CharField(max_length=100)

    class Admin():
        pass

class Comment(models.Model):
    content = models.CharField(max_length=120)
    comm_date = models.DateField(auto_now_add=True)
    comm_user = models.ForeignKey(UserClient)
    comm_img = models.ForeignKey(Photo)

    class Admin():
        pass

class Follow(models.Model):
    follow_user = models.ForeignKey(UserClient, related_name='follow_and_followed_user')
    followed_user = models.ForeignKey(UserClient)

    class Meta:
        unique_together = ('follow_user', 'followed_user')


    class Admin():
        pass