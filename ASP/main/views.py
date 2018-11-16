from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.db.models import Q
from django.db.models import Count
from django.contrib import messages
from .models import *
from .helper import *
import csv


#global variable
maxOrderWeight=23.8

#####DELETE THIS###
def boredaf(request):
    return redirect('http://www.staggeringbeauty.com/')
#####DELETE THIS###

def preRegistration(request):
    token=request.GET.get('token')
    counter = Token.objects.filter(token=token).count()
    
    if (request.method=='POST'):
        userType =request.POST.get('userType')
        url = "main/registration?token="+token+"&userType="+userType
        return redirect(url)
        
    else:
        if counter == 1:
            return render(request,'main/preregistration.html')
        else:
            return redirect('http://www.staggeringbeauty.com/')

def registration(request):
    userType = int(request.GET.get('userType'))
    token=request.GET.get('token')
    url = "main/registration?token="+token+"&userType="+str(userType)
    if(request.method=='POST'):
        
        dummy= Token.objects.filter(token=token)
        email = ""
        for data in dummy:
            email = data.email
        
        firstName=request.POST.get('firstName')
        lastName =request.POST.get('lastName')
        username =request.POST.get('username')
        password =request.POST.get('password')

        context ={
                    'firstName' : firstName,
                    'lastName'  : lastName,
                    'username'  : username,
                    'password'  : password,
                    'error'     : True,
                }
        if(userType==1):
            userCounter = ClinicManager.objects.filter(username=username).count()
            if (userCounter == 1):
                return render(request,url,context)
            location     = int(request.POST.get('location'))
            clinic = Clinic.objects.filter(id=location)
            for something in clinic:
                ClinicManager(firstName=firstName,lastName=lastName,username=username,password=password,email=email,locationID=something).save()
        else:
            if(userType==2):
                userCounter = WarehousePersonnel.objects.filter(username=username).count()
                if (userCounter == 1):
                    return render(request,'main/registration.html',context)
                WarehousePersonnel(firstName=firstName,lastName=lastName,username=username,password=password,email=email).save()
            elif(userType==3):
                userCounter = Dispatcher.objects.filter(username=username).count()
                if (userCounter == 1):
                    return render(request,url,context)
                Dispatcher(firstName=firstName,lastName=lastName,username=username,password=password,email=email).save()
            elif(userType==4):
                userCounter = HospitalAuthority.objects.filter(username=username).count()
                if (userCounter == 1):
                    return render(request,url,context)
                HospitalAuthority(firstName=firstName,lastName=lastName,username=username,password=password,email=email).save()
        #image    =request.POST.get('image')
        Token.objects.filter(token=token).delete()
        return redirect('http://www.google.com')
       
    else :
        if(userType==1):
            allLocations = Clinic.objects.all()
            context ={
                'allLocations' : allLocations,
                'isCM' : True
            }
            return render(request,'main/registration.html',context)
        return render(request,'main/registration.html')
            

def loginSession(request):
    if(request.method=='GET'): #return just the homepage
        return render(request, 'main/login.html')    
    else: #process the login
        uname=request.POST.get('username')
        pw=request.POST.get('password')
        cm=ClinicManager.objects.filter(Q(username=uname) & Q(password=pw))
        wp=WarehousePersonnel.objects.filter(Q(username=uname) & Q(password=pw))
        dis=Dispatcher.objects.filter(Q(username=uname) & Q(password=pw))
        ha=HospitalAuthority.objects.filter(Q(username=uname) & Q(password=pw))
        if cm.count() > 0:
            request.session['id']=cm[0].id
            ClinicManager.objects.get(pk=request.session['id'])
            return redirect('/main/cm_home')
        elif wp.count() > 0:
            request.session['id']=wp[0].id
            WarehousePersonnel.objects.get(pk=request.session['id'])
            return redirect('/main/wp_home')
        elif dis.count() > 0:
            request.session['id']=dis[0].id
            Dispatcher.objects.get(pk=request.session['id'])
            return redirect('/main/dp_dashboard')    
        elif ha.count() > 0:
            request.session['id']=ha[0].id
            HospitalAuthority.objects.get(pk=request.session['id'])
            return redirect()
        else: #data doesnt match any user records
            messages.error(request,'The Username or Password Entered is Incorrect. Please Try Again.')
            return redirect('/main/login')


def onlineOrder(request):
    clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    allCategories=ItemCategory.objects.all()
    if(request.method=='GET'):
        #if session has filter request
        if 'category' in request.session:
            category=int(request.session['category'])
            if not category == -1:
                categoryObj=ItemCategory.objects.get(pk=category)
                filteredItems=ItemCatalogue.objects.filter(category=categoryObj)
                context={
                'title': "Home",
                'filter':category,
                'items':filteredItems,
                'clinicManager':clinicMan,
                'allCategories':allCategories,
                }
                
                if 'success' in request.session:
                    success=request.session['success']
                    del request.session['success']
                    context['success']=success
                if 'error' in request.session:
                    error=request.session['error']
                    del request.session['error']
                    context['error']=error
                if 'message' in request.session:
                    message=request.session['message']
                    del request.session['message']
                    context['message']=message
                
                return render(request, 'main/cm_home.html', context)
            else:
                del request.session['category']
                return redirect('cm_home')
        else:#if session has no filter request
            allItems=ItemCatalogue.objects.all()
            ###Output all item name
            # name=""
            # for item in allItems:
            #     name=name+item.name
            #     name=name+"<br>"
            # return HttpResponse(name)
            context={
                'title': "Home",
                'items':allItems,
                'clinicManager':clinicMan,
                'filter':-1,
                'allCategories':allCategories,
                }

            if 'success' in request.session:
                success=request.session['success']
                del request.session['success']
                context['success']=success
            if 'error' in request.session:
                error=request.session['error']
                del request.session['error']
                context['error']=error
            if 'message' in request.session:
                message=request.session['message']
                del request.session['message']
                context['message']=message
                
            return render(request, 'main/cm_home.html', context)
    elif(request.method=='POST'):
         if('category' in request.POST):
            category=request.POST.get('category')
            #delete browse request session
            if category==-1:
                if('category' in request.session):
                    del request.session['category']
                return redirect('/main/cm_home')
            else:#request to browse (filter) items
                request.session['category']=category #assign filter to session
                # filteredItems=ItemCatalogue.objects.filter(category=category)
                # context={
                # 'items':filteredItems,
                # 'clinicManager':clinicMan
                # }
                # return render(request, 'main/cm_home.html', context)
                return redirect('/main/cm_home')
         else:#request to add item to cart
            item=request.POST.get('item')
            quantity=int(request.POST.get('quantity'))
            itemObj=ItemCatalogue.objects.get(pk=item)
            cartObj=Cart.objects.get(clinicID=clinicMan)

            if 'category' in request:
                category=request.session['category']
                categoryObj=ItemCategory.objects.get(pk=category)
                theItems=ItemCatalogue.objects.filter(category=categoryObj)
                fil=category #there exist filter
            else:
                theItems=ItemCatalogue.objects.all()
                fil=-1

            if(itemObj.weight*quantity+cartObj.getWeight() > maxOrderWeight):
                context={
                'title': "Home",
                'filter': fil,
                'error':"Order weight limit is reached",
                'allCategories':allCategories,
                'clinicManager':clinicMan,
                'items' : theItems,
                }
                return render(request, 'main/cm_home.html', context)
           

            for i in range(quantity):
                itemInCart=ItemsInCart(cartID=cartObj, itemID=itemObj)
                itemInCart.save()

            context={
                'title': "Home",
                'filter': fil,
                'success':"Item(s) have been added to cart",
                'allCategories':allCategories,
                'clinicManager':clinicMan,
                'items' : theItems,
            }
            return render(request, 'main/cm_home.html', context)
            

def cm_cart(request):
    if request.method=='GET':
        clinicMan=ClinicManager.objects.get(pk=request.session['id'])
        cartObj=Cart.objects.get(clinicID=clinicMan)
        cartWeight=format(cartObj.getWeight(),'.2f') 
        itemsCount=ItemsInCart.objects.filter(cartID=cartObj).values('itemID').annotate(total=Count('cartID')).order_by('itemID')
        #itemsCartList=ItemsInCart.objects.filter(cartID=cartObj).values('itemID').distinct().order_by('itemID')
        itemsInCart=[]
        for item in itemsCount:
            itemName=ItemCatalogue.objects.get(pk=item['itemID'])
            tup=(item['itemID'],itemName, item['total'])
            itemsInCart.append(tup)
        
        # itemPkList=[]
        # for item in itemsCartList:
        #     itemPkList.append(item.itemID.id)
        # itemList=ItemCatalogue.objects.filter(id__in=itemPkList)
        if 'success' in request.session:
            message=request.session['success']
            del request.session['success']
            context={
                    'success': message,
                    'itemsInCart':itemsInCart,
                    'clinicManager':clinicMan,
                    'weight':cartWeight,
                    }
        else:
            context={
                    'itemsInCart':itemsInCart,
                    'clinicManager':clinicMan,
                    'weight':cartWeight,
            }
        return render(request, 'main/cm_cart.html', context)
    else:#delete item from cart request
        item=request.POST.get('item')
        itemObj=ItemCatalogue.objects.get(pk=item)
        quantity=int(request.POST.get('quantity'))
        clinicMan=ClinicManager.objects.get(pk=request.session['id'])

        itemInCart=ItemsInCart.objects.filter(Q(cartID__clinicID=clinicMan) & Q(itemID=itemObj))[:quantity]
        ItemsInCart.objects.filter(pk__in=itemInCart).delete()

        # for i in range(int(quantity)):
        #     itemInCart[i].delete()
        message=str(quantity) + " " + itemObj.name + " have been removed"
        request.session['success']=message
        return redirect('/main/cm_cart')


def submitorder(request):
    clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    allCategories=ItemCategory.objects.all()
    cartObj=Cart.objects.get(clinicID=clinicMan)
    priority=int(request.POST.get('priority'))
    succeed=cartToOrder(cartObj, priority)
    if succeed:#if suceed to migrate cart to order
        
        request.session['success']="Order has been submitted!"
        return redirect('/main/cm_home')
    else:
       
        request.session['error']="Oh no!"
        request.session['message']="Failed to submit order"
        return redirect('/main/cm_home')


def wp_home(request):
    warehouse = WarehousePersonnel.objects.get(pk=request.session['id'])
    if request.method == 'GET':
        processing_queue = Order.objects.filter(status=statusToInt("Queued for Processing")).order_by('priority', 'orderDateTime')
        packing_queue = Order.objects.filter(status=statusToInt("Processing by Warehouse")).order_by('priority', 'orderDateTime')
        context = {
            'processing_queue': processing_queue,
            'warehouse': warehouse,
            'packing_queue': packing_queue,
        }

        if 'success' in request.session:
            success = request.session['success']
            del request.session['success']
            context['success'] = success
        if 'error' in request.session:
            error = request.session['error']
            del request.session['error']
            context['error'] = error
        if 'message' in request.session:
            message = request.session['message']
            del request.session['message']
            context['message'] = message

        return render(request, 'main/wp_home.html', context)

    elif request.method == 'POST':
        order_id = request.POST.get('order')
        order_type = request.POST.get('type')
        order = Order.objects.get(pk=order_id)

        if order_type == "process":
            order.status = statusToInt("Processing by Warehouse")
            order.save()
        elif order_type == "dispatch":
            order.status = statusToInt("Queued for Dispatch")
            order.save()

        return redirect('/main/wp_home')


def order_details(request):
    if request.method == 'POST':
        warehouse = WarehousePersonnel.objects.get(pk=request.session['id'])
        order_id = request.POST.get('id')
        order_id = int(order_id[:-1])
        clinic_manager = Order.objects.get(pk=order_id).clinicID
        clinic = Clinic.objects.get(pk=clinic_manager.pk).name
        items_list = ItemsInOrder.objects.filter(orderID=order_id)
        context = {
            'warehouse': warehouse,
            'order_id': order_id,
            'cm_name': clinic_manager.firstName + " " + clinic_manager.lastName,
            'clinic': clinic,
            'items_list': items_list,
        }
        return render(request, 'main/order_details.html', context)
    else:
        return redirect('/main/wp_home')


def dp_session(request):
    dispatcher=Dispatcher.objects.get(pk=request.session['id'])
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Dispatch")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    ordersToBeProcessed=tupleOrder[0]
    if not ordersToBeProcessed:
        remainingQueue=tupleOrder[1]
        request.session['error']="No orders to be dispatched"
        return redirect('/main/dp_dashboard')
    dispatcher=Dispatcher.objects.get(pk=request.session['id'])
    context={
                'nextOrders':ordersToBeProcessed,
                'dispatcher':dispatcher,
            }
    return render(request, 'main/dp_session.html', context)


def dp_dashboard(request):
    dispatcher=Dispatcher.objects.get(pk=request.session['id'])
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Dispatch")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    nextOrders=tupleOrder[0]
    remainingQueue=tupleOrder[1]
    context={
                    'nextOrders':nextOrders,
                    'dispatcher':dispatcher,
                    'orderQueue':remainingQueue,
                }
    
    if 'success' in request.session:
        success=request.session['success']
        del request.session['success']
        context['success']=success
    if 'error' in request.session:
        error=request.session['error']
        del request.session['error']
        context['error']=error
    if 'message' in request.session:
        message=request.session['message']
        del request.session['message']
        context['message']=message

    return render(request, 'main/dp_dashboard.html', context)


def itineraryDownload(request):
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Dispatch")).order_by('priority', 'orderDateTime')
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
    dispatcher=Dispatcher.objects.get(pk=request.session['id'])
    #Fetch the order currently being dispatched
    orderQueue=Order.objects.filter(status=statusToInt("Queued for Dispatch")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    ordersToBeProcessed=tupleOrder[0]
    #send email confirmation to clinic managers
    sendDispatchedEmail(ordersToBeProcessed)
    #log orders, save it to OrderRecord
    for order in ordersToBeProcessed:
        orderRecord=OrderRecord(orderID=order, dispatchedDateTime=datetime.datetime.now(), deliveredDateTime=None)
        order.status=statusToInt("Dispatched")
        order.save()
        orderRecord.save()

    return redirect('/main/dp_dashboard')

def debug(request):
    # # #adding item to cart
    # # clinicMan=ClinicManager.objects.get(pk=2) 
    # # itemObj=ItemCatalogue.objects.get(pk=3)
    # # cartObj=Cart.objects.get(clinicID=clinicMan)
    # # quantity=10
    # # for i in range(quantity):
    # #     itemInCart=ItemsInCart(cartID=cartObj, itemID=itemObj)
    # #     itemInCart.save()
    # del request.session['category']
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
    # cartObj=Cart.objects.get(clinicID__id=3)
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

    # #get item quantity in order
    # order=Order.objects.get(pk=38)
    # return HttpResponse(order.getItemQuantity(10))

    #get clinic distance from another clinic
    clinic= Clinic.objects.get(pk=1)
    target=Clinic.objects.get(pk=2)
    return HttpResponse(clinic.calc_dist(target))

    return redirect('/main/logincm')
    #return HttpResponse(datetime.datetime.now())

    pass
