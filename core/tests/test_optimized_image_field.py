from django.db import models
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.conf import settings
import os
import io
from PIL import Image

from core.fields import OptimizedImageField
from gallery.models import Artwork

# Create a temporary directory for tests
TEST_DIR = os.path.join(settings.MEDIA_ROOT, 'test_images')

class OptimizedImageFieldTestCase(TestCase):
    """
    Unit tests for the custom OptimizedImageField.
    """
    def setUp(self):
        # Ensure the test media directory exists
        if not os.path.exists(TEST_DIR):
            os.makedirs(TEST_DIR)

        self.artwork = Artwork.objects.create(name="Test Art", artist=None)

    def tearDown(self):
        # Clean up files created during tests
        for root, dirs, files in os.walk(TEST_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def create_dummy_image(self, file_format='JPEG'):
        """Helper to create an in-memory image file."""
        image = Image.new('RGB', (100, 100), 'red')
        buffer = io.BytesIO()
        image.save(buffer, file_format)
        buffer.seek(0)
        return buffer

    def test_image_upload_and_webp_creation(self):
        """Test that uploading a JPEG creates both a JPEG and a WebP file."""
        dummy_image = self.create_dummy_image()
        uploaded_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=dummy_image.read(),
            content_type='image/jpeg'
        )

        self.artwork.image = uploaded_file
        self.artwork.save()

        # Check that the original file was saved
        original_file_path = self.artwork.image.name
        self.assertTrue(default_storage.exists(original_file_path))
        self.assertTrue(original_file_path.startswith('images/'))
        self.assertTrue(original_file_path.endswith('.jpg'))

        # Check that the webp file was created and the field was populated
        webp_file_path = self.artwork.image_webp.name
        self.assertTrue(default_storage.exists(webp_file_path))
        self.assertTrue(webp_file_path.startswith('images/'))
        self.assertTrue(webp_file_path.endswith('.webp'))
        
        # Verify the content type of the WebP file
        webp_file = default_storage.open(webp_file_path)
        webp_image = Image.open(webp_file)
        self.assertEqual(webp_image.format, 'WEBP')
        webp_file.close()

    def test_png_to_webp_conversion_preserves_transparency(self):
        """Test that uploading a PNG creates a lossless WebP file."""
        image = Image.new('RGBA', (100, 100), (255, 0, 0, 128)) # Semi-transparent red
        buffer = io.BytesIO()
        image.save(buffer, 'PNG')
        buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            name='test_transparency.png',
            content=buffer.read(),
            content_type='image/png'
        )

        self.artwork.image = uploaded_file
        self.artwork.save()

        webp_file_path = self.artwork.image_webp.name
        self.assertTrue(default_storage.exists(webp_file_path))

        webp_file = default_storage.open(webp_file_path)
        webp_image = Image.open(webp_file)
        self.assertEqual(webp_image.format, 'WEBP')
        # Check that the image mode is RGBA, indicating transparency was preserved
        self.assertEqual(webp_image.mode, 'RGBA')
        webp_file.close()

    def test_unsupported_format_no_webp(self):
        """Test that unsupported formats like SVG or GIF are not converted."""
        # Create a dummy SVG file
        svg_content = '<svg xmlns="http://www.w3.org/2000/svg" />'
        uploaded_file = SimpleUploadedFile(
            name='test_image.svg',
            content=svg_content.encode(),
            content_type='image/svg+xml'
        )

        self.artwork.image = uploaded_file
        self.artwork.save()

        # Check that only the original file was saved
        original_file_path = self.artwork.image.name
        self.assertTrue(default_storage.exists(original_file_path))
        self.assertTrue(original_file_path.endswith('.svg'))

        # The WebP field should be empty
        self.assertEqual(self.artwork.image_webp.name, '')

    def test_clearing_image_deletes_both(self):
        """Test that clearing the image field deletes both files from storage."""
        # First, create and save an instance with an image
        dummy_image = self.create_dummy_image()
        uploaded_file = SimpleUploadedFile(
            name='test_to_be_deleted.jpg',
            content=dummy_image.read(),
            content_type='image/jpeg'
        )
        self.artwork.image = uploaded_file
        self.artwork.save()
        self.artwork.refresh_from_db()

        original_file_path = self.artwork.image.name
        webp_file_path = self.artwork.image_webp.name

        self.assertTrue(default_storage.exists(original_file_path))
        self.assertTrue(default_storage.exists(webp_file_path))

        # Now, clear the field and save the instance
        self.artwork.image = None
        self.artwork.save()
        self.artwork.refresh_from_db()

        # Check that both files no longer exist in storage
        self.assertFalse(default_storage.exists(original_file_path))
        self.assertFalse(default_storage.exists(webp_file_path))
        self.assertEqual(self.artwork.image.name, '')
        self.assertEqual(self.artwork.image_webp.name, '')

    def test_file_size_validation(self):
        """Test that uploading a file larger than the max size raises a ValidationError."""
        # Create a dummy image larger than the default 5MB limit
        # A 10MB file is a good size for this test.
        large_image_content = b'A' * (10 * 1024 * 1024)
        large_uploaded_file = SimpleUploadedFile(
            name='test_large_file.jpg',
            content=large_image_content,
            content_type='image/jpeg'
        )

        instance = Artwork(artist=None)
        
        with self.assertRaises(ValidationError):
            instance.image = large_uploaded_file
            instance.save()

    def test_update_image_replaces_both_files(self):
        """Test that updating an image field correctly deletes and replaces
        both the original and the WebP file."""
        # First, save an initial image
        initial_image = SimpleUploadedFile(
            name='test_initial_image.jpg',
            content=self.create_dummy_image().read(),
            content_type='image/jpeg'
        )
        self.artwork.image = initial_image
        self.artwork.save()
        initial_original_path = self.artwork.image.name
        initial_webp_path = self.artwork.image_webp.name

        # Check that initial files exist
        self.assertTrue(default_storage.exists(initial_original_path))
        self.assertTrue(default_storage.exists(initial_webp_path))

        # Now, save a new image to the same instance
        new_image = SimpleUploadedFile(
            name='test_new_image.jpg',
            content=self.create_dummy_image().read(),
            content_type='image/jpeg'
        )
        self.artwork.image = new_image
        self.artwork.save()

        # Get the new file paths
        new_original_path = self.artwork.image.name
        new_webp_path = self.artwork.image_webp.name
        
        # Assert that the old files are deleted
        self.assertFalse(default_storage.exists(initial_original_path))
        self.assertFalse(default_storage.exists(initial_webp_path))

        # Assert that the new files were created
        self.assertTrue(default_storage.exists(new_original_path))
        self.assertTrue(default_storage.exists(new_webp_path))

        # Assert that the paths were updated on the model instance
        self.assertNotEqual(initial_original_path, new_original_path)
        self.assertNotEqual(initial_webp_path, new_webp_path)

    def test_upload_svg_over_image_deletes_webp(self):
        """Test that uploading a non-image file over an existing image
        deletes the old WebP file."""
        # First, save an image to create a WebP file
        image_file = SimpleUploadedFile(
            name='test_image.png',
            content=self.create_dummy_image(file_format='PNG').read(),
            content_type='image/png'
        )
        self.artwork.image = image_file
        self.artwork.save()
        
        initial_webp_path = self.artwork.image_webp.name
        self.assertTrue(default_storage.exists(initial_webp_path))

        # Now, upload an SVG to the same instance
        svg_content = b'<svg xmlns="http://www.w3.org/2000/svg" />'
        svg_file = SimpleUploadedFile(
            name='test_image.svg',
            content=svg_content,
            content_type='image/svg+xml'
        )
        self.artwork.image = svg_file
        self.artwork.save()

        # The old WebP file should be deleted and the field cleared
        self.assertFalse(default_storage.exists(initial_webp_path))
        self.assertEqual(self.artwork.image_webp.name, '')
        
        # The new SVG file should exist
        self.assertTrue(default_storage.exists(self.artwork.image.name))

    def test_invalid_image_raises_validation_error(self):
        """Test that an invalid or corrupted file raises a ValidationError."""
        corrupted_file = SimpleUploadedFile(
            name='test_corrupted.jpg',
            content=b'This is not an image.',
            content_type='image/jpeg'
        )
        
        with self.assertRaises(ValidationError):
            self.artwork.image = corrupted_file
            self.artwork.save()