from django.contrib import admin
from .models import WoodCatalog,WoodParameters,WoodType,TimePeriod,DryerType
# Регистрация моделей таблиц в БД
admin.site.register(WoodCatalog)
admin.site.register(WoodParameters)
admin.site.register(WoodType)
admin.site.register(TimePeriod)
admin.site.register(DryerType)