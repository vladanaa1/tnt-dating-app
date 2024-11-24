

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # id inherited from AbstractUsera
    # username inherited from AbstractUsera
    # password inherited from AbstractUsera
    # first_name inherited from AbstractUsera
    # last_name inherited from AbstractUsera
    is_admin = models.BooleanField(blank=False, null=True, default=False)
    iduser = models.CharField(db_column='iduser', max_length=30, default='NoIdUser', null=True)
    idadmin = models.CharField(db_column='idadmin', max_length=30, default='NoIdAdmin', null=True)
    picture = models.ImageField(null=True, default="default_avatar.jpg")
    email = models.CharField(max_length=30, unique=True, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.BooleanField(default=True, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_premium = models.BooleanField(blank=False, null=True, default=False)
    premium_time = models.CharField(max_length=30, blank=True, null=True)
    is_suspended = models.BooleanField(blank=False, null=True, default=False)
    suspended_time = models.CharField(max_length=30, blank=True, null=True)
    hobbies = models.ManyToManyField('Hobby', related_name='users', blank=True)

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    class Meta:
        managed = True
        db_table = 'User'



class Rating(models.Model):
    user = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Rating {self.rating} for {self.user.username}"



class Hobby(models.Model):
    idhobby = models.CharField(db_column='idhobby', primary_key=True, max_length=30)
    name = models.CharField(max_length=30, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Hobby'



class Message(models.Model):
    idmsg = models.CharField(db_column='idmsg', primary_key=True, max_length=30)
    iduser1 = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser1', related_name='sent_messages')
    iduser2 = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser2', related_name='received_messages')
    time = models.CharField(max_length=30, blank=True, null=True)
    date = models.CharField(max_length=30, blank=True, null=True)
    text = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Message'
        unique_together = (('iduser1', 'iduser2', 'idmsg'),)



class Chats(models.Model):
    iduser1 = models.ForeignKey(Message, models.DO_NOTHING, db_column='iduser1', related_name='chat_user1')
    iduser2 = models.ForeignKey(Message, models.DO_NOTHING, db_column='iduser2', related_name='chat_user2')
    idmsg = models.ForeignKey(Message, models.DO_NOTHING, db_column='idmsg', related_name='chat_messages')
    iduser = models.ForeignKey(User, models.DO_NOTHING, db_column='iduser')

    class Meta:
        managed = True
        db_table = 'Chats'
        unique_together = (('iduser1', 'iduser2', 'idmsg', 'iduser'),)



class Payment(models.Model):
    iduser = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser', blank=True, null=True)
    idpay = models.CharField(db_column='idpay', primary_key=True, max_length=30)
    date = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Payment'



class Report(models.Model):
    iduser1 = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser1', related_name='reports_made')
    iduser2 = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser2', related_name='reports_received')
    idrep = models.CharField(db_column='idrep', max_length=30)
    date = models.CharField(max_length=30, blank=True, null=True)
    time = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Report'
        unique_together = (('iduser1', 'iduser2', 'idrep'),)



class Suspension(models.Model):
    date = models.CharField(max_length=30, blank=True, null=True)
    time = models.CharField(max_length=30, blank=True, null=True)
    idsus = models.CharField(db_column='idsus', primary_key=True, max_length=30)
    idadmin = models.ForeignKey('User', models.DO_NOTHING, db_column='idadmin', related_name='admin_who_suspended', blank=True, null=True)
    iduser = models.ForeignKey('User', models.DO_NOTHING, db_column='iduser', related_name='user_who_recived_suspension', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Suspension'
