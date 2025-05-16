from django import template
from newsletter.models import Newsletter

register = template.Library()

@register.simple_tag
def newsletter_average_read_time():
    all_newsletters = Newsletter.objects.all()

    time_sum = 0
    count = len(all_newsletters)

    for newsletter in all_newsletters:
        time_sum += round(len(newsletter.body.split(" ")) / 200)

    average_read_time = round(time_sum / count, 1)

    return average_read_time