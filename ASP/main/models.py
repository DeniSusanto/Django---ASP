from django.db import models
import uuid
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
import base64
import os
from django.db.models import Q
from math import sin, cos, atan2, sqrt, pi
from itertools import permutations
from sys import float_info

# Create your models here.
            
class Clinic(models.Model):
    name=models.CharField(max_length=300, unique=True)
    lat=models.FloatField()
    longitude=models.FloatField()
    alt=models.IntegerField()

    def __str__(self):
        return str(self.name)
    
    def calc_dist(self, target):
        lat1=self.lat
        long1=self.longitude

        lat2=target.lat
        long2=target.longitude
        
        rad = pi / 180.0
        d_long = (long2 - long1) * rad
        d_lat = (lat2 - lat1) * rad
        a = pow(sin(d_lat / 2.0), 2) + cos(lat1 * rad) * cos(lat2 * rad) * pow(sin(d_long / 2.0), 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c
        return distance
   

class ItemCategory(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

class ItemCatalogue(models.Model):
    name=models.CharField(max_length=100)
    weight=models.FloatField()
    category= models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    image=models.ImageField(upload_to="item/")
    description=models.TextField(blank=True, null=True)

    def __str__(self):
        return str("ID: " + str(self.id) + " " + self.name)

class UserRecord(models.Model):
    firstName=models.CharField(max_length=100)
    lastName=models.CharField(max_length=100)
    username=models.CharField(max_length=250, unique=True)
    password=models.CharField(max_length=100)
    email=models.EmailField(max_length=254, unique=True)
    image=models.ImageField(upload_to="profilePic/", blank=True, null=True, default='profilePic/noUserPic.png')

    class Meta:
        abstract=True

    def fullName(self):
        return self.firstName + " " + self.lastName       

class ClinicManager(UserRecord):
    locationID=models.OneToOneField(Clinic, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.firstName+" " + self.lastName + " from clinic " + self.locationID.name)



class WarehousePersonnel(UserRecord):
    pass

    def __str__(self):
        return str(self.firstName+" " + self.lastName)

class Dispatcher(UserRecord):
    pass

    def __str__(self):
        return str(self.firstName+" " + self.lastName)

class HospitalAuthority(UserRecord):
    pass

    def __str__(self):
        return str(self.firstName+" " + self.lastName)

class Cart(models.Model):
    clinicID= models.OneToOneField(ClinicManager, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.clinicID.firstName+" "+ self.clinicID.lastName+"'s cart")

    def getWeight(self):
        itemList=ItemsInCart.objects.filter(cartID=self)
        weight=float(0)
        for item in itemList:
            weight=weight+item.itemID.weight
        
        return weight
    
    def getQuantity(self):
        itemList=ItemsInCart.objects.filter(cartID=self)
        num=0
        for item in itemList:
            num+=1
        
        return num

    def emptyCart(self):
        itemList=ItemsInCart.objects.filter(cartID=self)
        for item in itemList:
            item.delete()

class ItemsInCart(models.Model):
    cartID=models.ForeignKey(Cart, on_delete=models.CASCADE)
    itemID=models.ForeignKey(ItemCatalogue, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cartID.clinicID.firstName + " " + self.cartID.clinicID.lastName + "'s cart: " + self.itemID.name)

class Token(models.Model):
    def id_generator():
        return get_random_string(length=6)
    email=models.EmailField(max_length=254, unique=True)
    role=models.IntegerField()
    token=models.CharField(max_length=10,default=id_generator,editable=False)

    '''def getEmail(self):
        ret_email=Token.objects.filter(token=self)
        return ret_email'''

    def __str__(self):
      return str(self.email)

class Order(models.Model):
    clinicID=models.ForeignKey(ClinicManager, on_delete=models.CASCADE)
    quantity= models.IntegerField()
    weight=models.FloatField()
    status=models.IntegerField()
    priority=models.IntegerField()
    orderDateTime=models.DateTimeField()
    file=models.FileField(upload_to='orderLabel/', null=True, blank=True)

    def __str__(self):
        return str("Order id:" + str(self.id) + " belong to " + self.clinicID.fullName())

    def priorityString(self):
        n=self.priority
        if n == 1:
            return "High"
        elif n == 2:
            return "Medium"
        else:
            return "Low"

    def weightRound(self):
        return format(self.weight,'.2f') 
    
    def getItemQuantity(self, itemID):
        if ItemsInOrder.objects.filter(Q(itemID=itemID) & Q(orderID=self.id)).count()>0:
            return ItemsInOrder.objects.filter(Q(itemID=itemID) & Q(orderID=self.id)).count()

class ItemsInOrder(models.Model):
    orderID=models.ForeignKey(Order, on_delete=models.CASCADE)
    itemID=models.ForeignKey(ItemCatalogue, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.orderID.clinicID.firstName + " " + self.orderID.clinicID.lastName + "'s order: " + self.itemID.name)


class OrderRecord(models.Model):
    orderID=models.ForeignKey(Order, on_delete=models.CASCADE)
    dispatchedDateTime=models.DateTimeField()
    deliveredDateTime=models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str("Order record of order " + str(self.orderID.id))

