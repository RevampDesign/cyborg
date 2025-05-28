from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

import pathlib
from ..models import Newsletter

class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs
        
    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])


class NewsletterFeed(Feed):
    title = "CYBORG_ Newsletters"
    description = "My latest articles"
    link = "/newsletters/feed/"

    feed_type = ExtendedRSSFeed

    def feed_copyright(self):
        return f"©{timezone.now().year} Not Defined LLC"

    def items(self):
        return Newsletter.objects.all().filter(approved=True).order_by('-publish_date')[:15]

    def item_title(self, item):
        return strip_tags(item.title)

    def item_description(self, item):
        excerptNoHTML = strip_tags(item.body)
        return excerptNoHTML[:300]

    def item_author_name(self, item):
        return item.author

    def item_pubdate(self, item):
        return item.publish_date

    def item_link(self, item):
        return reverse('newsletterDetail', args=[item.slug])

    def item_content_encoded(self, item):
        content = mark_safe(item.body)
        return "%s" % content

    def item_extra_kwargs(self, item):
        return {'content_encoded': self.item_content_encoded(item)}


    def item_enclosure_url(self, item):
        try:
            if item.featured_image:
                return item.featured_image.url
        except:
            return ''

    def item_enclosure_length(self, item):
        try:
            if item.featured_image:
                return item.featured_image.size
        except:
            return ''
    
    def item_enclosure_mime_type(self, item):
        try:
            if item.featured_image:
                img = item.featured_image
        except:
            return ''

        img_type = pathlib.Path(img.name).suffix.lower().replace('.', '')
        if img_type == 'jpg':
            img_type = 'jpeg'
        return f'image/{img_type}'


# class NewsletterTagFeed(Feed):
#     title = "CYBORG_ Newsletters"

#     feed_type = ExtendedRSSFeed

#     def feed_copyright(self):
#         return f"©{timezone.now().year} Not Defined LLC"

#     def get_object(self, request, slug):
#         # Access the slug from the URL
#         return slug

#     def items(self, obj):
#         slug = obj

#         if slug:
#             return Blog.objects.filter(publish_date__lte=timezone.now()).filter(approved=True).filter(tags__tag_type__slug=slug).order_by('-publish_date')[:15]
#         return None

#     def link(self, obj):
#         return f"/blog/feed/{obj}/"
    
#     def description(self, obj):
#         tag_type = BlogTagType.objects.filter(slug=obj).first()
#         if tag_type:
#             return f"{tag_type.title}: Our latest posts."
#         return f"Our latest posts."

#     def item_title(self, item):
#         return strip_tags(item.title)

#     def item_description(self, item):
#         excerptNoHTML = strip_tags(item.body)
#         return excerptNoHTML[:300]

#     def item_author_name(self, item):
#         return item.author

#     def item_pubdate(self, item):
#         return item.publish_date

#     def item_link(self, item):
#         return reverse('blogPost', args=[item.slug])

#     def item_content_encoded(self, item):
#         content = mark_safe(item.body)
#         return "%s" % content

#     def item_extra_kwargs(self, item):
#         return {'content_encoded': self.item_content_encoded(item)}


#     def item_enclosure_url(self, item):
#         if item.featured_image:
#             return item.featured_image.url
#         if item.image:
#             return item.image.url # Old images field
#         return ''

#     def item_enclosure_length(self, item):
#         try:
#             if item.featured_image:
#                 return item.featured_image.size
#             if item.image:
#                 return item.image.size
#         except:
#             return ''
    
#     def item_enclosure_mime_type(self, item):
#         if item.featured_image:
#             img = item.featured_image
#         elif item.image:
#             img = item.image
#         else:
#             return ''

#         img_type = pathlib.Path(img.name).suffix.lower().replace('.', '')
#         if img_type == 'jpg':
#             img_type = 'jpeg'
#         return f'image/{img_type}'