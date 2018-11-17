from django.db.models import Q
import datetime
from enum import Enum
from math import sin, cos, atan2, sqrt, pi
from itertools import permutations
from sys import float_info
from .models import *
from django.shortcuts import redirect
from django.db.models import Q


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
    priority = pr.lower()
    if priority == "high":
        return 1
    elif priority == "medium":
        return 2
    else:
        return 3


def intToPriority(n):
    if n == 1:
        return "High"
    elif n == 2:
        return "Medium"
    else:
        return "Low"


def statusToInt(st):
    status = st.lower()
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
    if n == 1:
        return "Queued for Processing"
    elif n == 2:
        return "Processing by Warehouse"
    elif n == 3:
        return "Queued for Dispatch"
    elif n == 4:
        return "Dispatched"
    else:
        return "Delivered"


# commit items in cart into order and delete all items in cart
def cartToOrder(cart, priority):
    itemsInCart=ItemsInCart.objects.filter(cartID=cart)
    if not itemsInCart:
        return False
    clinicMan = ClinicManager.objects.get(id=cart.clinicID.id)
    quantity = cart.getQuantity()
    weight = cart.getWeight() + 1.2
    status = statusToInt('Queued for Processing')
    orderPriority = priority
    orderTime = datetime.datetime.now()

    orderEnt = Order(clinicID=clinicMan, quantity=quantity, weight=weight, status=status, priority=orderPriority,
                     orderDateTime=orderTime)
    orderEnt.save()

    for item in itemsInCart:
        itemOrdersEnt = ItemsInOrder(orderID=orderEnt, itemID=item.itemID)
        itemOrdersEnt.save()

    cart.emptyCart()
    return True


# return next order to be dispatched on the drone
def dp_nextOrders(allOrders):
    weight = float(0)
    orderToLoad = []
    remainingOrder = []
    for order in allOrders:
        weight += order.weight
        if weight < 25:
            orderToLoad.append(order)
        else:
            remainingOrder.append(order)

    return (orderToLoad, remainingOrder)


# return a list of string where each element represent a string of the leg information
def routePlanner(clinics):
    queen_mary = Clinic(name="Queen Mary Hospital", lat=22.269660, longitude=114.131303, alt=163)

    all_routes = list(permutations(clinics))
    best_route = ()
    best_dist = float_info.max
    for route in all_routes:
        route_name = []
        dist = 0
        for i in range(len(route)):
            route_name.append(route[i].name)
            if i == 0:
                dist += queen_mary.calc_dist(route[i])
            else:
                dist += route[i-1].calc_dist(route[i])
        dist += route[len(route) - 1].calc_dist(queen_mary)
        if dist < best_dist:
            best_dist = dist
            best_route = route

    leg_list = []
    for i in range(len(best_route)):
        leg = "(" + str.format('{0:.6f}', best_route[i - 1].lat) + "," + str.format('{0:.6f}', best_route[i].longitude) + "," + str(best_route[i].alt) + ")"
        leg_list.append(leg)
    leg_list.append("(" + str.format('{0:.6f}', queen_mary.lat) + "," + str.format('{0:.6f}', queen_mary.longitude) + "," + str(queen_mary.alt) + ")")
    return leg_list

# def sendDispatchedEmail(orders):
#     for order in orders:
#         cmEmail=order.clinicID.email
        
def userLogout(request):
    # keys=[]
    # for key, value in request.session.items():
    #     keys.append(key)
    # for key in keys:
    #     del request.session[key]
    del request.session['id']
    del request.session['role']

def redirectToHome(request):
    if 'role' in request.session:
        role=request.session['role']
        if role=='cm':
            return redirect('/main/cm_home')
        elif role=='dp':
            return redirect('/main/dp_dashboard')
        elif role=='wp':
            pass
        elif role=='ha':
            pass
    else:
        return redirect('/main/login')

def isUserPermitted(request, targetRole):
    userRole=request.session['role']
    if userRole != targetRole:
        return False
    else:
        return True
