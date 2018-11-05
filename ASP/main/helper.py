from .models import *
from django.db.models import Q
import datetime
from enum import Enum
import math

class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class Status(Enum):
    QUEUED_FOR_PROCESSING = 1
    PROCESSING_BY_WAREHOUSE = 2
    QUEUED_FOR_DISPATCH = 3
    DISPATCHED = 4
    DELIVERED = 5


def priorityToInt(pr):
    priority=pr.lower()
    if priority == "high":
        return 1
    elif priority == "medium":
        return 2
    else:
        return 3

def intToPriority(n):
    if n==1:
        return "High"
    elif n==2:
        return "Medium"
    else:
        return "Low"

def statusToInt(st):
    status=st.lower()
    if status == "queued for processing":
        return 1
    elif status == "processing by warehouse":
        return 2
    elif status == "queued for dispatch":
        return 3
    elif status == "dispatched":
        return 4
    else:
        return 5

def intToStatus(n):
    if n==1:
        return "Queued for Processing"
    elif n==2:
        return "Processing by Warehouse"
    elif n==3:
        return "Queued for Dispatch"
    elif n==4:
        return "Dispatched"
    else:
        return "Delivered"


#commit items in cart into order and delete all items in cart
def cartToOrder(cart, priority):
    itemsInCart=ItemsInCart.objects.filter(cartID=cart)
    if not itemsInCart:
        return False
    clinicMan=ClinicManager.objects.get(id=cart.clinicID.id)
    quantity=cart.getQuantity()
    weight=cart.getWeight() + 1.2
    status= statusToInt('Queued for Processing')
    orderPriority=priority
    orderTime=datetime.datetime.now()

    orderEnt=Order(clinicID=clinicMan, quantity=quantity, weight=weight, status=status, priority=orderPriority, orderDateTime=orderTime)
    orderEnt.save()

    for item in itemsInCart:
        itemOrdersEnt=ItemsInOrder(orderID=orderEnt, itemID=item.itemID)
        itemOrdersEnt.save()

    cart.emptyCart()
    return True

#return next order to be dispatched on the drone
def dp_nextOrders(allOrders):
    weight=float(0)
    orderToLoad=[]
    remainingOrder=[]
    for order in allOrders:
        weight+=order.weight
        if weight<25:
            orderToLoad.append(order)
        else:
            remainingOrder.append(order)

    return (orderToLoad, remainingOrder)

# return a list of string where each element represent a string of the leg information
def routePlanner(clinic):
    # Queen Mary hospital detail: Lat. 22.243243, Long. 114.153765
    qmLat=22.243243
    qmLong=114.153765

    # function to find the distance between 2 location
    def haversine_km(lat1,long1,lat2, long2):
        d2r=math.pi / 180.0
        dlong = (long2 - long1) * d2r
        dlat = (lat2 - lat1) * d2r
        a = pow(sin(dlat/2.0), 2) + cos(lat1*d2r) * cos(lat2*d2r) * pow(sin(dlong/2.0), 2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = 6371 * c
        return distance

    # only trial, please return like this
    strList=[]
    strList.append("Trial")
    strList.append("Anotha one")
    return strList