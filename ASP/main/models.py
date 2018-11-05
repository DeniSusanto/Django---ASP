from django.db import models

# Create your models here.

class Clinic(models.Model):
    name=models.CharField(max_length=300)
    lat=models.FloatField()
    longitude=models.FloatField()
    alt=models.IntegerField()

    def __str__(self):
        return str(self.name)

class ItemCategory(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return str(self.name)

class ItemCatalogue(models.Model):
    name=models.CharField(max_length=100)
    weight=models.FloatField()
    category= models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    image=models.ImageField(upload_to="item/")
    description=models.TextField()

    def __str__(self):
        return str(self.name)

class UserRecord(models.Model):
    firstName=models.CharField(max_length=100)
    lastName=models.CharField(max_length=100)
    username=models.CharField(max_length=250, unique=True)
    password=models.CharField(max_length=100)
    email=models.EmailField(max_length=254, unique=True)

    class Meta:
        abstract=True

class ClinicManager(UserRecord):
    locationID=models.OneToOneField(Clinic, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.firstName+" " + self.lastName)

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
    token=models.CharField(max_length=250)
    email=models.EmailField(max_length=254)

class Order(models.Model):
    clinicID=models.ForeignKey(ClinicManager, on_delete=models.CASCADE)
    quantity= models.IntegerField()
    weight=models.FloatField()
    status=models.IntegerField()
    priority=models.IntegerField()
    orderDateTime=models.DateTimeField()

    def __str__(self):
        return str("Order id:" + str(self.id))

class ItemsInOrder(models.Model):
    orderID=models.ForeignKey(Order, on_delete=models.CASCADE)
    itemID=models.ForeignKey(ItemCatalogue, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.orderID.clinicID.firstName + " " + self.orderID.clinicID.lastName + "'s order: " + self.itemID.name)


class OrderRecord(models.Model):
    orderID=models.ForeignKey(Order, on_delete=models.CASCADE)
    dispatchedDateTime=models.DateTimeField()
    deliveredDateTime=models.DateTimeField(blank=True, null=True)


