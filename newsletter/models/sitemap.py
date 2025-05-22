from django.contrib.sitemaps import Sitemap
from itertools import chain
from django.urls import reverse

from ..models import Newsletter #, NewsletterListPage

class NewsletterSitemap(Sitemap):
	changefreq = "weekly"
	priority = 0.9
	protocol = 'https'

	def items(self):
		# newsletter_list_page = NewsletterListPage.objects.all()
		newsletters = Newsletter.objects.filter(approved=True) 
		# newsletters = list(chain([reverse('newsletterList')], newsletters))
		return newsletters

	def lastmod(self, obj):
		if obj.date_updated:
			return obj.date_updated
		return obj.publish_date

	def heading(self):
		return 'Newsletters'

    