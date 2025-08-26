from django.db import models
from meta_seo.models import MetaSEO
from publishing.models import Approval
from django.urls import reverse
from django.utils.html import format_html


class SourcePublisher(models.Model):
    name = models.CharField(max_length=300, help_text="Person or organization full name")

    is_organization = models.BooleanField(default=True, help_text="If publisher is an person, uncheck. This reflects in the publisher schema that it is a Person rather than the more typical Organization.")

    def __str__(self):
        return self.name


class SourceAuthor(models.Model):
    name = models.CharField(max_length=300, help_text="Person or organization full name")

    is_organization = models.BooleanField(default=False, help_text="If author is an organization, check. This reflects in the author schema that it is an organization rather than a Person.")

    def __str__(self):
        return self.name


class Source(models.Model):
    title = models.CharField(max_length=500, help_text="Use the full title / headline, including the subheadline. Exp: include the part after the ':'")
    alt_title = models.CharField(max_length=500, blank=True, help_text="This will be the shorter version of the title for secondary references in footnotes.")
    description = models.TextField(blank=True, help_text="Optional, probably for schema.")

    # Add foreignkey to a publisher model???
    # Add image??? if uploader then the Schema image prop will be the src...

    copyright_year = models.PositiveIntegerField(blank=True, null=True)

    url = models.URLField(blank=True)

    author = models.ManyToManyField(
        'glossary.SourceAuthor',
        blank=True,
    )
    publisher = models.ForeignKey(
        'glossary.SourcePublisher',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    date_published = models.DateField(blank=True, null=True, help_text="Date of first publication or broadcast.")
    date_modified = models.DateField(blank=True, null=True, help_text="The date on which the CreativeWork was most recently modified or when the item's entry was modified within a DataFeed.")

    class CreativeWorkType(models.TextChoices):
        BOOK = 'Book', "Book"
        ARTICLE = 'Article', "Article"
        SCHOLARLYARTICLE = 'ScholarlyArticle', "Scholarly Article"
        NEWSARTICLE = 'NewsArticle', "News Article"
        MOVIE = 'Movie', "Movie"
        TVSERIES = 'TVSeries', "TV Series"
        WEBSITE = 'WebSite', "Website"
        WEBPAGE = 'WebPage', "Webpage"
        SOCIAL = 'SocialMediaPosting', "Social Media Posting"
        PHOTOGRAPH = 'Photograph', "Photograph"
        PAINTING = 'Painting', "Painting"

    creative_work_type = models.CharField(max_length=50, choices=CreativeWorkType.choices)

    def __str__(self):
        if self.alt_title:
            return self.alt_title
        return self.title

    def chicago_authors(self):
        if not self.author.first:
            return ''
        
        author_person_schema_wrapper = '<span itemprop="author" itemscope itemtype="https://schema.org/Person">'
        author_org_schema_wrapper = '<span itemprop="author" itemscope itemtype="https://schema.org/Organization">'
        author_name_schema_wrapper = '<span itemprop="name">'

        authors = []
        for author in self.author.all():
            if author.is_organization:
                authors.append(author_org_schema_wrapper + author.name + '</span>')
            else:
                authors.append(author_person_schema_wrapper + author_name_schema_wrapper + author.name + '</span>' + '</span>')

        if self.author.count() > 6:
            """ Chicago styles says after 6 authors, only cite the first 3. In this case we remove the wrapper schema and output plain text and output the full author line-up as meta tags so that the Schema shows all authors while the text follows the style guide. """
            text_authors = ", ".join([author.name for author in self.author.all()[:3]]) + ' et al.,'

            meta_authors = []
            for author in self.author.all():
                if author.is_organization:
                    meta_authors.append(f'<span itemprop="author" itemscope itemtype="https://schema.org/Organization"><meta itemprop="name" content="{author.name}" /></span>')
                else:
                    meta_authors.append(f'<span itemprop="author" itemscope itemtype="https://schema.org/Person"><meta itemprop="name" content="{author.name}" /></span>')

            return text_authors + "".join(meta_authors)
        
        return ", ".join(authors) + ","