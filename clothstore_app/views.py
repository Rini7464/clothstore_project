from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from clothstore_app.models import product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.
def create(request):
    return HttpResponse("created")

def home(request):
    #userid=request.user.id
    #print("id of the user logged in:",userid)
    #print("Result:",request.user.is_authenticated)
    context={}
    p=product.objects.filter(is_active=True)
    context['products']=p
    print(p)
    return render(request,'index.html',context)

def product_details(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        #if is here for checking whether form is empty or not if not else part will work
        if uname=="" or upass=="" or ucpass=="":
                context['errmsg']="fields can not be empty"
                return render(request,'register.html',context)
        elif upass!=ucpass:
            context['errmsg']=" password and confirm password should be same"
            return render(request,'register.html',context) 
        else:
            try:
                u=User.objects.create(password=upass,username=uname,email=uname)
                u.set_password(upass) #show password in encrypted format
                u.save()
                context['success']="User Created Successfully, Please Login"
                return render(request,'register.html',context)
                #return HttpResponse("User created successfully")
            except Exception:
                context['errmsg']="User with same username already Exist!"  
                return render(request,'register.html',context) 
    else:
        return render(request,'register.html')

def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        context={}
        if uname=="" or upass=="" :
                context['errmsg']="Fields can not be empty"
                return render(request,'login.html',context)
        #print(uname,upass)
        #return HttpResponse("data is fetched")
        else:
            u=authenticate(username=uname, password=upass)
            #print(u) #u is object
            #print(u.username)
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalide Username And Password"
                return render(request,'login.html',context)

            #return HttpResponse("data is fetched")
        
    else:
        return render(request,'login.html')       
    

def contact(request):
    return render (request,'contact.html')

def about(request):
    return render (request,'about.html')

def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def colorfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(color=cv)
    p=product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def brandfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(name=cv)
    p=product.objects.filter(q1 & q2)
    print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)


def sort(request,sv):
    if sv =='0':
        col='price'   #asc
    else:
        col='-price'  #desending order    
    #p=product.objects.order_by(col) 
    p=product.objects.filter(is_active=True).order_by(col) 
    context={}
    context['products']=p
    return render(request,'index.html',context) 

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)
    #print(min)
    #print(max)
   # return HttpResponse("Value fetched")

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        #print(userid)
        #print(pid)
        
        u=User.objects.filter(id=userid)#queryset---list
        print(u[0])
        p=product.objects.filter(id=pid)
        print(p[0])
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        context['products']=p
        if n == 1:
            context['msg']="Product is already present in the cart"
            return render(request,'product_details.html',context)
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['success']="Product added successfully to cart "
            return render(request,'product_details.html',context)
        #return HttpResponse("Data is fetched") 
    else:
        return redirect('/login')
 

def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    s=0
    np=len(c)
    for x in c:
        s=s+x.pid.price*x.qty
    print(s)    
    #print(c)
    #print(c[0])
    #print(c[0].pid) #product object (3)
    #print(c[0].uid) #user object
    #print(c[0].pid.name)
    #print(c[0].pid.price)
    #print(c[0].uid.username)
    context={}
    context['n']=np
    context['total']=s
    context['data']=c
    return render(request,'cart.html',context)

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)

    if qv == '1':
        t=c[0].qty +1
        c.update(qty=t)
    else:
        if c[0].qty > 1:
            t=c[0].qty - 1
            c.update(qty=t)
    return redirect("/viewcart")

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=request.user.id)  
    context={}
    context['data']=orders
    np=len(orders) 
    s=0
    for x in orders:
        s=s+x.pid.price*x.qty
    context['total']=s
    context['n']=np    

    return render(request,'placeorder.html',context)



"""
def makepayment(request):
        orders=Order.objects.filter(uid=request.user.id)
        s=0
        np=len(orders)
        for x in orders:
            s=s+x.pid.price*x.qty
            oid=x.order_id
            
        client = razorpay.Client(auth=("rzp_test_SceFM4xg1JPGQg", "FGAn1kAS9CWLsFTeFuXNj4WJ"))

        data = { "amount": s*100, "currency": "INR", "receipt": oid }
        payment = client.order.create(data=data)
        #print(payment)
        context={}
        context['data']=payment
        #return HttpResponse("Success")
        return render(request,'pay.html',context)
 """

def makepayment(request):
    uemail=request.user.username
    print(uemail)
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s+x.pid.price*x.qty 
        oid=x.order_id
    
    client = razorpay.Client(auth=("rzp_test_SceFM4xg1JPGQg", "FGAn1kAS9CWLsFTeFuXNj4WJ"))

    data = { "amount": s*100 , "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    #print(payment)
    #return HttpResponse("success") 
    context={}
    context['data']=payment
    uemail=request.user.username
    print(uemail)
    context['uemail']=uemail
    return render(request,'pay.html',context) 

def sendusermail(request,uemail):
    #uemail=request.user.mail
    #print(uemail)
    send_mail(
        "Ekart-order placed succesfully.",
        "Ordered items will be delivered by 10 days",
        "rini1331989@gmail.com",
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("mail send succesfully")