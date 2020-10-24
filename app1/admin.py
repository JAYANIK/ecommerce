from django.contrib import admin
from .models import Contact,Registration,Product,WishList,Cart,Transaction

# Register your models here.
admin.site.register(Contact)
admin.site.register(Registration)
admin.site.register(Product)
admin.site.register(WishList)
admin.site.register(Cart)
admin.site.register(Transaction)
