from uuid import uuid4


def get_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if instance.pk:
        filename = 'user_photos/{}.{}'.format(instance.pk, ext)
    else:
        filename = 'user_photos/{}.{}'.format(uuid4().hex, ext)
    return filename
