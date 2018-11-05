from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.db.models import Q
from .models import *
from .helper import *
import csv

#global variable
maxOrderWeight=23.8

#####DELETE THIS###
def boredaf(request):
    return redirect('http://www.staggeringbeauty.com/')
#####DELETE THIS###

def loginSimulationCM(request):
    request.session['id']=1
    return HttpResponse("done")

def loginSimulationDP(request):
    pass

def onlineOrder(request):
    clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    if(request.method=='GET'):#if session has filter request
        if 'category' in session.request:
            category=request.session['category']
            categoryObj=ItemCategory.objects.get(pk=category)
            filteredItems=ItemCatalogue.objects.filter(category=categoryObj)
            context={
            'items':filteredItems,
            'clinicManager':clinicMan
            }
            return render(request, 'cm_home.html', context)
        else:#if session has no filter request
            allItems=ItemCatalogue.objects.all()
            ###Output all item name
            # name=""
            # for item in allItems:
            #     name=name+item.name
            #     name=name+"<br>"
            # return HttpResponse(name)
            context={
                'items':allItems,
                'clinicManager':clinicMan
                }
            return render(request, 'cm_home.html', context)
    elif(request.method=='POST'):
         if('category' in request.POST):
            category=request.POST.get('category')
            #delete browse request session
            if category==-1:
                if('category' in request.session):
                    del request.session['category']
                    redirect('/main/cm_home')
            else:#request to browse (filter) items
                request.session['category']=category #assign filter to session
                filteredItems=ItemCatalogue.objects.filter(category=category)
                context={
                'items':filteredItems,
                'clinicManager':clinicMan
                }
                return render(request, 'cm_home.html', context)
         else:#request to add item to cart
            item=request.POST.get('item')
            quantity=int(request.POST.get('quantity'))
            itemObj=ItemCatalogue.objects.get(pk=item)
            cartObj=Cart.objects.get(clinicID=clinicMan)

            if(itemObj.weight*quantity+cartObj.getWeight() > maxOrderWeight):
                context={
                'error':"Order weight limit is reached"
                }
                return render(request, 'cm_home.html', context)
           

            for i in range(quantity):
                itemInCart=ItemsInCart(cartID=cartObj, itemID=itemObj)
                itemInCart.save()
            redirect('main/cm_home')

def cm_cart(request):
    if request.method=='GET':
        clinicMan=ClinicManager.objects.get(pk=request.session['id'])
        cartObj=Cart.objects.get(clinicID=clinicMan)
        cartWeight=cartObj.cartWeight()
        itemsCartList=ItemsInCart.objects.filter(cartID=cartObj)
        # itemPkList=[]
        # for item in itemsCartList:
        #     itemPkList.append(item.itemID.id)
        # itemList=ItemCatalogue.objects.filter(id__in=itemPkList)
        context={
                    'itemsInCart':itemsCartList,
                    'clinicManager':clinicMan,
                    'weight':cartWeight,
                }
        
        return render(request, 'cm_cart.html', context)
    else:#delete item from cart request
        item=request.POST.get('item')
        itemObj=ItemCatalogue.objects.get(pk=item)
        quantity=request.POST.get('quantity')

        clinicMan=ClinicManager.objects.get(pk=request.session['id'])

        itemInCart=ItemsInCart.objects.filter(Q(cartID__clinicID=clinicMan) & Q(itemID=itemObj))
        for i in range(quantity):
            itemInCart[i].delete()

        redirect('main/cm_cart')


def submitorder(request):
    clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    cartObj=Cart.objects.get()
    priority=request.POST.get('priority')
    succeed=cartToOrder(cartObj, priority)
    if suceed:
        return HttpResponse("Suceeded")
    else:
        redirect('main/cm_cart')

def dp_dashboard(request):
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    nextOrders=tupleOrder[0]
    remainingQueue=tupleOrder[1]
    dispatcher=Dispatcher.objects.get(pk=request.session['id'])
    context={
                    'nextOrders':nextOrders,
                    'dispatcher':dispatcher,
                    'orderQueue':remainingQueue,
                }
    return render(request, 'dp_dashboard.html', context)

def dp_session(request):
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    ordersToBeProcessed=tupleOrder[0]
    dispatcher=Dispatcher.objects.get(pk=request.session['id'])
    context={
                'nextOrders':ordersToBeProcessed,
                'dispatcher':dispatcher,
            }
    return render(request, 'dp_session.html', context)

def itineraryDownload(request):
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    ordersToBeProcessed=tupleOrder[0]
    clinicIdList=[]
    for order in ordersToBeProcessed:
        clinicIdList.append(order.clinicID.locationID.id)
    allClinics=Clinic.objects.filter(id__in=clinicIdList)

    ###Please implement the routePlanner function in helper.py###
    itineraryList=routePlanner(allClinics)
    ###Please implement the routePlanner function in helper.py###

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ItineraryFile.csv"'
    writer = csv.writer(response)
    for st in itineraryList:
        writer.writerow([st,""])
    return response

def dp_close_session(request):
    #Fetch the order currently being dispatched
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    ordersToBeProcessed=tupleOrder[0]
    #log orders, save it to OrderRecord
    for order in ordersToBeProcessed:
        orderRecord=OrderRecord(orderID=order, dispatchedDateTime=datetime.datetime.now(), deliveredDateTime=None)
        order.status=statusToInt("Dispatched")
        order.save()
    redirect('main/dp_dashboard')

def debug(request):
    # #adding item to cart
    # clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    # itemObj=ItemCatalogue.objects.get(pk=2)
    # cartObj=Cart.objects.get(clinicID=clinicMan)
    # quantity=2
    # for i in range(quantity):
    #     itemInCart=ItemsInCart(cartID=cartObj, itemID=itemObj)
    #     itemInCart.save()
    # return HttpResponse("all good")

    # ##getWeight()
    # myCart=Cart.objects.get(pk=1)
    # return HttpResponse(myCart.getWeight())

    # #trying stuffs
    # user=ClinicManager.objects.get(pk=1)
    # itemList=ItemsInCart.objects.filter(cartID__clinicID=user)
    # itemPkList=[]
    # for item in itemList:
    #         itemPkList.append(item.itemID.id)
    # itemList=ItemCatalogue.objects.filter(Q(id__in=itemPkList) | Q(id=1)).order_by('-id')
    # return HttpResponse(itemList)

    # #deleting item from cart simulator
    # itemInCart=ItemsInCart.objects.filter(Q(cartID__clinicID__id=1) & Q(itemID__id=2))
    # for i in range(1):
    #     itemInCart[i].delete()
    # return HttpResponse("deleted")
    
    # #migrate cart to order simulator
    # cartObj=Cart.objects.get(clinicID__id=1)
    # priority= priorityToInt("High")
    # cartToOrder(cartObj, priority)

    # #output all orders
    # orderList=Order.objects.all().order_by('priority','orderDateTime')
    # name=""
    # for order in orderList:
    #     name+=str(order.id)
    #     name+="<br>"
    # return HttpResponse(name)

    #save orderRecords simulator
    # oR=OrderRecord(orderID_id=1, dispatchedDateTime=datetime.datetime.now(), deliveredDateTime=None)
    # oR.save()

    # #CSV file download simulator
    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="ItineraryFile.csv"'
    # writer = csv.writer(response)
    # clinic=Clinic.objects.all()
    # for i in range(3):
    #     st=""
    #     st+="Leg " + str(i) + "Queen Mary Hospital -> " + clinic[i].name 
    #     writer.writerow([st,""])
    # return response

    ##dafuq
    # orderQueue=Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime')
    # tupleOrder = dp_nextOrders(orderQueue)
    # ordersToBeProcessed=tupleOrder[0]
    # return HttpResponse(ordersToBeProcessed)

    # #try list queryset
    # orderQueue=list(Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime'))
    # name=""
    # for order in orderQueue:
    #     name+=str(order.id)
    #     name+="<br>"
    # return HttpResponse(name)

    return HttpResponse(datetime.datetime.now())

    pass