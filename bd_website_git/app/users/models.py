#from msvcrt import open_osfhandle
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import uuid

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    beandrop_social_user_uuid = models.UUIDField(primary_key = False, default=uuid.uuid4, editable=False, unique=True)
    beandrop_user_funds = models.IntegerField(default=0, editable=False)
    beandrop_cups_in_ownership = models.IntegerField(default=0, editable=False)
    beandrop_number_of_cups_used = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class registered_users_db(models.Model):
    idregistered_users_db = models.AutoField(primary_key=True)
    EXTERNAL_ID = models.CharField(max_length=64, unique=True)
    EXTERNAL_TYPE = models.CharField(max_length=16)
    PAYMENT_ID = models.CharField(max_length=45, unique=True)

    class Meta:
        managed = False
        db_table = 'registered_users_db'

    #def save(self, *args, **kwargs):
    #    super(registered_users_db, self).save(*args, **kwargs)


class users_db(models.Model):
    name_of_user = models.TextField()
    user_email = models.CharField(max_length=255)
    user_funds = models.DecimalField(max_digits=19, decimal_places=4)
    cups_owned = models.IntegerField()
    registration_date = models.DateTimeField()
    POS_ID = models.IntegerField()
    QR_generator = models.CharField(max_length=40)
    POS_generator = models.CharField(max_length=40)
    user_unique_ID  = models.AutoField(primary_key = True, unique=True)
    EXTERNAL_TYPE = models.CharField(max_length=16)
    EXTERNAL_ID = models.CharField(max_length=64)
    user_type = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'users_db'

    #def link_receipt_to_account(self, *args):
    #    try:
    #        users_db.objects.filter(QR_generator__exact=, POS_generator__exact=).update(EXTERNAL_ID=, EXTERNAL_TYPE="DJANGO_USER")
    #    except Exception:
    #        pass

class deposit_refund_transfers_db(models.Model):
    deposit_refund_pk = models.AutoField(primary_key = True, unique=True)
    registered_user_id = models.CharField(max_length=64)
    registered_user_external_type = models.CharField(max_length=64)
    users_db_qr_generator = models.CharField(max_length=40)
    transfer_id = models.CharField(max_length=45)
    transfer_value = models.DecimalField(max_digits=7, decimal_places=2)
    transfer_datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'deposit_refund_transfers_db'


class BeanDropProfile(models.Model):
    '''A model to hold the customer's bean drop cup details account'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #beandrop_qr_generator = models.CharField(default="", max_length=100, editable=False)
    beandrop_user_funds = models.IntegerField(default=0, editable=False)
    beandrop_cups_in_ownership = models.IntegerField(default=0, editable=False)
    beandrop_number_of_cups_used = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    def update_user_bean_drop_profile(self):
        # pass  # define method to pull user details from server
        beandrop_customer_accounts_connected = users_db.objects.get(EXTERNAL_ID__exact=user.beandrop_social_user_uuid).annotate(funds_sum = Sum('user_funds'), cups_sum = Sum('cups_owned'), total_cups_used_sum = Sum('')).using('customer_data')          #.using('database') is the method to select which database to querry
        beandrop_user_funds = beandrop_customer_accounts_connected.funds_sum
        beandrop_cups_in_ownership = beandrop_customer_accounts_connected.cups_sum
        #beandrop_number_of_cups_used beandrop_number_of_cups_used.total_cups_used_sum

