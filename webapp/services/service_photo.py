import uuid
import os

from webapp.config import UPLOAD_PATH, ALLOWED_IMAGE


def allowed_file(photos):
    for photo in photos:
        photo_name = photo.filename
        extension = photo_name.split('.')[-1]
        if extension not in ALLOWED_IMAGE:
            return True
            

def save_files(photos):

    photos_path = []

    for photo in photos:
        photo_name = photo.filename
        unique_filename = str(uuid.uuid4())
        extension = photo_name.split('.')[-1]
        photo_name_ext = f'{unique_filename}.{extension}'
        photo.save(os.path.join(UPLOAD_PATH, 'media', photo_name_ext))
        photos_path.append(os.path.join(UPLOAD_PATH, 'media', photo_name_ext))
    
    return photos_path