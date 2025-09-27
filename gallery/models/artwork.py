from django.db import models
from core.fields import OptimizedImageField
import datetime
from django.utils.html import format_html

class Artwork(models.Model):
    """ Most fields pulled from schema: 
    https://schema.org/VisualArtwork """

    name = models.CharField(max_length=300, help_text="Title of the work as it will be displayed on site and in schema")

    about = models.TextField(blank=True, help_text="The subject matter of the content.")

    image = OptimizedImageField(
        upload_to='images/gallery/',
        blank=True,
    )
    image_webp = models.ImageField(
        upload_to='images/gallery/',
        null=True,
        blank=True
    )

    date_artwork_created = models.DateTimeField(blank=True, null=True)

    art_medium = models.CharField(max_length=255, blank=True, default="Charcoal", help_text="The material used (e.g. Oil, Watercolour, Acrylic, Woodcut, etc.")

    art_edition = models.CharField(max_length=255, blank=True, help_text="The number of copies when multiple copies of a piece of artwork are produced - e.g. for a limited edition of 20 prints, 'artEdition' refers to the total number of copies (in this example \"20\").")

    artform = models.CharField(max_length=255, blank=True, default="Drawing", help_text="Painting, Drawing, Sculpture, Print, Photograph, Assemblage, Collage, etc.")

    artwork_surface = models.CharField(max_length=255, blank=True, default="Paper", help_text="The supporting materials for the artwork, e.g. Canvas, Paper, Wood, Board, etc.")

    # Use these for Unit types:
    # https://schema.org/Distance
    # https://schema.org/Mass
    class Unit(models.TextChoices):
        INCHES = 'in', "Inches"
        FEET = 'ft', "Feet"

    height = models.PositiveIntegerField(blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    dimension_unit = models.CharField(max_length=50, blank=True, choices=Unit.choices)

    artist = models.ForeignKey(
        "author.Author",
        related_name="artworks",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=1
    )

    def __str__(self):
        return self.name

    def copyright_notice(self):
        if self.date_artwork_created:
            year = self.date_artwork_created.year
        else:
            year = datetime.date.today().year
            
        return f"© {year} {self.artist.name}"

    def image_preview(self):
        if self.image_webp:
            return format_html('<img src="{src}" style="width:30px; margin:0;">', src=self.image_webp.url)
        if self.image:
            return format_html('<img src="{src}" style="width:30px; margin:0;">', src=self.image.url)
        return ''
    image_preview.short_description = "Preview"