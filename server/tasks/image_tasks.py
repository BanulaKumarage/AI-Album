from io import BytesIO

from PIL import Image

from server.conf import thumbnail_resolution


def convert_to_thumbnail(impath):    
    im = Image.open(impath)
    stream = BytesIO()
    im.thumbnail(thumbnail_resolution)
    im.save(stream, 'jpeg')

    return stream


def convert_to_image_stream(impath):    
    im = Image.open(impath)
    stream = BytesIO()
    im.save(stream, 'jpeg')

    return stream
