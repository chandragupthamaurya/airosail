from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from newsletter.models import Newsletter

class StaticViewsSitemap(Sitemap):
	pass

class NewsletterSitemap(Sitemap):

	def items(self):
		return Newsletter.objects.all()
