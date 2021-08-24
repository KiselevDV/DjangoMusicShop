from django.contrib import admin

from .models import (
    MediaType, Member, Genre, Artist, Album, CartProduct, Cart, Order,
    Customer, Notification, ImageGallery)

admin.site.register(MediaType)
admin.site.register(Member)
admin.site.register(Genre)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Notification)
admin.site.register(ImageGallery)

admin.site.site_header = 'Сайт "Музыкальный магазин"'
admin.site.site_title = 'Сайт интернет магазина'
