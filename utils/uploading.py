class ImageUploadHelper:
    """
    Построение путей сохранения изображений для моделей:
    Member, Artist, Album, ImageGallery, ...
    """

    FILED_TO_COMBINE_MAP = {
        'defaults': {
            'upload_postfix': 'uploads'
        },
        'Member': {
            'field': 'slug',
            'upload_postfix': 'members_images'
        },
        'Artist': {
            'field': 'slug',
            'upload_postfix': 'artists_images'
        },
        'Album': {
            'field': 'slug',
            'upload_postfix': 'albums_images'
        },
        'ImageGallery': {
            'field': 'slug',
            'upload_postfix': 'gallery_images'
        },
    }

    def __init__(self, field_name_to_combine, instance, filename,
                 upload_postfix):
        self.field_name_to_combine = field_name_to_combine
        self.instance = instance
        self.extension = filename.split('.')[-1]
        self.upload_postfix = f'_{upload_postfix}'

    @classmethod
    def get_field_to_combine_and_upload_postfix(cls, klass):
        """Получить имя поля и постфикс из списка диктов"""
        # klass = Member, Artist or Album
        field_to_combine = cls.FILED_TO_COMBINE_MAP[klass]['field']
        upload_postfix = cls.FILED_TO_COMBINE_MAP.get(
            'upload_postfix',
            cls.FILED_TO_COMBINE_MAP['defaults']['upload_postfix']
        )
        return field_to_combine, upload_postfix

    @property
    def path(self):
        """Простроить путь для сохранения файла"""
        field_to_combine = getattr(self.instance, self.field_name_to_combine)
        filename = '.'.join([field_to_combine, self.extension])
        # self.instance.__class__.__name__.lower() = member, artist, album ...
        return (f'images/{self.instance.__class__.__name__.lower()}'
                f'{self.upload_postfix}/{field_to_combine}/{filename}')


def upload_function(instance, filename):
    if hasattr(instance, 'content_object'):
        instance = instance.content_object
    # Получить имя поля и постфикс из FILED_TO_COMBINE_MAP
    field_to_combine, upload_postfix = ImageUploadHelper. \
        get_field_to_combine_and_upload_postfix(instance.__class__.__name__)
    # Сама инстанция
    image = ImageUploadHelper(field_to_combine, instance, filename, upload_postfix)
    return image.path  # построить путь сохранения
