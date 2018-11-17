from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseForbidden, FileResponse
from django.shortcuts import redirect
from django.db.models import Q
from django.db.models import Count
from django.contrib import messages
from .models import *
from .helper import *
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, SimpleDocTemplate, TableStyle, Paragraph
from reportlab.platypus.tables import Table
from io import BytesIO
import datetime
import csv


#global variable
maxOrderWeight=23.8

#####DELETE THIS###
def boredaf(request):
    return redirect('http://www.staggeringbeauty.com/')
#####DELETE THIS###

def registration(request):
    token=request.GET.get('token')
    if(request.method=='POST'):
        
        dummy= Token.objects.filter(token=token)
        email = ""
        userType = ""
        for data in dummy:
            email = data.email
            userType = data.role;

        firstName=request.POST.get('firstName')
        lastName =request.POST.get('lastName')
        username =request.POST.get('username')
        password =request.POST.get('password')

        context ={
                    'firstName' : firstName,
                    'lastName'  : lastName,
                    'username'  : username,
                    'password'  : password,
                    'error'     : 1,
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
                    return render(request,'main/registration.html',context)
                Dispatcher(firstName=firstName,lastName=lastName,username=username,password=password,email=email).save()
            elif(userType==4):
                userCounter = HospitalAuthority.objects.filter(username=username).count()
                if (userCounter == 1):
                    return render(request,'main/registration.html',context)
                HospitalAuthority(firstName=firstName,lastName=lastName,username=username,password=password,email=email).save()
        #image    =request.POST.get('image')
        Token.objects.filter(token=token).delete()
        return render(request,'main/login.html')
    else :
        dummy= Token.objects.filter(token=token)
        userType = ""
        for data in dummy:
            userType = data.role;

        if(userType==1):
            allLocations = Clinic.objects.all()
            allExistingLocations = ClinicManager.objects.all()
            for existingLocation in allExistingLocations:
                allLocations=allLocations.exclude(id=existingLocation.locationID.id)

            context ={
                'allLocations' : allLocations,
                'isCM' : True
            }
        return render(request,'main/registration.html',context)
    return render(request,'main/registration.html')
            

def loginSession(request):
    if 'id' in request.session and 'role' in request.session:
        role=request.session['role']
        return redirectToHome(request)
    else:
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
                request.session['role']="cm"
                ClinicManager.objects.get(pk=request.session['id'])
                return redirect('/main/cm_home')
            elif wp.count() > 0:
                request.session['id']=wp[0].id
                request.session['role']="wp"
                WarehousePersonnel.objects.get(pk=request.session['id'])
                return redirect('/main/wp_home')
            elif dis.count() > 0:
                request.session['id']=dis[0].id
                request.session['role']="dp"
                Dispatcher.objects.get(pk=request.session['id'])
                return redirect('/main/dp_dashboard')
            elif ha.count() > 0:
                request.session['id']=ha[0].id
                request.session['role']="ha"
                HospitalAuthority.objects.get(pk=request.session['id'])
                return redirect()
            else: #data doesnt match any user records
                messages.error(request,'The Username or Password Entered is Incorrect. Please Try Again.')
                return redirect('/main/login')


def onlineOrder(request):
    if not isUserPermitted(request,'cm'):
        return redirectToHome(request)

    clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    allCategories=ItemCategory.objects.all()
    if(request.method=='GET'):#if session has filter request
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
    if not isUserPermitted(request,'cm'):
        return redirectToHome(request)

    if request.method=='GET':
        clinicMan=ClinicManager.objects.get(pk=request.session['id'])
        cartObj=Cart.objects.get(clinicID=clinicMan)
        cartWeight=format(cartObj.getWeight(),'.2f') 
        itemsCount=ItemsInCart.objects.filter(cartID=cartObj).values('itemID').annotate(total=Count('cartID')).order_by('itemID')
        #itemsCartList=ItemsInCart.objects.filter(cartID=cartObj).values('itemID').distinct().order_by('itemID')
        itemsInCart=[]
        for item in itemsCount:
            itemName=(ItemCatalogue.objects.get(pk=item['itemID'])).name
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
    if not isUserPermitted(request,'cm'):
        return redirectToHome(request)

    clinicMan=ClinicManager.objects.get(pk=request.session['id'])
    allCategories=ItemCategory.objects.all()
    cartObj=Cart.objects.get(clinicID=clinicMan)
    priority=int(request.POST.get('priority'))
    succeed=cartToOrder(cartObj, priority)
    if succeed:#if suceed to migrate cart to order
        
        request.session['success']="Order has been submitted!"
        return redirect('/main/myorders')
    else:
       
        request.session['error']="Oh no!"
        request.session['message']="Failed to submit order"
        return redirect('/main/cm_home')


def wp_home(request):
    if not isUserPermitted(request, 'wp'):
        return redirectToHome(request)

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

        request.session['success'] = "Order has been updated!"
        return redirect('/main/wp_home')


def order_details(request):
    if request.method == 'POST':
        warehouse = WarehousePersonnel.objects.get(pk=request.session['id'])
        order_id = request.POST.get('id')
        order_type = request.POST.get('type')
        # order_id = int(order_id[:-1])
        order = Order.objects.get(pk=order_id)
        clinic_manager = Order.objects.get(pk=order_id).clinicID
        clinic = Clinic.objects.get(pk=clinic_manager.pk).name
        items_list = ItemsInOrder.objects.filter(orderID=order_id).values_list('itemID', flat=True).distinct()

        class ItemDetails:
            def __init__(self, item_id, name, quantity):
                self.item_id = item_id
                self.name = name
                self.quantity = quantity

        item_details_list = []

        for item in items_list:
            temp = Order.objects.filter(pk=order_id)
            item_name = ItemCatalogue.objects.get(pk=item).get_name()
            item_quantity = temp[0].getItemQuantity(item)
            item_details_list.append(ItemDetails(item, item_name, item_quantity))

        context = {
            'warehouse': warehouse,
            'order': order,
            'type': order_type,
            'cm': clinic_manager,
            'clinic': clinic,
            'item_details': item_details_list,
        }
        return render(request, 'main/order_details.html', context)
    else:
        request.session['error'] = "Oh no!"
        request.session['message'] = "Failed to view order"
        return redirect('/main/wp_home')


def pdf_download(request):
    if request.method == 'POST':
        order_id = request.POST.get('id')
        order = Order.objects.get(pk=order_id)
        clinic_manager = Order.objects.get(pk=order_id).clinicID
        clinic = Clinic.objects.get(pk=clinic_manager.pk)
        items_list = ItemsInOrder.objects.filter(orderID=order_id).values_list('itemID', flat=True).distinct()

        class ItemDetails:
            def __init__(self, item_id, name, quantity):
                self.item_id = item_id
                self.name = name
                self.quantity = quantity

        item_details_list = []

        for item in items_list:
            temp = Order.objects.filter(pk=order_id)
            item_name = ItemCatalogue.objects.get(pk=item).get_name()
            item_quantity = temp[0].getItemQuantity(item)
            item_details_list.append(ItemDetails(item, item_name, item_quantity))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="ShippingLabel.pdf"'  # CHANGE TO ATTACHMENT

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=portrait(letter))
        c.setTitle("order"+str(order_id))
        # Borders
        c.line(60, 720, 550, 720)
        c.line(60, 720, 60, 50)
        c.line(60, 50, 550, 50)
        c.line(550, 720, 550, 50)

        # Need to change path
        #path = r'C:\Users\Kevin Hung\Documents\_Projects\Unchained\ASP\main\qm_logo.jpg'
        #c.drawImage(path, 80, 610, width=120, height=100)

        c.line(60, 595, 550, 595)  # Horizontal line
        c.line(220, 595, 220, 720)  # Vertical line
        c.setFont('Helvetica', 12, leading=None)
        print_time = str(datetime.date.today())
        c.drawRightString(540, 700, "Order #"+str(order_id))
        c.drawString(230, 700, "Ordered on: " + str(order.orderDateTime.date()))
        c.drawString(230, 685, "Processed on: " + print_time)
        c.drawString(230, 670, "Weight: " + str(order.weightRound()) + " kg")
        c.drawString(230, 655, "Delivery from: Queen Mary Hospital")
        c.drawString(307, 640, "(22.269660, 114.131303, 163)")
        c.line(220, 630, 550, 630)

        c.setFont('Helvetica', 23, leading=None)
        if order.priority == 1:
            package_title = "ASP HIGH-PRIORITY PKG"
        elif order.priority == 2:
            package_title = "ASP MEDIUM-PRIORITY PKG"
        else:
            package_title = "ASP LOW-PRIORITY PKG"

        c.drawCentredString(385, 605, package_title)

        c.setFont('Helvetica', 15, leading=None)
        c.drawString(70, 575, "SHIP TO: " + clinic_manager.firstName + ' ' + clinic_manager.lastName)
        c.drawString(138, 555, clinic.name)
        c.drawString(138, 535, "(" + str(clinic.lat) + ", " + str(clinic.longitude) + ", " + str(clinic.alt) + ")")

        c.line(60, 525, 550, 525)

        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'Times-Bold'
        styles['Normal'].fontSize = 12
        style = ParagraphStyle(
            name='Body',
            fontName='Times-Roman',
            fontSize=12,
        )

        width, height = letter
        data = [[Paragraph("ID", styles['Normal']),
                 Paragraph("Name", styles['Normal']),
                 Paragraph("Quantity", styles['Normal'])],
                ]

        for item in item_details_list:
            item_data = [Paragraph(str(item.item_id), style), Paragraph(item.name, style), Paragraph(str(item.quantity), style)]
            data.append(item_data)


        table = Table(data, colWidths=[30, 350, 70])

        table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
             ('VALIGN', (0, 0), (-1, 0), 'TOP'),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)]))

        table.wrapOn(c, width, height)
        table.wrapOn(c, width, height)
        table.drawOn(c, 80, 300)

        c.showPage()
        c.save()

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    else:
        request.session['error'] = "Oh no!"
        request.session['message'] = "Failed to view order"
        return redirect('/main/wp_home')


def dp_dashboard(request):
    if not isUserPermitted(request, 'dp'):
        return redirectToHome(request)

    dispatcher = Dispatcher.objects.get(pk=request.session['id'])
    orderQueue = Order.objects.filter(status=statusToInt("Queued for Dispatch")).order_by('priority', 'orderDateTime')
    tupleOrder = dp_nextOrders(orderQueue)
    nextOrders = tupleOrder[0]
    remainingQueue = tupleOrder[1]
    context = {
        'nextOrders': nextOrders,
        'dispatcher': dispatcher,
        'orderQueue': remainingQueue,
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

    return render(request, 'main/dp_dashboard.html', context)

def dp_session(request):
    if not isUserPermitted(request,'dp'):
        return redirectToHome(request)

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

def itineraryDownload(request):
    if not isUserPermitted(request,'dp'):
        return redirectToHome(request)

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
    if not isUserPermitted(request,'dp'):
        return redirectToHome(request)

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

def logout(request):
    userLogout(request)
    return redirect('/main/login')

def myorders(request):
    if not isUserPermitted(request,'cm'):
        return redirectToHome(request)
    clinicMan= ClinicManager.objects.get(pk=request.session['id'])
    openOrdersObj=Order.objects.filter(Q(clinicID=clinicMan) & ~Q(status=5)).order_by('-orderDateTime')
    openOrders=[] #tuples lists
    for order in openOrdersObj:
        itemsObj=ItemsInOrder.objects.filter(orderID=order).values('itemID').distinct()
        itemsTup=[]
        for itemid in itemsObj:
            item=ItemCatalogue.objects.get(pk=itemid['itemID'])
            itemQuantity=order.getItemQuantity(item)
            tup=(item.name, itemQuantity)
            itemsTup.append(tup)
        if order.status==1:
            action="cancel"
        elif order.status==4:
            action="confirm"
        else:
            action="none"
        orderTup=(order.id, intToStatus(order.status),intToPriority(order.priority), itemsTup, format(order.weight,'.2f'), order.orderDateTime, action)
        openOrders.append(orderTup)

    finishedOrdersObj=Order.objects.filter(Q(clinicID=clinicMan) & Q(status=5)).order_by('-orderDateTime')
    finishedOrders=[] #tuples list
    for order in finishedOrdersObj:
        itemsObj=ItemsInOrder.objects.filter(orderID=order).values('itemID').distinct()
        itemsTup=[]
        for itemid in itemsObj:
            item=ItemCatalogue.objects.get(pk=itemid['itemID'])
            itemQuantity=order.getItemQuantity(item)
            tup=(item.name, itemQuantity)
            itemsTup.append(tup)
        recordObj=OrderRecord.objects.get(orderID=order)
        orderTup=(order.id, intToPriority(order.priority), itemsTup, format(order.weight,'.2f'), order.orderDateTime, recordObj.deliveredDateTime)
        finishedOrders.append(orderTup)

    context={
                'openOrders':openOrders,
                'orderHistory':finishedOrders,
                'clinicManager':clinicMan,
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
    return render(request, 'main/cm_myorders.html', context)

def deleteOrder(request):
    orderID=int(request.GET.get('order'))
    order=Order.objects.get(pk=orderID)
    order.delete()
    return redirect('/main/myorders')

def confirmReceived(request):
    orderID=int(request.GET.get('order'))
    order=Order.objects.get(pk=orderID)
    order.status=statusToInt("Delivered")
    order.save()

    record=OrderRecord.objects.get(orderID=order)
    record.deliveredDateTime=datetime.datetime.now()
    record.save()

    return redirect('/main/myorders')

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

    # #get clinic distance from another clinic
    # clinic= Clinic.objects.get(pk=1)
    # target=Clinic.objects.get(pk=2)
    # return HttpResponse(clinic.calc_dist(target))

    del request.session['success']
    return HttpResponse("ok")
    #delete all sessions
    keys=[]
    for key, value in request.session.items():
        keys.append(key)
    for key in keys:
        del request.session[key]
    return redirect('/main/login')
    #return HttpResponse(datetime.datetime.now())

    pass
