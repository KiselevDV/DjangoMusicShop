from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from utils import upload_function


class MediaType(models.Model):
    """Медианоситель"""

    name = models.CharField(
        max_length=100, verbose_name='Название медианосителя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Медианоситель'
        verbose_name_plural = 'Медианосители'


class Member(models.Model):
    """Музыкант"""

    name = models.CharField(max_length=255, verbose_name='Имя музыканта')
    image = models.ImageField(
        upload_to=upload_function, null=True, blank=True,
        verbose_name='Аватарка')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Музыкант'
        verbose_name_plural = 'Музыканты'


class Genre(models.Model):
    """Музыкальный жанр"""

    name = models.CharField(max_length=50, verbose_name='Название жанра')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Artist(models.Model):
    """Исполнитель"""

    name = models.CharField(max_length=255, verbose_name='Исполнитель/группа')
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, verbose_name='Жанр')
    members = models.ManyToManyField(
        Member, related_name='artist', verbose_name='Участник')
    image = models.ImageField(
        upload_to=upload_function, null=True, blank=True,
        verbose_name='Аватарка')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def get_absolute_url(self):
        return reverse('artist_detail', kwargs={'artist_slug': self.slug})

    def __str__(self):
        return f'{self.name} | {self.genre.name}'

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class Album(models.Model):
    """Альбом исполнителя"""

    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, verbose_name='Исполнитель')
    name = models.CharField(max_length=255, verbose_name='Название альбома')
    description = models.TextField(
        max_length=15000, default='', verbose_name='Описание')
    image = models.ImageField(
        upload_to=upload_function, verbose_name='Обложка')
    media_type = models.ForeignKey(
        MediaType, on_delete=models.CASCADE, verbose_name='Носитель')
    songs_list = models.TextField(max_length=15000, verbose_name='Треклист')
    release_date = models.DateField(verbose_name='Дата релиза')
    price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveSmallIntegerField(
        default=0, verbose_name='Наличие товара на складе')
    offer_of_the_week = models.BooleanField(
        default=False, verbose_name='Предложение недели!?!?')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    @property
    def ct_model(self):
        """Наименование модели (content_type)"""
        return self._meta.model_name

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={
            'artist_slug': self.artist.slug,
            'album_slug': self.slug
        })

    def __str__(self):
        return f'{self.id} | {self.artist.name} | {self.name}'

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'


class CartProduct(models.Model):
    """
    Продукт для корзины - копия продукта которую, в последующем можно
    добавить в корзину. Промежуточная модель между товаром и корзиной
    """

    user = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    cart = models.ForeignKey(
        'Cart', on_delete=models.CASCADE, verbose_name='Корзина')
    qty = models.PositiveSmallIntegerField(
        default=1, verbose_name='Количество')
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Общая цена')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        """Получить полную стоимость"""
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Продукт: {self.content_object.name} (для корзины)'

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Cart(models.Model):
    """Корзина"""

    owner = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    products = models.ManyToManyField(
        CartProduct, related_name='related_cart', blank=True,
        verbose_name='Продукты для корзины')
    total_products = models.PositiveSmallIntegerField(
        default=0, verbose_name='Всего товаров в корзине')
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(
        default=False, verbose_name='Уже используется')
    for_anonymous_user = models.BooleanField(
        default=False, verbose_name='Для зарегистрированного пользователя')

    def __str__(self):
        return f'Корзина № {str(self.id)}, для покупателя {self.owner}'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    """Заказы пользователя"""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен покупателем')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, related_name='orders',
        verbose_name='Покупатель')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, verbose_name='Корзина')
    address = models.CharField(
        max_length=1024, null=True, blank=True, verbose_name='Адрес')
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_NEW,
        verbose_name='Статус заказа')
    buying_type = models.CharField(
        max_length=100, choices=BUYING_TYPE_CHOICES, verbose_name='Тип заказа')
    comment = models.TextField(
        max_length=15000, null=True, blank=True,
        verbose_name='Комментарий к заказу')
    created_at = models.DateField(
        auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(
        default=timezone.now, verbose_name='Дата получения заказа')

    def __str__(self):
        return f'Заказ № {str(self.id)}, от пользователя {self.customer}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Customer(models.Model):
    """Покупатель"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Пользователь')
    is_active = models.BooleanField(default=True, verbose_name='Активный?')
    customer_orders = models.ManyToManyField(
        Order, related_name='related_customer', blank=True,
        verbose_name='Заказы покупателя')
    wishlist = models.ManyToManyField(
        Album, blank=True, verbose_name='Список ожидаемого')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Адрес')

    def __str__(self):
        if not (self.user.first_name and self.user.last_name):
            return self.user.username
        return f'Покупатель: {self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Notification(models.Model):
    """Уведомления"""

    recipient = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField(max_length=10000, verbose_name='Сообщение')
    read = models.BooleanField(default=False, verbose_name='Прочитано?')

    def __str__(self):
        return (f'Уведомление для {self.recipient.user.username}'
                f' | id={str(self.id)}')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class ImageGallery(models.Model):
    """Галерея изображений"""

    image = models.ImageField(upload_to=upload_function, verbose_name='Фото')
    use_in_slider = models.BooleanField(
        default=False, verbose_name='Для слайдера')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def image_url(self):
        return mark_safe(
            f'<img src="{self.image.url}" width="auto" height="200px">')

    def __str__(self):
        return f'Изображение для {self.content_object}'

    class Meta:
        verbose_name = 'Галерея изображений'
        verbose_name_plural = verbose_name
