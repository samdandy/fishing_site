from django.db import models

class FlowRate(models.Model):
    reading_time_central = models.DateTimeField()
    flow_rate = models.FloatField()

    class Meta:
        db_table = '"river"."bra_flow_rate"' 
        managed = False


class WindSpeed(models.Model):
    start_time_central = models.DateTimeField(primary_key=True)
    wind_speed_mph = models.FloatField()

    class Meta:
        db_table = '"weather"."nws_wind"' 
        managed = False


class Temperature(models.Model):
    start_time_central = models.DateTimeField(primary_key=True)
    temperature_f = models.FloatField(null=True)

    class Meta:
        db_table = '"weather"."nws_wind"'
        managed = False

class WindDirection(models.Model):
    start_time_central = models.DateTimeField(primary_key=True)
    wind_direction = models.CharField(max_length=10)

    class Meta:
        db_table = '"weather"."nws_wind"'
        managed = False