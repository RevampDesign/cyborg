import json
from collections import defaultdict
from datetime import date

from django.views.generic import DetailView, TemplateView

from .models import SpanCategory, TimelineEntry, TimelineEra, TimelineSpan


def assign_lanes(spans):
    """Greedy interval packing — assigns .lane on each span in place."""
    lanes = []  # end date of last span in each lane
    for span in sorted(spans, key=lambda s: s.start_date):
        span_end = span.end_date or date.max
        for i, lane_end in enumerate(lanes):
            if span.start_date > lane_end:  # strict >, adjacent spans don't fuse
                span.lane = i
                lanes[i] = span_end
                break
        else:
            span.lane = len(lanes)
            lanes.append(span_end)
    return spans, len(lanes)


class TimelineView(TemplateView):
    template_name = "timeline/timeline.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        current_year = today.year

        # 1. Query approved entries and spans.
        entries = list(
            TimelineEntry.objects.filter(approved=True)
            .select_related("source", "term")
            .prefetch_related("source__author")
            .order_by("-date")
        )
        spans = list(
            TimelineSpan.objects.filter(approved=True)
            .select_related("category", "term")
        )

        # 2. Lane assignment (mutates span objects with .lane attribute).
        spans, lane_count = assign_lanes(spans)

        # 3. Active years = years with entries ∪ all years any span passes through.
        active_years = set()
        for entry in entries:
            active_years.add(entry.date.year)
        for span in spans:
            end_y = span.end_date.year if span.end_date else current_year
            for y in range(span.start_date.year, end_y + 1):
                active_years.add(y)

        # 4. Group entries by year.
        entries_by_year = defaultdict(list)
        for entry in entries:
            entries_by_year[entry.date.year].append(entry)

        # 5. Intensity per year: {year: {category_id: count}}.
        intensity_by_year = {year: {} for year in active_years}
        for span in spans:
            end_y = span.end_date.year if span.end_date else current_year
            for year in range(span.start_date.year, end_y + 1):
                if year in intensity_by_year:
                    counts = intensity_by_year[year]
                    counts[span.category_id] = counts.get(span.category_id, 0) + 1

        # 6. Build year_sections newest-first; flag non-adjacent year gaps.
        categories = list(SpanCategory.objects.all())  # ordered by weight
        eras = {
            era.year: era
            for era in TimelineEra.objects.filter(year__in=active_years)
        }

        sorted_years = sorted(active_years, reverse=True)
        year_sections = []
        for i, year in enumerate(sorted_years):
            prev_year = sorted_years[i - 1] if i > 0 else None
            gap_before = prev_year is not None and (prev_year - year) > 1
            year_sections.append({
                "year": year,
                "gap_before": gap_before,
                "era": eras.get(year),
                "entries": entries_by_year.get(year, []),
                "intensity": intensity_by_year.get(year, {}),
            })

        # 7. compass_payload: JSON dict keyed by year string for IntersectionObserver.
        compass_payload = {}
        for sec in year_sections:
            year = sec["year"]
            era = sec["era"]
            intensity_list = [
                {"category": cat.name, "color": cat.color, "count": sec["intensity"].get(cat.id, 0)}
                for cat in categories
                if sec["intensity"].get(cat.id, 0) > 0
            ]
            compass_payload[str(year)] = {
                "year": year,
                "framing": era.human_framing if era else "",
                "newsletter": (
                    {"title": era.newsletter_title, "url": era.newsletter_url}
                    if era and era.newsletter_url else None
                ),
                "intensity": intensity_list,
            }

        ctx.update({
            "year_sections": year_sections,
            "spans": spans,
            "lane_count": lane_count,
            "categories": categories,
            "current_year": current_year,
            "compass_payload": compass_payload,
        })
        return ctx


class TimelineEntryDetail(DetailView):
    model = TimelineEntry
    template_name = "timeline/entry_detail.html"
    context_object_name = "entry"

    def get_queryset(self):
        return (
            TimelineEntry.objects.filter(approved=True)
            .select_related("source", "source__publisher", "term")
            .prefetch_related("source__author", "related_entries")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        entry = self.object
        ctx["content"] = entry  # for base.html <title>
        ctx["json_ld"] = self._build_json_ld(entry)
        ctx["breadcrumb_parents"] = [{'title': 'Timeline', 'url': '/timeline/'}]

        return ctx

    def _build_json_ld(self, entry):
        ld = {"@context": "https://schema.org"}
        if entry.source:
            src = entry.source
            ld["@type"] = src.creative_work_type or "CreativeWork"
            ld["name"] = src.title
            if src.url:
                ld["url"] = src.url
            if src.date_published:
                ld["datePublished"] = src.date_published.isoformat()
            if src.description:
                ld["description"] = src.description
            authors = list(src.author.all())
            if authors:
                ld["author"] = [
                    {
                        "@type": "Organization" if a.is_organization else "Person",
                        "name": a.name,
                    }
                    for a in authors
                ]
            if src.publisher:
                ld["publisher"] = {
                    "@type": "Organization" if src.publisher.is_organization else "Person",
                    "name": src.publisher.name,
                }
        elif entry.term:
            term = entry.term
            ld["@type"] = "DefinedTerm"
            ld["name"] = term.title
            if term.description:
                ld["description"] = term.description
            ld["inDefinedTermSet"] = "https://cyborgnewsletter.com/glossary/"
        else:
            ld["@type"] = "Thing"
            ld["name"] = entry.title
            if entry.description:
                ld["description"] = entry.description
        return json.dumps(ld)
