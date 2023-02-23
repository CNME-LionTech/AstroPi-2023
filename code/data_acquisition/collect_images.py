from picamera import PiCamera
from datetime import datetime, timedelta
from utilities import get_file_time_stamp, create_directory_if_not_exists

PHOTO_FILE_LABEL = "LTech"

class ImageCollector:
    def __init__(self, image_dir, photo_delay=7.5):
        self.camera = PiCamera()
        self.camera.resolution = (1920, 1080)
        self.photo_counter = 1
        self.photo_delay = photo_delay
        self.photo_folder = get_file_time_stamp()
        self.last_photo_time = datetime.now()
        create_directory_if_not_exists(image_dir)
        create_directory_if_not_exists(f'{image_dir}/{self.photo_folder}')

    def capture_image(self, image_dir):
        now_time = datetime.now()
        if now_time > self.last_photo_time + timedelta(seconds=self.photo_delay):
            image_file = f'{image_dir}/{self.photo_folder}/{PHOTO_FILE_LABEL}_{self.photo_counter:04d}.jpg'
            self.camera.capture(image_file)
            self.photo_counter += 1
            self.last_photo_time = now_time
