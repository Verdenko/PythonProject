# Create your models here.

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class WoodType(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'Тип древесины'  # название таблицы в панели администратора
        verbose_name_plural = 'Типы древесины'

class TimePeriod(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'Отопительный Период'  # название таблицы в панели администратора
        verbose_name_plural = 'Отопительные периоды'

class DryerType(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'Тип сушилки'  # название таблицы в панели администратора
        verbose_name_plural = 'Типы сушилок'
class WoodCatalog(models.Model):
    name = models.CharField('Название материала',max_length=255)
    density = models.PositiveIntegerField('Плотность',default=1)
    wood_type = models.ForeignKey(WoodType,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Плотность сухого материала'  # название таблицы в панели администратора
        verbose_name_plural = 'Плотности сухого материала'

class WoodParameters(models.Model):
    temp_dif = models.IntegerField('Wh-Wk',validators=[MinValueValidator(10), MaxValueValidator(90)])
    dryer = models.ForeignKey(DryerType, on_delete=models.CASCADE)
    period = models.ForeignKey(TimePeriod, on_delete=models.CASCADE)
    heat_value=models.IntegerField('q ккал.кг',default=1)
    wood_type = models.ForeignKey(WoodType, on_delete=models.CASCADE)

    def __str__(self):
        return f" {self.id},{self.wood_type},{self.period},{self.dryer}"

    class Meta:
        verbose_name = 'Удельные расходы теплоты на сушку древесины'  # название таблицы в панели администратора
        verbose_name_plural = 'Удельные расходы теплоты на сушку древесины'
