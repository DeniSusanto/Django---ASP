from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ItemCategory)
admin.site.register(ItemCatalogue)
admin.site.register(ClinicManager)
admin.site.register(Clinic)
admin.site.register(WarehousePersonnel)
admin.site.register(Dispatcher)
admin.site.register(HospitalAuthority)
admin.site.register(Cart)
admin.site.register(ItemsInCart)
admin.site.register(ItemsInOrder)
admin.site.register(Order)
admin.site.register(OrderRecord)

