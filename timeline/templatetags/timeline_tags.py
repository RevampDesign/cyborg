import marko
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdown(value):
    if not value:
        return ""
    return mark_safe(marko.convert(value))


@register.filter
def dict_get(d, key):
    """Look up a dict value by key in templates: {{ intensity|dict_get:cat.id }}"""
    return d.get(key, 0)


_KIND_LABELS = {
    "film": "Film / TV",
    "book": "Book / Publication",
    "tech": "Technology",
    "event": "Historical Event",
    "idea": "Idea / Concept",
    "personal": "Personal / Newsletter",
}


@register.filter
def kind_label(value):
    return _KIND_LABELS.get(value, value.title())


@register.simple_tag
def timeline_entries_for_term(term):
    """Return approved TimelineEntries linked to a glossary Term, for reverse-discovery."""
    from ..models import TimelineEntry
    return TimelineEntry.objects.filter(approved=True, term=term).select_related("source").order_by("-date")


@register.simple_tag
def timeline_spans_for_term(term):
    """Return approved TimelineSpans linked to a glossary Term, for reverse-discovery."""
    from ..models import TimelineSpan
    return TimelineSpan.objects.filter(approved=True, term=term).select_related("category").order_by("-start_date")


@register.simple_tag
def grid_template(year_sections, lane_count):
    # Build interleaved [names]/size parts, merging adjacent name groups so no
    # two bracket sets are adjacent without a track size between them (invalid CSS).
    parts = []  # alternating: list-of-names | str size

    def push_names(names):
        if parts and isinstance(parts[-1], list):
            parts[-1].extend(names)
        else:
            parts.append(list(names))

    for sec in year_sections:
        if sec["gap_before"]:
            push_names([f"gap-{sec['year']}"])
            parts.append("min-content")
        push_names([f"y{sec['year']}-start"])
        parts.append("auto")
        push_names([f"y{sec['year']}-end"])

    row_str = " ".join(
        f"[{' '.join(p)}]" if isinstance(p, list) else p
        for p in parts
    )
    cols = f"repeat({lane_count}, var(--lane-width, 14px)) 1fr"
    return mark_safe(f"grid-template-rows: {row_str}; grid-template-columns: {cols};")
