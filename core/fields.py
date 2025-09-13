from django.db import models
import os, io
from PIL import Image
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
import datetime


class OptimizedImageField(models.FileField):
    """
    A custom Django field that automatically creates and saves a WebP
    version of an uploaded image file. The processing logic is placed in
    `pre_save` to ensure it runs whenever the model instance is saved.
    """
    def __init__(self, webp_field_name='_webp', webp_quality=88, *args, **kwargs):
        """
        Initializes the field with configurable options.

        Args:
            webp_field_name (str): The suffix for the WebP field name.
                                   Example: 'image' -> 'image_webp'.
            webp_quality (int): The quality setting for WebP conversion (0-100).
        """
        self.webp_field_name_suffix = webp_field_name
        self.webp_quality = webp_quality
        # Define a configurable maximum file size, defaulting to 5 MB
        self.max_size = getattr(settings, 'OPTIMIZED_IMAGE_MAX_FILE_SIZE_MB', 5) * 1024 * 1024
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        """
        Returns the field type for migrations.
        """
        return "FileField"
    
    def pre_save(self, model_instance, add):
        """
        This is the correct place for file processing. It is called by the
        model's save() method before writing to the database.
        """
        # Get the previous state of the file and the webp file from the database
        # to handle deletion of old files on update.
        old_file = None
        old_webp_file = None
        if not add and model_instance.pk:
            try:
                old_instance = self.model.objects.get(pk=model_instance.pk)
                old_file = getattr(old_instance, self.attname)
                old_webp_file = getattr(old_instance, self.name + self.webp_field_name_suffix)
            except self.model.DoesNotExist:
                pass
        
        webp_field_name = self.name + self.webp_field_name_suffix

        # Let the parent class handle the initial file saving. This returns the
        # FieldFile instance with the final path.
        new_file = super().pre_save(model_instance, add)

        # If the file field is being cleared, handle deletion.
        if not new_file:
            # Delete old original file using the FieldFile's delete method.
            if old_file and old_file.name:
                old_file.delete(save=False)
            
            # Delete old WebP file if it exists
            if old_webp_file and old_webp_file.name and default_storage.exists(old_webp_file.name):
                default_storage.delete(old_webp_file.name)
                
            setattr(model_instance, webp_field_name, '')
            return new_file

        # Handle updating an existing instance
        if old_file and old_file.name and old_file.name != new_file.name:
            # Delete old original file if it's different from the new one
            old_file.delete(save=False)
            
        # Check for file size before processing to prevent DoS attacks
        if new_file.size > self.max_size:
            # Delete the newly uploaded file before raising an error
            new_file.delete(save=False)
            raise ValidationError(f"The uploaded file is too large. The maximum size allowed is {self.max_size / (1024 * 1024):.0f} MB.")
            
        # Handle SVG and GIF files which should not be converted to WebP
        extension = os.path.splitext(new_file.name)[1].lower()
        if extension in [".svg", ".gif"]:
            # If a WebP file exists for a previous upload, delete it.
            if old_webp_file and old_webp_file.name and default_storage.exists(old_webp_file.name):
                default_storage.delete(old_webp_file.name)
            setattr(model_instance, webp_field_name, '')
            return new_file

        try:
            # Delete old WebP file before creating the new one to prevent orphaned files
            if old_webp_file and old_webp_file.name and default_storage.exists(old_webp_file.name):
                default_storage.delete(old_webp_file.name)
            
            # Rewind the original file object to ensure it can be read from the beginning
            new_file.seek(0)
            # Read the entire file content into an in-memory buffer
            image_buffer = io.BytesIO(new_file.read())
            image = Image.open(image_buffer)

            # Create a new buffer for the WebP output
            webp_buffer = io.BytesIO()

            # Convert and save the image to the WebP buffer
            if image.mode in ("P", "RGBA") or extension == ".png":
                webp_image = image.convert("RGBA")
                webp_image.save(webp_buffer, 'WEBP', preserve_palette=True, lossless=True)
            else:
                webp_image = image.convert("RGB")
                webp_image.save(webp_buffer, 'WEBP', quality=self.webp_quality)
            
            webp_buffer.seek(0)
            
            # Construct the new WebP path by replacing the original extension with '.webp'
            original_file_path = new_file.name
            webp_path = os.path.splitext(original_file_path)[0] + '.webp'

            # Save the new WebP file using Django's default storage backend
            webp_file_to_save = InMemoryUploadedFile(webp_buffer, None, webp_path, 'image/webp', webp_buffer.getbuffer().nbytes, None)
            
            # Save the new file to storage
            default_storage.save(webp_path, webp_file_to_save)

            # Update the related WebP field in the model instance
            setattr(model_instance, webp_field_name, webp_path)

            image.close()

        except Exception as e:
            # Catch any errors during image processing
            raise ValidationError(f"Unable to process the image file. Please ensure it is a valid image format. Error: {e}")
        
        return new_file
