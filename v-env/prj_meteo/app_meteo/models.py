from django.db import models

from django.db import connections

import uuid

#-------------------------------------------------------------------------------------------------
#
#   Database model : Sqlite - CollectInfo database
#
#-------------------------------------------------------------------------------------------------

class CollectInfo(models.Model):

    CollectInfoID = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Uniqe ID')
    collectdate = models.DateTimeField(null=False, blank=False, help_text='Data collect date.')
    temperature = models.FloatField(null=False, blank=False, help_text='Temperature')
    humidity = models.FloatField(null=False, blank=False, help_text='Humidity')

    # class Meta:
    #     managed = True
    #     ordering = ['collectdate']

    # def __str__(self):
    #     return f'{self.collectdate (self.collectdate)}'

    # def get_absolute_url(self):
    #     """Returns the url to access a particular instance of MyModelName."""
    #     return reverse('model-detail-view', args=[str(self.id)])


#-------------------------------------------------------------------------------------------------
#
#   Database model : MySql - homeassistant/TempData database 
#
#-------------------------------------------------------------------------------------------------

class Out_temp(models.Model):
    CollectInfoID =  models.AutoField(primary_key=True, default=None)
    collectdate = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    battery_level = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'weather_outdoor'
        ordering = ['collectdate']

    # def __str__(self):
    #     return f'{self.collectdate (self.collectdate)}'

    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])



class In_temp(models.Model):
    CollectInfoID =  models.AutoField(primary_key=True, default=None)
    collectdate = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    battery_level = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'weather_indoor'
        ordering = ['collectdate']

    # def __str__(self):
    #     return f'{self.collectdate (self.collectdate)}'

    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])


class Serre_temp(models.Model):
    CollectInfoID =  models.AutoField(primary_key=True, default=None)
    collectdate = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    battery_level = models.DecimalField(max_digits=3, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'weather_serre'
        ordering = ['collectdate']

    # def __str__(self):
    #     return f'{self.collectdate (self.collectdate)}'

    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])



