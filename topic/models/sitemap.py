from django.contrib.sitemaps import Sitemap
from itertools import chain
from django.urls import reverse

from ..models import Topic

class TopicSitemap(Sitemap):
	changefreq = "monthly"
	priority = 0.7
	protocol = 'https'

	def items(self):
		topics = Topic.objects.all()
		return topics

	def lastmod(self, obj):
		if obj.date_updated:
			return obj.date_updated
		return obj.publish_date

	def heading(self):
		return 'Topics'

    