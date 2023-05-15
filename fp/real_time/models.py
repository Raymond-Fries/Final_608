# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Companies(models.Model):
    symbol = models.CharField(primary_key=True, max_length=7)

    def __str__(self) -> str:
        return self.symbol
    
    class Meta:
        managed = False
        db_table = 'companies'


class DailyMinuteMeans(models.Model):
    symbol = models.OneToOneField(Companies, models.DO_NOTHING, db_column='symbol', primary_key=True)
    weekday = models.CharField(max_length=12)
    timestamp = models.TimeField()
    change = models.FloatField(blank=True, null=True)
    change_std = models.FloatField(blank=True, null=True)
    standardized_mean = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_minute_means'
        unique_together = (('symbol', 'weekday', 'timestamp'),)


class IntradayPrices(models.Model):
    symbol = models.OneToOneField(Companies, models.DO_NOTHING, db_column='symbol', primary_key=True)
    timestamp = models.DateTimeField()
    open = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    low = models.FloatField(blank=True, null=True)
    close = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'intraday_prices'
        unique_together = (('symbol', 'timestamp'),)


class MinuteMeans(models.Model):
    symbol = models.OneToOneField(Companies, models.DO_NOTHING, db_column='symbol', primary_key=True)
    timestamp = models.TimeField()
    change = models.FloatField(blank=True, null=True)
    change_std = models.FloatField(blank=True, null=True)
    standardized_mean = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'minute_means'
        unique_together = (('symbol', 'timestamp'),)


class Positions(models.Model):
    position_id = models.AutoField(primary_key=True)
    symbol = models.ForeignKey(Companies, models.DO_NOTHING, db_column='symbol', blank=True, null=True)
    side = models.CharField(max_length=4, blank=True, null=True)
    pos_quantity = models.IntegerField()
    average_price = models.FloatField()
    cost = models.FloatField()

    class Meta:
        managed = False
        db_table = 'positions'


class Transactions(models.Model):
    transactions_id = models.BigAutoField(primary_key=True)
    symbol = models.ForeignKey(Companies, models.DO_NOTHING, db_column='symbol', blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    side = models.CharField(max_length=4, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    execution_id = models.CharField(max_length=50, blank=True, null=True)
    position_quantity = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transactions'
