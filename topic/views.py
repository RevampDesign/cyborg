from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from newsletter.models import Newsletter
from .models import Topic

class TopicList(ListView):
    model = Topic # Use object_list in template
    paginate_by = 10
    template_name = 'topic/list.html'
    ordering = ['order']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = {'title': 'Topics', 'headline': 'All things CYBORG_.', 'description': 'Search the collection for topics like design, artificial intelligence, and humanity.'}
        return context



def topicDetail(request, slug):
    content = get_object_or_404(Topic, slug=slug)
    object_list = Newsletter.objects.filter(tags__name=content.title).order_by('-publish_date')

    template_name = 'topic/detail.html'

    context = {'content': content, 'object_list': object_list}

    return render(request, template_name, context)