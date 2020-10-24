
from django.urls import path
from . import views

urlpatterns = [
  
    path('',views.index,name='index'),
    path('contact/',views.contact,name='contact'),
    path('signup/',views.signup, name='signup'),
    path('login/',views.login,name='login'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('logout/',views.logout,name='logout'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('sendotp/',views.sendotp,name='sendotp'),
    path('newpassword/',views.new_password,name='new_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('profile/',views.profile,name='profile'),    
    path('enter_email/',views.enter_email,name='enter_email'),
    path('validate_mail/',views.validate_mail,name='validate_mail'),
    path('update_pic/',views.update_pic,name="update_pic"),
    path('add_product/',views.add_product,name='add_product'),
    path('view_product/',views.view_product,name='view_product'),
    path('product_details/<int:pk>/',views.product_details,name='product_details'),
    path('product_unavailable/<int:pk>/',views.product_unavailable,name='product_unavailable'),
    path('get_unavailable/',views.get_unavailable,name='get_unavailable'),
    path('get_available/',views.get_available,name='get_available'),
    path('edit_product/<int:pk>/',views.edit_product,name='edit_product'),
    path('all_product/',views.all_product,name='all_product'),
    path('fashion/',views.fashion,name='fashion'),
    path('electronic/',views.electronic,name='electronic'),
    path('mobile/',views.mobile,name='mobile'),
    path('user_product_details/<int:pk>/',views.user_product_details,name='user_product_details'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('mywishlist/',views.mywishlist,name='mywishlist'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('mycart/',views.mycart,name='mycart'),
    path('remove_from_wishlist/<int:pk>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('update_q/<int:pk>/',views.update_q,name='update_q'),
    path('pay/',views.initiate_payment, name='pay'),
    path('callback/',views.callback,name='callback'),
]

