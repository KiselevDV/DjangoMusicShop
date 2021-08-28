from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (
    MediaType, Member, Genre, Artist, Album, CartProduct, Cart, Order,
    Customer, Notification, ImageGallery)


class MembersInline(admin.TabularInline):
    """Выбор участника, для m2m"""
    model = Artist.members.through


class ImageGalleryInline(GenericTabularInline):
    """Вывести само изображение"""
    model = ImageGallery
    readonly_fields = ('image_url',)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    inlines = [MembersInline, ImageGalleryInline]
    exclude = ('members',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [ImageGalleryInline]


admin.site.register(MediaType)
admin.site.register(Member)
admin.site.register(Genre)
# admin.site.register(Artist)
# admin.site.register(Album)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Notification)
admin.site.register(ImageGallery)

admin.site.site_header = 'Сайт "Музыкальный магазин"'
admin.site.site_title = 'Сайт интернет магазина'
