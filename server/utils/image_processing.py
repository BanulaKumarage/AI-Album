from io import BytesIO

from PIL import Image, ExifTags

from server.conf import thumbnail_resolution


ORIENTATION_FLAG = [k for k, v in ExifTags.TAGS.items() if v == "Orientation"][0]


def rotate_image(image: Image):
    exif = image.getexif()

    if ORIENTATION_FLAG not in exif:
        return image
    elif exif[ORIENTATION_FLAG] == 3:
        image = image.rotate(180, expand=True)
    elif exif[ORIENTATION_FLAG] == 6:
        image = image.rotate(270, expand=True)
    elif exif[ORIENTATION_FLAG] == 8:
        image = image.rotate(90, expand=True)

    return image


def crop_image(image: Image, top, right, bottom, left):
    return image.crop((left, top, right, bottom))


def convert_to_thumbnail(impath, top, right, bottom, left):
    im = Image.open(impath)

    if all([top >= 0, right >= 0, bottom >= 0, left >= 0]):
        im = crop_image(im, top, right, bottom, left)

    im = rotate_image(im)
    stream = BytesIO()
    im.thumbnail(thumbnail_resolution)
    im.save(stream, "jpeg")

    return stream


def convert_to_image_stream(impath):
    im = Image.open(impath)
    im = rotate_image(im)
    stream = BytesIO()
    im.save(stream, "jpeg")

    return stream
