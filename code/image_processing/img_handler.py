"""
This module is intended to contain only class definitions related to image processing.

Classes:
    ImageHandler: A class for managing and loading images from a directory.
"""
try:
    import os
    import cv2
    import skimage.io
    import logging
    from termcolor import colored
    import numpy as np
    from PIL import Image
    import random
    from log_utils import LogColors
except ImportError as e:
    raise ImportError(f"{e}. Please run 'pip install -r requirements.txt'") from None
 
# WARNING = 'magenta'
# ERROR = 'red'
# MESSAGE = 'green'

class ImageHandler:
    SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.ico']

    def __init__(self, dir_name="data", extensions=['.png', '.jpg'], lib='skimage.io', color_mode='rgb', log_level=logging.WARNING):
        logging.basicConfig(level=log_level)
        self.dir_path = os.path.join(os.getcwd(), dir_name)
        self.extensions = ['.' + e if not e.startswith('.') else e for e in extensions]

        for ext in self.extensions:
            if ext not in self.SUPPORTED_EXTENSIONS:
                raise UnsupportedExtensionException(ext)
            
        self.lib = lib
        self.color_mode = color_mode
        self.image_paths = self.get_image_paths()
        self.images = []
        self.metadata = [] # This will store metadata for each image path

    def get_image_paths(self):
        if not os.path.isdir(self.dir_path):
            logging.error(colored(f"The specified directory {self.dir_path} does not exist. Please check the directory path.", LogColors.ERROR, attrs=["dark"]))
            raise InvalidDirectoryError(self.dir_path)
        
        image_paths = []
        image_counts = {}  # Initialize the dictionary
        for root, _, files in os.walk(self.dir_path):
            dir_name = os.path.basename(root)
            image_counts[dir_name] = 0  # Initialize count to 0 for each directory
            for file in files:
                if os.path.splitext(file)[1] in self.extensions:
                    if not self.is_image_black(os.path.join(root, file)):
                        image_paths.append(os.path.join(root, file))
                        image_counts[dir_name] += 1  # Increment count when a non-black image is found

            # count = sum([os.path.splitext(file)[1] in self.extensions for file in files])
            # if count > 0:  # Only include directories with images
            #     dir_name = os.path.basename(root)
            #     image_counts[dir_name] = count
            # for file in files:
            #     if os.path.splitext(file)[1] in self.extensions:
            #         if not self.is_image_black(os.path.join(root, file)):
            #             image_paths.append(os.path.join(root, file))
            #         else:
            #             count -= 1
        logging.info(colored(" Path walk done.", LogColors.MESSAGE, attrs=["dark"]))
        for dir_path, count in image_counts.items():
            logging.info(colored(f"   Number of images in {dir_path}: {count}", LogColors.MESSAGE, attrs=["dark"]))

        return image_paths
    
    def is_valid_image(self, img, image_path):
        return (
            self._is_image_readable(img, image_path) and
            self._is_image_has_valid_dimensions(img, image_path) and
            self._is_image_not_empty(img, image_path)
        )

    def _is_image_readable(self, img, image_path):
        if img is None:
            logging.warning(colored(f"Warning: The image {image_path} could not be read.", LogColors.WARNING, attrs=["dark"]))
            return False
        return True

    def _is_image_has_valid_dimensions(self, img, image_path):
        if img.ndim not in [2, 3, 4]:
            logging.warning(colored(f"Warning: The image {image_path} is not in the expected format.", LogColors.WARNING, attrs=["dark"]))
            return False
        return True

    def _is_image_not_empty(self, img, image_path):
        if min(img.shape) == 0:
            logging.warning(colored(f"Warning: The image {image_path} has a dimension of zero.", LogColors.WARNING, attrs=["dark"]))
            return False
        return True
    
    def get_image_index(self, image_path):
        """
        Get the index of a given image path.

        Parameters:
        - image_path (str): The path to the image file.

        Returns:
        - int: The index of the image path in the list, or -1 if the image path is not found.
        """
        try:
            return self.image_paths.index(image_path)
        except ValueError:
            logging.error(colored(f"Image path {image_path} not found in the list.", LogColors.ERROR, attrs=["dark"]))
            return -1
        
    def load_image_cv2(self, image_path):
        if self.color_mode == 'rgb':
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        else:  # default to grayscale
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return img
    
    def load_image_pillow(self, image_path):
        with Image.open(image_path) as img:
            if self.color_mode == 'rgb':
                img = img.convert("RGB")
            elif self.color_mode == 'rgba':
                img = img.convert("RGBA")
            else:
                img = img.convert("L")  # default to grayscale
        img = np.array(img)
        return img
    
    def load_image_skimage(self, image_path):
        img = skimage.io.imread(image_path)
        return img
    
    def is_image_black(self, image_path, threshold=10):
        """
        Determines if an image is black by averaging the pixel values.
        A low average value indicates a dark image.

        Args:
            image_path (str): Path to the image.
            threshold (int): Pixel average below which an image is considered black.

        Returns:
            bool: True if the image is black, False otherwise.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read image in grayscale mode
        avg_pixel_value = img.mean()  # Calculate average pixel value

        if avg_pixel_value < threshold:
            return True
        else:
            return False

    def load(self, num_images=None):
        """
        Load a specified number of images from the paths obtained from get_image_paths method.
        The method checks if the images are valid before adding them to the images list.
        Logs an error message and returns if there are no valid image paths or an unsupported library is used.
        If there are valid images, it logs the number of images loaded and their dimensions.
        """
        image_paths = self.image_paths
        if not image_paths:
            raise ImageNotFoundException(self.dir_path)
        
        if num_images is not None:
            if num_images > len(image_paths):
                logging.warning(colored("Requested more images than available. Loading all images.", LogColors.WARNING, attrs=["dark"]))
            else:
                image_paths = random.sample(image_paths, num_images)  # Select a random subset of image paths
                logging.info(colored(f" Requested {num_images} images. Loading all these images: { [os.path.basename(ip) for ip in image_paths]}.", LogColors.MESSAGE, attrs=["dark"]))
        
        for image_path in image_paths:
            if self.lib == 'cv2':
                img = self.load_image_cv2(image_path)
            elif self.lib == 'Pillow':
                img = self.load_image_pillow(image_path)
            elif self.lib == 'skimage.io': # default to skimage.io
                img = self.load_image_skimage(image_path)
            else:
                raise UnsupportedLibraryException(self.lib)

            if self.is_valid_image(img, image_path)  and not self.is_image_black(image_path):
                self.images.append(img)
                logging.info(colored(f" {num_images} images loaded.", LogColors.MESSAGE, attrs=["dark"]))
                print(image_path)
                self.load_exif_metadata(image_path)  # Load EXIF metadata for the image
            else:
                self.image_paths.remove(image_path)
        
        if not self.images:
            logging.error(colored("No valid images found to process. Please verify the images.", LogColors.ERROR, attrs=["dark"]))
        else:
            logging.info(colored(f" - {len(self.images)} images loaded, with shape {self.images[0].shape}", LogColors.MESSAGE, attrs=["dark"]))
    

    def load_sequence(self, start_index=0, num_images=None):
        """
        Load the images from the paths obtained from get_image_paths method.
        The method checks if the images are valid before adding them to the images list.
        Logs an error message and returns if there are no valid image paths or an unsupported library is used.
        If there are valid images, it logs the number of images loaded and their dimensions.
        """
        image_paths = self.get_image_paths()
        if not image_paths:
            raise ImageNotFoundException(self.dir_path)
        
        if num_images is None:
            num_images = len(image_paths) - start_index  # load all images from start_index to end
        elif start_index + num_images > len(image_paths):
            num_images = len(image_paths) - start_index  # adjust num_images if it exceeds the list boundaries

        loaded_image_filenames = []
        image_loaded = False
        for image_path in image_paths[start_index : start_index + num_images]:
            if self.lib == 'cv2':
                img = self.load_image_cv2(image_path)
                image_loaded = True
            elif self.lib == 'Pillow':
                img = self.load_image_pillow(image_path)
                image_loaded = True
            elif self.lib == 'skimage.io':  # default to skimage.io
                img = self.load_image_skimage(image_path)
                image_loaded = True
            else:
                raise UnsupportedLibraryException(self.lib)

            if self.is_valid_image(img, image_path):
                self.images.append(img)
                self.load_exif_metadata(image_path)  # Load EXIF metadata for the image
            
            if image_loaded:
                loaded_image_filenames.append(image_path)

        if not self.images:
            logging.error(colored("No valid images found to process. Please verify the images.", LogColors.ERROR, attrs=["dark"]))
        else:
            logging.info(colored(f" - {len(self.images)} images loaded, with shape {self.images[0].shape}", LogColors.MESSAGE, attrs=["dark"]))
            logging.info(colored(f"     {[os.path.basename(lif) for lif in loaded_image_filenames]}", LogColors.MESSAGE, attrs=["dark"]))



    def extract_coordinates(self, gps_data):
        try:
            latitude_ref = gps_data[1]
            latitude = self.convert_gps_coordinate(latitude_ref, gps_data[2])
            longitude_ref = gps_data[3]
            longitude = self.convert_gps_coordinate(latitude_ref, gps_data[4])
            return latitude_ref, latitude, longitude_ref, longitude
        except (KeyError, TypeError):
            logging.warning(colored("GPS data not available or invalid.", LogColors.WARNING, attrs=["dark"]))
            return None, None, None, None
    
    def convert_gps_coordinate(self, ref, coordinate):
        """
        Convert GPS coordinates from degrees/minutes/seconds to decimal degrees.

        Parameters:
        - ref (str): The reference direction ('N', 'S', 'E', or 'W').
        - coordinates (tuple): The GPS coordinates in the form (degrees, minutes, seconds).

        Returns:
        - float: The converted GPS coordinates in decimal degrees (unit: degrees).
        """
        degrees = coordinate[0][0] / coordinate[0][1]
        minutes = coordinate[1][0] / coordinate[1][1]
        seconds = coordinate[2][0] / coordinate[2][1]
        decimal_degrees = degrees + minutes / 60 + seconds / 3600

        if ref == 'S' or ref == 'W':
            decimal_degrees = -decimal_degrees

        return decimal_degrees

    def load_exif_metadata(self, image_path):
        """
        Load EXIF metadata for a given image and print it.

        Parameters:
        - image_path (str): The path to the image file.

        Returns:
        - dict: The metadata for the image.
        
        Raises:
        - OSError: If the image cannot be opened.
        - AttributeError: If the image does not have the _getexif attribute.
        - KeyError: If the GPS info is not available in the image metadata.
        """
        metadata = {}

        try:
            with Image.open(image_path) as image:
                try:
                    exif_data = image._getexif()

                    if exif_data is not None:
                        metadata["ImageWidth"] = exif_data.get(256)
                        metadata["ImageLength"] = exif_data.get(257)
                        metadata["Make"] = exif_data.get(271)
                        metadata["DateTime"] = exif_data.get(306)

                        if 34853 in exif_data:
                            gps_data = exif_data[34853]
                            metadata["GPSLatitudeRef"], metadata["GPSLatitude"], metadata["GPSLongitudeRef"], metadata["GPSLongitude"] = self.extract_coordinates(gps_data)
                        else:
                            metadata["GPSLatitudeRef"], metadata["GPSLatitude"], metadata["GPSLongitudeRef"], metadata["GPSLongitude"] = None, None, None, None

                except (AttributeError, KeyError) as e:
                    logging.warning(f"Error occurred while loading metadata for image {image_path}: {e}")

        except (OSError, AttributeError, KeyError) as e:
            logging.warning(f"Error occurred while loading metadata for image {image_path}: {e}")
        
        self.metadata.append(metadata)
        return metadata

    def resize_images(self, size):
        resized_images = []
        for image in self.images:
            resized_image = cv2.resize(image, size)
            resized_images.append(resized_image)
        return resized_images

    def crop_images(self, coordinates):
        cropped_images = []
        for image in self.images:
            x, y, width, height = coordinates
            cropped_image = image[y:y+height, x:x+width]
            cropped_images.append(cropped_image)
        return cropped_images

    def normalize_images(self):
        normalized_images = [cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX) for image in self.images]
        return normalized_images




class InvalidDirectoryError(Exception):
    """
    Exception raised when a non-existent directory is given to ImageHandler.
    """
    def __init__(self, directory):
        self.directory = directory
        self.message = colored(f"The specified directory {self.directory} does not exist. Please check the directory path.", LogColors.ERROR, attrs=["dark"])
        super().__init__(self.message)


class UnsupportedLibraryException(Exception):
    """
    Exception raised when an unsupported library is used.
    """
    def __init__(self, lib, message=colored(f"Unsupported library. Please use 'cv2' or 'skimage.io'.", LogColors.ERROR, attrs=["dark"])):
        self.lib = lib
        self.message = colored(f"Unsupported library '{lib}'. Please use 'cv2', 'Pillow', or 'skimage.io'.", LogColors.ERROR, attrs=["dark"])
        super().__init__(self.message)


class ImageNotFoundException(Exception):
    """
    Exception raised when no images are found to process.
    """
    def __init__(self, directory, message=colored("No images found to process. Please verify the directory and file extensions.", LogColors.ERROR, attrs=["dark"])):
        self.directory = directory
        self.message = f"{message}: {directory}"
        super().__init__(self.message)


class UnsupportedExtensionException(Exception):
    """
    Exception raised when an unsupported image extension is used.
    """
    def __init__(self, ext):
        self.ext = ext
        self.message = colored(f"Unsupported image extension '{ext}'. Please use one of {ImageHandler.SUPPORTED_EXTENSIONS}.", LogColors.ERROR, attrs=["dark"])
        super().__init__(self.message)
