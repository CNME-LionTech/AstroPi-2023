"""
This module is intended to contain only class definitions related to image processing.

Classes:
    ImageProcessor: A class for performing various preprocessing steps on images.
"""

try:
    import os
    import urllib
    import numpy as np
    import matplotlib.pyplot as plt
    import cv2
    import json
    import logging
    logging.basicConfig(level=logging.INFO)
except ImportError as e:
    raise ImportError(f"{e}. Please run 'pip install -r requirements.txt'") from None

class ImageProcessor:
    def __init__(self, images, kernels_filepath='kernels.json'):
        """
        Initializes an ImageProcessor instance with a list of images to be processed.
        
        Parameters:
        images (list of numpy.ndarray): The list of input images to be processed. 
            Each image should be a numpy.ndarray representing the pixel intensities 
            of the image. 
        
        Attributes:
        images (list of numpy.ndarray): Stores the original images.
        processed_images (list of numpy.ndarray): Stores the processed images. 
            Initialized as an empty list, it will be populated when process_images() 
            is called.
        kernels (dict): Stores the kernels to be used for image processing. 
            Each key is a string representing the kernel's name, and the corresponding 
            value is a numpy.ndarray representing the kernel. 

        The predefined kernels are as follows:
        - "sharpen": Sharpens the image.
        - "laplacian": Highlights regions of rapid intensity change (edges).
        - "edge_detect": Detects edges in the image.
        - "gaussian_blur": Blurs the image using a Gaussian filter.
        - "emboss": Embosses the image.
        - "sobel_x": Detects horizontal edges using the Sobel operator.
        - "sobel_y": Detects vertical edges using the Sobel operator.
        - "prewitt_x": Detects horizontal edges using the Prewitt operator.
        - "prewitt_y": Detects vertical edges using the Prewitt operator.
        """
        self.images = images
        # Checking if all images are numpy.ndarray instances
        for image in images:
            if not isinstance(image, np.ndarray):
                raise ValueError(f"Each image must be a numpy.ndarray but got {type(image).__name__}")
        # Initialize an empty processed images entry for each image
        self.processed_images = [[] for _ in images]

        try:
            # Load kernels from json file
            with open(kernels_filepath, 'r') as f:
                kernels = json.load(f)
        except FileNotFoundError:
            logging.warning(f"File {kernels_filepath} not found. Using default kernels.")
            kernels = self.default_kernel()  # function that returns default kernels
        except json.JSONDecodeError:
            logging.warning(f"File {kernels_filepath} is not a valid JSON file. Using default kernels.")
            kernels = self.default_kernel()  # function that returns default kernels
            
        # Convert lists back to numpy arrays and apply divider
        self.kernels = {}
        for key, value in kernels.items():
            self.kernels[key] = np.array(value["values"]) / value["divider"]

        # Initialize an empty history entry for each image
        self.history = [[] for _ in images]

    @staticmethod
    def default_kernel():
        """
        Returns a dictionary with default kernels for image processing.
        """
        return {
            "original": {"values": [[0,0,0], [0,1,0], [0,0,0]], "divider": 1}
        }

    def apply_kernel(self, img: np.ndarray, kernel_name: str):
        """
        Applies a specified kernel to the given image using convolution.

        Parameters:
        img (numpy.ndarray): The input image to which the kernel should be applied.
        kernel (numpy.ndarray): The kernel to be used for convolution. This should be a square array.

        Returns:
        numpy.ndarray: The resulting image after applying the kernel.

        Raises:
        ValueError
            If the kernel name is not in the 'kernels' dictionary.

        Usage:
        Select a kernel from the predefined kernels in the 'kernels' dictionary of the ImageProcessor class.
        The keys of the dictionary represent the kernel names. Available options are:
        - "sharpen": For sharpening the image
        - "laplacian": For highlighting regions of rapid intensity change (edges)
        - "edge_detect": For edge detection in the image
        - "gaussian_blur": For blurring the image
        - "emboss" :Emboss Kernel - This kernel is used to create a three-dimensional representation of the image. It highlights the edges of the image by replacing each pixel's value with a shadow.
        - "sobel_x":  Sobel Horizontal Edge Detection Kernel
        - "sobel_y":  Sobel Vertical Edge Detection Kernel
        - "prewitt_x": Prewit Horizontal Edge Detection Kernel
        - "prewitt_y": Prewit Vertical Edge Detection Kernel

        Additional kernels can be added to the dictionary as needed. 
        Each additional kernel should be a numpy.ndarray, and it should be added to the dictionary with a unique string key.

        For example, to apply the sharpening kernel, call this method as follows:
        img_processor.apply_kernel(image, img_processor.kernels["sharpen"])
        """

        if kernel_name not in self.kernels:
            logging.warning(f"Kernel '{kernel_name}' is not defined. Applying the default kernel instead.")
            kernel = np.array(self.default_kernel()["original"]["values"]) / self.default_kernel()["original"]["divider"] 
        else:
            kernel = self.kernels[kernel_name]

        return cv2.filter2D(img, -1, kernel)
    
    def apply_all(self, img: np.ndarray, idx: int, processing_functions, args_list, kwargs_list, in_place=False):
        """
        Applies all the specified processing functions to the given image.

        Parameters:
        img (numpy.ndarray): The input image to process.
        idx (int): The index of the image in self.images and self.history.
        processing_functions (list of str): The names of the functions to apply to the image.
        args_list (list of list): List of arguments for the processing functions.
        kwargs_list (list of dict): List of keyword arguments for the processing functions.
        in_place (bool, optional): Whether to modify the original image (True) or a copy (False). Default is True.

        Raises:
        ValueError: If the number of functions doesn't match the number of argument lists or keyword argument lists.

        Returns:
        None. But modifies the `processed_images` attribute in the process.
        """
        # Check if the transformations should be applied in-place or out-of-place
        if in_place:
            img_to_process = img  # Modify the original image
        else:
            img_to_process = img.copy()  # Create a new image, leave the original unchanged

        if len(processing_functions) != len(args_list):
            raise ValueError(f"Number of functions {len(processing_functions)} does not match number of arguments {len(args_list)}")
        if len(processing_functions) != len(kwargs_list):
            raise ValueError(f"Number of functions {len(processing_functions)} does not match number of keyword arguments {len(kwargs_list)}")
        
        logging.info(f"Index: {idx}")
        logging.info(f"Processing functions: {processing_functions}")
        logging.info(f"Arguments: {args_list}")
        logging.info(f"Keyword arguments: {kwargs_list}")

        self.processed_images[idx].append(img)
        self.history[idx].append({'function': 'original'})

        for processing_function, args, kwargs in zip(processing_functions, list(args_list), kwargs_list):
            self.log(idx, processing_function, args, kwargs)  # Log the transformation

            # Construct the parameters dictionary
            params = dict(zip(args, kwargs))
            logging.info(f"    {params}")

            try:
                img_to_process = processing_function(img_to_process, **params)
            except Exception as e:
                logging.error(f"An error occurred when applying function {processing_function} with args {args} and kwargs {kwargs}. Error message: {str(e)}")
                raise ValueError(f"An error occurred when applying function {processing_function} with args {args} and kwargs {kwargs}") from e

            self.processed_images[idx].append(img_to_process)
            self.history[idx].append({"function": processing_function.__name__, "args": args, "kwargs": kwargs})

    def is_image_black(self, img: np.ndarray, threshold=10):
        """
        Determines if an image is black by averaging the pixel values.
        A low average value indicates a dark image.

        Args:
            image_path (str): Path to the image.
            threshold (int): Pixel average below which an image is considered black.

        Returns:
            bool: True if the image is black, False otherwise.
        """
        avg_pixel_value = img.mean()  # Calculate average pixel value

        if avg_pixel_value < threshold:
            return True
        else:
            return False

    def histogram_equalization(self, img, threshold=100):
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

        # equalize the histogram of the Y channel
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

        # convert the YUV image back to RGB format
        img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

        return img_output

    def median_filtering(self, img, kernel_size=5):
        """
        Applies median filtering to the image.

        Parameters:
        img (numpy.ndarray): The input image.
        size (int): Positional argument (optional). 
            If provided, the first argument will be used as the kernel size for the median filter.

        Returns:
        numpy.ndarray: The processed image.
        """
        if not isinstance(img, np.ndarray):
            raise TypeError(f"img must be a numpy.ndarray but got {type(img).__name__}")
        if not isinstance(kernel_size, int) or kernel_size <= 0:
            raise ValueError(f"size must be a positive integer but got {kernel_size}")
    
        return cv2.medianBlur(img, kernel_size)
    
    def bilateral_filtering(self, img, d, sigma_color, sigma_space):
        """
        Applies bilateral filtering to the given image.

        Parameters:
        img (numpy.ndarray): The input image to apply bilateral filtering.
        d (int): Diameter of each pixel neighborhood.
        sigma_color (float): Filter sigma in the color space.
        sigma_space (float): Filter sigma in the coordinate space.

        Returns:
        numpy.ndarray: The resulting image after applying bilateral filtering.
        """
        return cv2.bilateralFilter(img, d, sigma_color, sigma_space)



    def process_all_images(self, processing_functions, args_lists, kwargs_lists):
        """
        Apply the specified processing functions to all the images.

        Parameters:
        processing_functions (list of str): The names of the functions to apply to each image.
        args_lists (list of lists): Variable-length positional argument lists for each processing function.
        kwargs_lists (list of dicts): Variable-length keyword argument lists for each processing function.
        """
        for idx, img in enumerate(self.images):
            self.apply_all(img, idx, processing_functions, args_lists, kwargs_lists)

    def log(self, idx, processing_function, args, kwargs):
        """
        Logs the transformations applied to an image.

        Parameters:
        idx (int): The index of the image.
        processing_function (str): The name of the function applied to the image.
        args (list): The arguments used in the function.
        kwargs (dict): The keyword arguments used in the function.
        """
        logging.info(f"Index: {idx}")
        logging.info(f"  Processing function: {processing_function.__name__}")
        logging.info(f"  Arguments: {args}")
        logging.info(f"  Keyword arguments: {kwargs}")


    def load_image(self, img):
        """
        Loads an image. If the input is a numpy array, it is returned as is. If the input is a string,
        it is treated as a file path or URL and the corresponding image is loaded and returned.

        Parameters:
        img (str or numpy.ndarray): The input image, either as a numpy array, a file path, or a URL.

        Returns:
        numpy.ndarray: The loaded image.
        """
        if isinstance(img, np.ndarray):
            return img
        elif isinstance(img, str):
            if os.path.isfile(img):
                # The string is a file path
                return cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB)
            else:
                # The string is a URL
                with urllib.request.urlopen(img) as url:
                    s = url.read()
                arr = np.asarray(bytearray(s), dtype=np.uint8)
                return cv2.cvtColor(cv2.imdecode(arr, -1), cv2.COLOR_BGR2RGB)
        else:
            raise TypeError("Image input should be a numpy.ndarray, a file path or a URL.")
