from magic_image import enhance, transform

# Load and enhance
image = enhance.load_image('path_to_image.png')
enhanced = enhance.adjust_contrast(image, factor=1.5)
enhance.save_image(enhanced, '~/Downloads/image.png')

# Resize if needed
resized = transform.resize_image(image, (1920, 1080))
transform.save_image(resized, 'resized_image.png')
