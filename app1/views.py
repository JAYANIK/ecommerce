from django.shortcuts import render,redirect
from .models import Contact,Product,Registration,WishList,Cart,Transaction
from django.core.mail import send_mail
import random
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
# Create your views here.

#payments start here
def initiate_payment(request):
    try:
        user=Registration.objects.get(email=request.session['email'])
        amount = int(request.POST['amount'])
        
    except:        
        return render(request, 'my_cart.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


#payment end here--------------------------------


def index(request):
    return render(request,'index.html')

def seller_index(request):
    user=Registration.objects.get(email=request.session['email'])
    a_product=len(Product.objects.filter(user=user,product_stock="available"))
    un_product=len(Product.objects.filter(user=user,product_stock="unavailable"))
    all_product=len(Product.objects.filter(user=user))
    count={'a_product':a_product,'un_product':un_product,'all_product':all_product}
    return render(request,'seller_index.html',{'count':count})

def contact(request):
    if request.method == "POST":
        cn=request.POST['cname']
        e=request.POST['email']
        m=request.POST['mobile']
        f=request.POST['feedback']
        Contact.objects.create(name=cn,email=e,mobile=m,feedback=f)
        msg="Contact Saved Successfully.."
        contacts = Contact.objects.all().order_by('-id')
        return render (request,'contact.html',{'msg':msg,'contacts':contacts})

    else:
        contacts = Contact.objects.all().order_by('-id')
        return render (request,'contact.html',{'contacts':contacts})

def signup(request):
    if request.method=="POST":
        fn=request.POST['fname']
        ln=request.POST['lname']
        e=request.POST['email']
        m=request.POST['mobile']
        p=request.POST['password']
        c=request.POST['cpassword']
        utype=request.POST['usertype']
        image=request.FILES['image']
        try:
            user  = Registration.objects.get(email=e)
            if user:
                msg="Email Already Exists"
                return render (request,'signup.html',{'msg':msg})
        except:
            if p == c:
                Registration.objects.create(fname=fn,lname=ln,email=e,mobile=m,password=p,usertype=utype,image=image)
                rec = [e,]
                subject = "OTP For Successful Registration"
                otp = random.randint(1000,9999)
                message = "Hello "+fn +" Your OTP For Registration is :"+str(otp)
                email_from = settings.EMAIL_HOST_USER
                send_mail(subject,message,email_from,rec)
                msg="Check Your Mail Inbox For OTP"
                return render (request,'enterotp.html',{'otp':otp,'email':e,'msg':msg})
            else:
                msg="Password & Confirm Password not match"
                return render (request,'signup.html',{'msg':msg})
    else:
        return render(request,'signup.html')
@login_required
def verify_otp(request):    
    otp = request.POST['otp']
    uotp = request.POST['uotp']
    email = request.POST['email']
    myvar=request.POST['myvar']
    user=Registration.objects.get(email=email)
    if otp==uotp and myvar=='forgot':
        return render(request,'newpassword.html',{'email':email})  
    elif otp==uotp and myvar=="account_status":
        user.status="active"
        user.save()
        msg="Account Activated.. Now Login"
        return render(request,'login.html',{'msg':msg})
    elif otp==uotp:
        user.status="active"
        user.save()
        msg="Email Verification Successful. Login With Email & Password"
        return render(request,'login.html',{'msg':msg})
    else:
        msg="OTP is Incorrect.. Try Again"
        return render (request,'enterotp.html',{'otp':otp,'email':email,'msg':msg,'myvar':myvar})

def login(request):
    if request.method=="POST":
        e=request.POST['email']      
        p=request.POST['password']
        utype=request.POST['usertype']
        try:
            user=Registration.objects.get(email=e,password=p)
            if user.usertype=="user" and utype=="user":
                if user.status=="active":
                    request.session['fname']=user.fname
                    request.session['lname']=user.lname
                    request.session['email']=user.email
                    wishlist_len=len(WishList.objects.filter(user=user))
                    request.session['wishlist_len']=wishlist_len
                    mycart_len=len(Cart.objects.filter(user=user))
                    request.session['mycart_len']=mycart_len                    
                    if user.image=="":
                        pass
                    else:
                        request.session['image']=user.image.url
                    # return render(request,'index.html')
                    return redirect('all_product')
                else:
                   
                    msg1="Your Account is Inactive"
                    return render(request,'login.html',{'msg1':msg1})
            elif user.usertype=="seller" and utype=="seller":
                if user.status=="active":
                    request.session['fname']=user.fname
                    request.session['lname']=user.lname
                    request.session['email']=user.email
                    if user.image=="":
                        pass
                    else:
                        request.session['image']=user.image.url
                    return redirect('seller_index')
                else:
                    msg1="Your Account is Inactive"
                    return render(request,'login.html',{'msg1':msg1})
            else:
                msg="User Type is wrong.. Try again"
                return render(request,'login.html',{'msg':msg})
        except:
            msg="Email Or Password is Incorrect"
            return render(request,'login.html',{'msg':msg})

    else:
        return render(request,'login.html')

def logout(request):
    try:
        del request.session['fname']
        del request.session['lname']
        del request.session['email']
        del request.session['image']
        del request.session['wishlist_len']
        del request.session['mycart_len']
        return render(request,'index.html')
    except:
        return render(request,'index.html')

def forgotpassword(request):
    return render(request,'forgotpassword.html')

def sendotp(request):
    e=request.POST['email']
                
    try:
        user=Registration.objects.get(email=e)
        if user:
            rec = [e,]
            subject = "OTP For Successful Registration"
            otp = random.randint(1000,9999)
            message = "Your OTP For Registration is :"+str(otp)
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject,message,email_from,rec)
            msg="Check Your Mail Inbox For OTP"
            myvar="forgot"
            return render(request,'enterotp.html',{'myvar':myvar,'email':e,'otp':otp,'msg':msg})
    except:
        msg="This Email is Not Registered"
        return render(request,'forgotpassword.html',{'msg':msg})

def new_password(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        
        if password==cpassword:
            try:
                user=Registration.objects.get(email=email)
                user.password=password
                user.save()
                msg="Password Successfully Changed..."
                return render(request,'login.html',{'msg':msg})
            except:
                pass
        else:
            msg="Password & Conform Password Not Matched"
            return render(request,'newpassword.html',{'msg':msg,'email':email})
    else:
        return render(request,'newpassword.html')
@login_required
def change_password(request):
    if request.method=="POST":
        old_password=request.POST['old_password']
        new_password=request.POST['new_password']
        confirm_new_password=request.POST['confirm_new_password']
        try:
            user=Registration.objects.get(email=request.session['email'])
            if old_password==user.password:
                if new_password==confirm_new_password:
                    user.password=new_password
                    user.save()
                    return redirect('logout')
                else:
                    if user.usertype=="seller":
                        msg="New Password & Confirm New Password Not Matched"
                        return render(request,'change_password.html',{'msg':msg})
                    else:
                        msg="New Password & Confirm New Password Not Matched"
                        return render(request,'user_change_password.html',{'msg':msg})                        
            else:
                if user.usertype=="seller":
                    msg="Old Password Is Incorrect"
                    return render(request,'change_password.html',{'msg':msg})
                else:
                    msg="Old Password Is Incorrect"
                    return render(request,'user_change_password.html',{'msg':msg})
                
        except:
            pass
                    
    
    else:
        try:
            user=Registration.objects.get(email=request.session['email'])
            if user.usertype=="user":
                return render(request,'user_change_password.html')
            elif user.usertype=="seller":
                return render(request,'change_password.html')
        except:
            pass

def profile(request):
    try:
        user=Registration.objects.get(email=request.session['email'])    
        if user.usertype=="user":
            mobile=user.mobile
            email=user.email
            image=user.image.url
            return render(request,'user_profile.html',{'mobile':mobile,'email':email,'image':image})
        elif user.usertype=="seller":
            mobile=user.mobile
            email=user.email
            image=user.image.url
            return render(request,'seller_profile.html',{'mobile':mobile,'email':email,'image':image})
        else:
           return render(request,'login.html') 
    except:
        return render(request,'login.html')

def enter_email(request):
    return render(request,'enter_email.html')

def validate_mail(request):
    email=request.POST['email']
    try:
        user=Registration.objects.get(email=email)
        if user:
            rec = [email,]
            subject = "OTP For Successful Registration"
            otp = random.randint(1000,9999)
            message = "Your OTP For Account Activation is :"+str(otp)
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject,message,email_from,rec)
            msg="Check Your Mail Inbox For OTP"
            myvar="account_status"
            return render(request,'enterotp.html',{'myvar':myvar,'email':email,'otp':otp,'msg':msg})
        else:
            msg="This Email is Not Registered"
            return render(request,'enter_email.html',{'msg':msg})
    except:
        msg="This Email is Not Registered"
        return render(request,'enter_email.html',{'msg':msg})
@login_required()
def update_pic(request):
    if request.method=="POST":
        new_pic=request.FILES['image']
        email=request.POST['email']
        print("jay")
        try:
            user=Registration.objects.get(email=email)
            if user.usertype=="user":                
                user.image=new_pic
                user.save()               
                msg="Profile Picture Successfully Changed.."
                mobile=user.mobile
                email=user.email
                image=user.image.url
                del request.session['image']
                request.session['image']=user.image.url
                return render(request,'user_profile.html',{'mobile':mobile,'email':email,'image':image,'msg':msg})
            if user.usertype=="seller":                
                user.image=new_pic
                user.save()               
                msg="Profile Picture Successfully Changed.."
                mobile=user.mobile
                email=user.email
                image=user.image.url
                del request.session['image']
                request.session['image']=user.image.url
                return render(request,'seller_profile.html',{'mobile':mobile,'email':email,'image':image,'msg':msg})
            else:
                return render(request,'seller_profile.html')
        except:
            return render(request,'seller_profile.html')
    else:
        pass
@login_required
def add_product(request):
    if request.method=="POST":
        pc=request.POST['product_category']
        pn=request.POST['product_name']
        pp=request.POST['product_price']
        pd=request.POST['product_desc']
        pi=request.FILES['product_image']
        user=Registration.objects.get(email=request.session['email'])
        Product.objects.create(user=user,product_category=pc,product_name=pn,product_price=pp,product_desc=pd,product_image=pi)
        msg="Product Added Successfully"
        return render(request,'add_product.html',{'msg':msg})
    else:

        return render(request,'add_product.html')

def view_product(request):
    user=Registration.objects.get(email=request.session['email'])
    products=Product.objects.filter(user=user)
    return render(request,'view_product.html',{'products':products})

def product_details(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'product_details.html',{'product':product})

def product_unavailable(request,pk):
    product=Product.objects.get(pk=pk)
    if product.product_stock=="available":
        product.product_stock="unavailable"
    else:
        product.product_stock="available"
    product.save()
    return render(request,'product_details.html',{'product':product})

def get_unavailable(request):
    user=Registration.objects.get(email=request.session['email'])
    products=Product.objects.filter(user=user,product_stock="unavailable")
    return render(request,'unavailable_product.html',{'products':products})

def get_available(request):
    user=Registration.objects.get(email=request.session['email'])
    products=Product.objects.filter(user=user,product_stock="available")
    return render(request,'available_product.html',{'products':products})

def edit_product(request,pk):
    if request.method=="POST":
        product=Product.objects.get(pk=pk)
        product_name=request.POST['product_name']
        product_price=request.POST['product_price']
        product_desc=request.POST['product_desc']
        try:
            product_image=request.FILES['product_image']
            product.product_name=product_name
            product.product_price=product_price
            product.product_desc=product_desc
            product.product_image=product_image
            print("msg")
            product.save()
            msg="Product Updated Successfully"
            return render(request,'product_details.html',{'product':product,'msg':msg})
        except:
            product.product_name=product_name
            product.product_price=product_price
            product.product_desc=product_desc
            product.save()
            msg="Product Updated Successfully"
            return render(request,'product_details.html',{'product':product,'msg':msg})
    else:
        product=Product.objects.get(pk=pk)
        return render(request,'edit_product.html',{'product':product})

def fashion(request):
    products=Product.objects.filter(product_category='fashion',product_stock='available')
    return render(request,'show_product.html',{'products':products})

def electronic(request):
    products=Product.objects.filter(product_category='electronic',product_stock='available')
    return render(request,'show_product.html',{'products':products})

def mobile(request):
    products=Product.objects.filter(product_category='mobile',product_stock='available')
    return render(request,'show_product.html',{'products':products})

def user_product_details(request,pk):
    flag=True
    flag_cart=True
    product=Product.objects.get(pk=pk)
    
    try:
        user=Registration.objects.get(email=request.session['email'])
        mywishlist=WishList.objects.filter(user=user)    
        for i in mywishlist:
            if product.pk==i.product.pk:
                flag=False
                break

        mycart=Cart.objects.filter(user=user)
        for i in mycart:
            if product.pk==i.product.pk:
                flag_cart=False
                break
        return render(request,'user_product_details.html',{'product':product,'flag':flag,'flag_cart':flag_cart})
    except:
        return render(request,'user_product_details.html',{'product':product})

def all_product(request):    
    products=Product.objects.filter(product_stock='available')    
    return render(request,'show_product.html',{'products':products})

def add_to_wishlist(request,pk):
    user=Registration.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    mycart=Cart.objects.filter(user=user,product=product)
    if mycart:
        Cart.objects.get(user=user,product=product).delete()
        request.session['mycart_len']=len(Cart.objects.filter(user=user))
    try:
        wish=WishList.objects.get(user=user,product=product)
        if wish:
            mywishlist=WishList.objects.filter(user=user)            
            msg="Product already added in Wishlist"
            return render(request,'mywishlist.html',{'mywishlist':mywishlist,'msg':msg})        
    except:
        WishList.objects.create(user=user,product=product)
        mywishlist=WishList.objects.filter(user=user)
        wishlist_len=len(mywishlist)
        request.session['wishlist_len']=wishlist_len
        msg="Product Added to Wishlist Successfully"
        return render(request,'mywishlist.html',{'mywishlist':mywishlist,'msg':msg})

def mywishlist(request):
    user=Registration.objects.get(email=request.session['email'])
    mywishlist=WishList.objects.filter(user=user)    
    return render(request,'mywishlist.html',{'mywishlist':mywishlist})

def add_to_cart(request,pk):
    user=Registration.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    mywishlist=WishList.objects.filter(user=user,product=product)    
    if mywishlist:
        WishList.objects.get(user=user,product=product).delete()        
        request.session['wishlist_len']=len(WishList.objects.filter(user=user))
    try:
        cart=Cart.objects.get(user=user,product=product)
        if cart:
            total_amount=0
            mycart=Cart.objects.filter(user=user)  
            for i in mycart:
                total_amount=int(i.product.product_price)*int(i.quantity)+int(total_amount)        
            msg="Product already added in Cart"
            return render(request,'my_cart.html',{'mycart':mycart,'msg':msg,'total_amount':total_amount})      
    except:
        total_amount=0
        Cart.objects.create(user=user,product=product)
        mycart=Cart.objects.filter(user=user)
        mycart_len=len(mycart)
        request.session['mycart_len']=mycart_len
        for i in mycart:
            total_amount=int(i.product.product_price)*int(i.quantity)+int(total_amount) 
        msg="Product Added to Cart Successfully"        
        return render(request,'my_cart.html',{'mycart':mycart,'msg':msg,'total_amount':total_amount})
@login_required(login_url="login")
def mycart(request):
    total_amount=0
    user=Registration.objects.get(email=request.session['email'])
    mycart=Cart.objects.filter(user=user) 
    for i in mycart:
        total_amount=int(i.product.product_price)*int(i.quantity)+int(total_amount)    
    return render(request,'my_cart.html',{'mycart':mycart,'total_amount':total_amount})

def remove_from_wishlist(request,pk):
    user=Registration.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    WishList.objects.get(user=user,product=product).delete()
    request.session['wishlist_len'] = len(WishList.objects.filter(user=user))
    msg="Product Removed From Wishlist"
    return redirect('mywishlist')

def remove_from_cart(request,pk):
    user=Registration.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    Cart.objects.get(user=user,product=product).delete()
    request.session['mycart_len'] = len(Cart.objects.filter(user=user))
    msg="Product Removed From Cart"
    return redirect('mycart')

def update_q(request,pk):
    q=request.POST['quantity']
    user=Registration.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    myproduct=Cart.objects.get(user=user,product=product)
    myproduct.quantity=q
    myproduct.save()
    print(myproduct.quantity)
    return redirect('mycart')


