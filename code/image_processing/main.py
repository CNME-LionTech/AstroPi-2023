import os
import img_handler as handle
import img_processor as process
import img_renderer as render
import log_processor as lp
import logging
from termcolor import colored
from log_utils import LogColors

logging.basicConfig(level=logging.WARNING)

datalog = lp.ISSInstance()
# datalog.load_csvs_from_directory("data")
# data = datalog.df
# print(data)
# print(datalog.get_field_types())
# print(datalog.get_position_at_time(data['timestamp'][5]))

# handle = handle.ImageHandler("data", ['.png', '.jpg'], lib='skimage.io', color_mode='rgb')
# handle.load(num_images = 3)
# image_processor = process.ImageProcessor(handle.images)  # 'images' is a list of images
# image_renderer = render.ImageRenderer(handle.images, [[] for _ in handle.images])
# # processed = process.ImageProcessor(images)
# if len(image_processor.images) > 0:
#     orig = image_processor.images[0]
# else:
#     logging.error(colored("No images were loaded. Cannot proceed.", 'red', attrs=["dark"]))
# print(f"Folder with date stamp found. Epoch time is {datalog.extract_datetime_from_dirlist(handle.image_paths)}")
# # hist = processed.histogram_equalization(orig)
# # processed.compare_images(orig, hist)
# # sharp = processed.image_sharpening(orig)
# # processed.compare_images(orig, sharp)
# # median = processed.apply_kernel(orig, 'emboss')
# # processed.compare_images(orig, median)
# # image_renderer.render_image(orig, 'matplotlib')
# # renderer.render_image(sharp, 'cv2')
# # renderer.render_image(median, 'cv2')

# # image_processor = ImageProcessor(images)  # 'images' is a list of images

# # Define the processing functions to apply
# processing_functions = [image_processor.median_filtering,
#                        image_processor.bilateral_filtering,
#                        image_processor.histogram_equalization, 
#                        image_processor.apply_kernel
#                        ]

# # Define the argument lists for each processing function
# args_list = [
#     ('kernel_size',),                    # No arguments for median_filtering
#     ('d', 'sigma_color', 'sigma_space'),  # Arguments for bilateral_filtering
#     ('threshold',),                      # Keyword argument for edge_detection
#     ('kernel_name',),                    # Argument for kernel
# ]

# # Define the argument lists for each processing function
# kwargs_list = [
#     (5,),            # No arguments for median_filtering
#     (9, 75, 75),  # Arguments for bilateral_filtering
#     (50,),           # Keyword argument for edge_detection
#     ("emboss",)      # Argument for kernel
# ]


# image_processor.process_all_images(processing_functions, args_list, kwargs_list)
# # img_renderer = render.ImageRenderer(image_processor.images)
# # # # image_processor.display_all()
# # # for i, (intermediate_images, image_history) in enumerate(zip(image_processor.processed_images, image_processor.history)):
# # #     for j, (image, processing_step) in enumerate(zip(intermediate_images, image_history)):
# # #         img_renderer = render.ImageRenderer([image])  # Need to pass a list of images
# # #         img_renderer.render_image(0, method='matplotlib', title=f"Image {i+1}, Step {j+1}: {processing_step}")

# # for i, (intermediate_images, image_history) in enumerate(zip(image_processor.processed_images, image_processor.history)):
# #     img_renderer = render.ImageRenderer(intermediate_images)
# #     img_renderer.render_all(method='matplotlib', history=image_history)

# # After processing, we get the processed images and history
# processed_images = image_processor.processed_images
# processing_history = image_processor.history

# # Create an instance of the ImageRenderer with the processed images and processing history
# image_renderer = render.ImageRenderer(processed_images, processing_history)
# num_images = image_renderer.get_image_number()
# print(f"There are {num_images} images.")

# processing_steps = image_renderer.get_processing_steps()
# for i, step in enumerate(processing_steps):
#     print(f"Processing step for image {i+1}: {step}")

# # Render a sequence of images starting from index 0, and displaying 4 images
# print(processing_history)
# print(f" image of {processed_images[0][0]}")
# print(image_processor.is_image_black(processed_images[0][0]))
# image_renderer.render_image_sequence_grid(img_idx=0, start_idx=0, sequence_length=5)


handle = handle.ImageHandler("data", ['.png', '.jpg'], lib='skimage.io', color_mode='rgb')
handle.load_sequence(start_index= 180, num_images = 2)
# print(handle.image_paths)
img_processor = lp.ImgProcessing()

p0 = img_processor.detect_features(handle.images[0])


cloud_height = img_processor.estimate_cloud_height(handle.images[0], handle.images[1], 1, p0)

print(f'The estimated cloud height is {cloud_height} meters.')
print(handle.images)
image_renderer = render.ImageRenderer(handle.images, [[] for _ in handle.images])