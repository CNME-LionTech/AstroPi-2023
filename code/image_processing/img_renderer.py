"""
This module is intended to contain only class definitions related to image processing.

Classes:
    ImageRenderer: A class for performing image rendering.
"""

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import cv2
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    import plotly.express as px
    import skimage.io
    import bokeh.plotting as bplt
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    from bokeh.io import show
    import logging
except ImportError as e:
    raise ImportError(f"{e}. Please run 'pip install -r requirements.txt'") from None

class ImageRenderer:
    def __init__(self, images, history):
        self.images = images
        self.history = history

    def render_with_matplotlib(self, image, title="Image"):
        plt.imshow(image, cmap='gray')
        plt.title(title)
        plt.axis('off')
        plt.show()

    def render_with_plotly(self, image, title="Image"):
        fig = go.Figure(data=go.Image(z=image))
        fig.update_layout(title_text=title)
        fig.show()

    def render_with_matplotlib_multy(self, title="Image"):
        num_images = len(self.images)
        fig, axs = plt.subplots(1, num_images, figsize=(15,15))
        for i, img in enumerate(self.images):
            axs[i].imshow(img, cmap='gray')
            axs[i].title.set_text(f'{title} {i+1}')
            axs[i].axis('off')
        plt.show()

    def render_with_plotly_multy(self):
        fig = make_subplots(rows=1, cols=len(self.images))
        for i, img in enumerate(self.images):
            fig.add_trace(
                go.Image(z=img), 
                row=1, col=i+1
            )
        fig.update_layout(height=600, width=600*len(self.images))
        fig.show()

    def render_with_bokeh(self, image, title="Image"):
        # Create a Bokeh figure
        p = figure(title=title, tools="", x_range=(0, image.shape[1]), y_range=(0, image.shape[0]),
                background_fill_color="#fafafa")

        # Create an RGBA image data source
        rgba_image = np.dstack((image, np.full_like(image[:, :, :1], 255)))
        source = ColumnDataSource(data=dict(image=[rgba_image]))

        # Add the image to the figure
        p.image_rgba(image='image', x=0, y=0, dw=image.shape[1], dh=image.shape[0], source=source)

        # Show the plot
        show(p)

    # OpenCV and Scikit-image don't support multi-image plots natively
    def render_with_cv2(self, img, title="Image"):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
        cv2.imshow(title, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def render_with_skimage(self, image):
        skimage.io.imshow(image)
        skimage.io.show()

    def render_all(self, method='matplotlib', history=None):
        render_method = getattr(self, f"render_with_{method}", None)
        if not callable(render_method):
            raise ValueError(f"Unknown rendering method: {method}")

        if history is None:  # If no history is provided, use default titles
            for i, img in enumerate(self.images):
                render_method(img, title=f"Image {i+1}")
        else:  # If history is provided, use it to create titles
            for i, (img, processing_step) in enumerate(zip(self.images, history)):
                render_method(img, title=f"Image {i+1}: {processing_step}")

    def render_image(self, img_or_idx, method='matplotlib', title=None):
        if isinstance(img_or_idx, int):
            if img_or_idx < 0 or img_or_idx >= len(self.images):
                raise ValueError(f"Invalid image index: {img_or_idx}. Please provide a valid index.")
            img = self.images[img_or_idx]
        elif isinstance(img_or_idx, np.ndarray):
            img = img_or_idx
        else:
            raise TypeError("Invalid type for img_or_idx. It must be either an int or a np.ndarray.")

        render_method = getattr(self, f"render_with_{method}", None)
        if not callable(render_method):
            raise ValueError(f"Unknown rendering method: {method}")

        render_method(img, title=title if title is not None else f"Image")

    def render_image_sequence_grid(self, img_idx, start_idx, sequence_length, method='matplotlib'):
        # Check if the requested image index is valid
        if img_idx < 0 or img_idx >= len(self.history):
            raise ValueError(f"Invalid image index: {img_idx}. Please provide a valid index.")
        
        image_list = self.get_processed_images_for_image(img_idx)
        image_history = self.get_processing_steps_for_image(img_idx)
        
        # Check if the requested number of images is available
        if start_idx+sequence_length > len(image_list):
            raise ValueError(f"Requested {sequence_length} images from index {start_idx}, but only {len(image_list)} images are available.")
        
        # Check if there are enough recorded processing steps
        if start_idx+sequence_length > len(image_history):
            raise ValueError(f"Requested {sequence_length} processing steps from index {start_idx}, but only {len(image_history)} steps are recorded.")

        # Only 'matplotlib' supports grid display of images
        if method != 'matplotlib':
            logging.warning(f"{method} does not support grid display of multiple images. Please use 'matplotlib'.")
            return

        # Create titles for the images based on the processing functions
        function_titles = [title.get('function', 'default_value') for title in image_history[start_idx:start_idx + sequence_length]]

        # Prepare images for the plot
        images_to_plot = image_list[start_idx:start_idx + sequence_length]

        # Determine grid size
        grid_size = (int(np.ceil(np.sqrt(sequence_length))), int(np.ceil(np.sqrt(sequence_length))))

        # If the number of images is less than the total grid size, remove the extra subplot(s)
        fig, axs = plt.subplots(*grid_size, figsize=(15, 15))
        if sequence_length < grid_size[0]*grid_size[1]:
            for ax in axs.flat[sequence_length:]:
                ax.remove()
        axs = axs.ravel()

        # Display images on the grid
        for i, (img, title) in enumerate(zip(images_to_plot, function_titles)):
            axs[i].imshow(img, cmap='gray')
            axs[i].title.set_text(title)
            axs[i].axis('off')

        plt.tight_layout()
        plt.show()



    def get_image_number(self):
        """
        Returns the number of images stored in the renderer.

        Returns:
            int: The number of images.
        """
        return len(self.images)
    
    def get_processing_steps(self):
        """
        Returns the history of processing steps for each image.

        Returns:
            list: The history of processing steps.
        """
        return self.history
    
    def get_processing_history(self):
        """
        Returns the processing steps and their history for each image.

        Returns:
            dict: A dictionary where the keys are the image indices and the values are lists of processing steps.
        """
        processing_history = {}
        for i, steps in enumerate(self.history):
            processing_history[i+1] = steps
        return processing_history

    def get_processed_images(self):
        """
        Returns the processed images.

        Returns:
            list: The processed images.
        """
        return self.images

    def get_processing_steps_for_image(self, image_idx):
        """
        Returns the sequence of processing steps for specific images.

        Args:
            image_idx (int): A list of indices of the images.

        Returns:
            list: The processing steps for the images.
        """
        if image_idx < 0 or image_idx >= len(self.history):
            raise ValueError(f"Invalid image index: {image_idx}. Please provide valid indices.")

        return self.history[image_idx]
    
    def get_processed_images_for_image(self, image_idx):
        """
        Returns the processed images for specific image indices.

        Args:
            image_idx (int): The list of image indices.

        Returns:
            list: The processed images for the specified indices.
        """
        if image_idx < 0 or image_idx >= len(self.images):
            raise ValueError(f"Invalid image index: {image_idx}. Please provide a valid index.")
    
        return self.images[image_idx]





    def histogram_with_bokeh(self, image, title="Image"):
        # Create a Bokeh histogram plot
        hist, edges = np.histogram(image.flatten(), bins='auto')
        source = ColumnDataSource(data=dict(hist=hist, edges_left=edges[:-1], edges_right=edges[1:]))
        p = figure(title=title, tools="", background_fill_color="#fafafa")
        p.quad(top='hist', bottom=0, left='edges_left', right='edges_right', source=source,
            fill_color="blue", line_color="white", alpha=0.5)

        # Show the plot
        show(p)
