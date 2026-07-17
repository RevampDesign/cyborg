from django_distill import distill_path

from .models import TimelineEntry
from .views import TimelineEntryDetail, TimelineView


def get_all_timeline_entries():
    for entry in TimelineEntry.objects.filter(approved=True):
        yield {"slug": entry.slug}


urlpatterns = [
    distill_path("", TimelineView.as_view(), name="timeline"),
    distill_path(
        "<slug:slug>/",
        TimelineEntryDetail.as_view(),
        name="timeline_entry_detail",
        distill_func=get_all_timeline_entries,
    ),
]
