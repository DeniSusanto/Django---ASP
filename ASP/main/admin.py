from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group, User

admin.site.register(ClinicManager)
admin.site.register(Dispatcher)
admin.site.register(ItemsInCart)
admin.site.register(ItemsInOrder)
admin.site.register(Order)
admin.site.register(OrderRecord)

# #temporarily ommited from admin panel
admin.site.register(ItemCatalogue)
# admin.site.register(ItemCategory)
admin.site.register(Clinic)
# admin.site.register(WarehousePersonnel)
# admin.site.register(HospitalAuthority)
admin.site.register(Cart)


class TokenAdmin(admin.ModelAdmin):
    def save_model(self,request,obj,form,change):
        emailExist = ClinicManager.objects.filter(email=obj.email).count() + WarehousePersonnel.objects.filter(email=obj.email).count() + Dispatcher.objects.filter(email=obj.email).count() +  HospitalAuthority.objects.filter(email=obj.email).count()
        if emailExist == 1:
            messages.error(request, "Email already exists")
            # return render() -> render back to admin page to ask for new email
        else:
            email = []
            email.append(obj.email)
            token = obj.token
            content = 'Here is your link for registration http://127.0.0.1:8000/main/preregistration?token=' + str(token) +'\n'

            send_mail('Token Registration',content,'navig8.comp3297@gmail.com',email,fail_silently=False,)
            return super(TokenAdmin,self).save_model(request,obj,form,change)
admin.site.register(Token,TokenAdmin)


#unregister
admin.site.unregister(User)
admin.site.unregister(Group)