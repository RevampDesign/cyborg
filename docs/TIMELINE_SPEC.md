# Timeline App — Implementation Spec

Handoff document for implementing a new `timeline` Django app. All architecture decisions below have been made deliberately — implement as specified, flag (don't silently change) anything that conflicts with the existing codebase.

---

## 1. Purpose & Concept

A vertically scrolling timeline (inspired by ai-2027.com's format, not its content) for cyborgnewsletter.com. It is a **research and discovery tool** tracking humanity's interaction with technology over time — cultural artifacts (films, books), technology milestones, historical events, and fuzzy cultural currents — not just AI capability documentation.

Two audiences: the author (single contributor, connecting research already captured in the existing `glossary` app) and readers (orientation + discovery of connections between ideas).

### Core UX decisions (settled)
- **Scroll direction:** vertical, natural scrolling, **newest first** (reverse chronological).
- **Density:** compressed / natural density. The timeline is NOT proportional to time — year sections take whatever height their content needs. Empty years collapse into a `···` gap divider.
- **Point events:** entry cards with title + short description; expand via native `<details>` and/or link to a detail page.
- **Fuzzy ranges:** vertical span bars in lanes on the LEFT side, like a git history graph. Spans represent thematic/cultural currents (e.g., "Cyberpunk as dominant tech imagination"). Fuzzy start/end render as gradient fades, not hard caps.
- **Sticky "Era Compass":** a sticky panel that **snaps** (not continuous) when scrolling crosses a year boundary. Shows: year, an editorial one-line "human framing," per-category span intensity, and a link to the most relevant newsletter issue.
- **Eras = calendar years.** No custom named eras.
- **Span granularity = year.** Span bars snap to year boundaries on the grid (a span starting March 2025 visually starts at 2025's edge). Known, accepted simplification — fits the fuzzy/non-proportional design. Do not implement sub-year span positioning.
- **Rendering:** server-rendered Django templates. No JS framework. htmx is approved for later enhancement but v1 should NOT require it (see Deferred Items).

---

## 2. Existing Codebase Integration

The project already has:
- A `glossary` app with `Term`, `Source`, `SourceAuthor`, `SourcePublisher`, `TermSource` models. `Source` follows schema.org CreativeWork patterns (has `creative_work_type` choices, `date_published`, `chicago_authors()` citation rendering). `Term` mixes in `MetaSEO` (from `meta_seo.models`) and `Approval` (from `publishing.models`).
- Standard Django admin (no Wagtail active; Wagtail imports in glossary are commented out).
- `marko` for markdown.

### Integration principle: **Timeline references, glossary owns.**
Timeline models never duplicate glossary data. A timeline entry for *Neuromancer* stores only timeline placement + a short timeline-specific framing; author/citation/summary content is pulled through FK relations at render time.

### Explicit FKs, not GenericForeignKey.
This was considered and rejected. Use nullable FKs to `glossary.Source` and `glossary.Term`.

### Markdown caution (do not replicate existing bug)
`glossary.Term.save()` converts markdown→HTML **in place**, destroying the raw markdown and double-converting on re-save. Do NOT copy this pattern. For timeline text fields (`timeline_context`, span `description`), store raw markdown and render at template time via a template filter wrapping `marko.convert` (e.g., `{{ entry.timeline_context|markdown }}`). Fixing the glossary bug is out of scope here.

---

## 3. Models (`timeline/models.py`)

Reuse the project's `MetaSEO` and `Approval` mixins where indicated, matching glossary conventions. Inspect `publishing.models.Approval` for the actual published/approved filter and use it in views wherever `# Approval filter` is noted. Inspect `MetaSEO` for title/slug fields it may already provide — if `MetaSEO` provides `title`/`slug`, do not redeclare them on `TimelineEntry`.

```python
class SpanCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, help_text="Hex color, e.g. #6e44ff")
    weight = models.PositiveIntegerField(default=0, help_text="Ordering in compass/legend")

    class Meta:
        ordering = ["weight"]


class TimelineEra(models.Model):
    year = models.PositiveIntegerField(unique=True)
    human_framing = models.CharField(
        max_length=300, blank=True,
        help_text="One-line editorial frame for this year, in the author's voice.")
    newsletter_url = models.URLField(blank=True)
    newsletter_title = models.CharField(max_length=300, blank=True)
```

Entries have **no FK to Era** — `entry.date.year` is the join key. Era records exist only for years with editorial content; views fall back to a bare year label.

```python
class TimelineEntry(MetaSEO, Approval):
    date = models.DateField(help_text="Where this sits on the timeline. May differ from the Source's publication date.")

    class DatePrecision(models.TextChoices):
        EXACT = "exact", "Exact date"
        MONTH = "month", "Month"
        YEAR = "year", "Year"
    date_precision = models.CharField(max_length=10, choices=DatePrecision.choices, default=DatePrecision.EXACT)

    timeline_context = models.TextField(
        blank=True,
        help_text="Short framing for the timeline view (markdown). Detail content comes from linked Term/Source.")

    source = models.ForeignKey("glossary.Source", on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="timeline_entries")
    term = models.ForeignKey("glossary.Term", on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="timeline_entries")
    related_entries = models.ManyToManyField("self", blank=True)

    class Kind(models.TextChoices):
        FILM = "film", "Film / TV"
        BOOK = "book", "Book / Publication"
        TECH = "tech", "Technology"
        EVENT = "event", "Historical Event"
        IDEA = "idea", "Idea / Concept"
        PERSONAL = "personal", "Personal / Newsletter"
    kind = models.CharField(max_length=20, choices=Kind.choices, blank=True,
                            help_text="Leave blank to derive from linked Source's type.")

    SOURCE_TYPE_TO_KIND = {
        "Movie": Kind.FILM, "TVSeries": Kind.FILM,
        "Book": Kind.BOOK, "Article": Kind.BOOK,
        "ScholarlyArticle": Kind.BOOK, "NewsArticle": Kind.BOOK,
    }

    @property
    def display_kind(self):
        if self.kind:
            return self.kind
        if self.source_id:
            return self.SOURCE_TYPE_TO_KIND.get(self.source.creative_work_type, self.Kind.EVENT)
        if self.term_id:
            return self.Kind.IDEA
        return self.Kind.EVENT

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "timeline entries"
```

Date display rule: `date_precision` drives rendering — `exact` → "April 3, 2025"; `month` → "April 2025"; `year` → "2025". Implement as a model method or template filter.

```python
class TimelineSpan(Approval):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Blank = ongoing.")
    start_fuzzy = models.BooleanField(default=True)
    end_fuzzy = models.BooleanField(default=True)
    description = models.TextField(blank=True, help_text="Markdown.")
    term = models.ForeignKey("glossary.Term", on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="timeline_spans")
    category = models.ForeignKey(SpanCategory, on_delete=models.PROTECT, related_name="spans")
```

`lane` is **computed at view time, never stored**. Do not add a `lane_override` field (explicitly deferred).

---

## 4. Admin (`timeline/admin.py` + glossary additions)

### Prerequisite — glossary admins need `search_fields` for autocomplete to work
```python
# glossary/admin.py — add if missing
class SourceAdmin(...): search_fields = ["title", "alt_title"]; list_filter = ["creative_work_type"]
class TermAdmin(...):   search_fields = ["title"]
```

### TimelineEntry admin
- Custom `ModelForm` where `date` is not required in the form; `clean()` fills it from `source.date_published` when blank, else raises a field error ("Provide a date, or link a Source that has a publication date."). The entry's own date always wins when provided.
- `autocomplete_fields = ["source", "term", "related_entries"]`
- `list_display`: str, date, date_precision, derived-kind display (show "(derived)" when kind is blank), boolean has_source / has_term columns.
- `list_filter`: kind, date_precision, plus the Approval status field.
- `date_hierarchy = "date"`, `ordering = ["-date"]`, `prepopulated_fields = {"slug": ["title"]}` (if slug is editable here and not handled by MetaSEO).
- Fieldsets: Timeline placement (date, date_precision, kind) / Content (title, slug, timeline_context) / Glossary links (source, term) / Connections (related_entries, collapsed) / plus MetaSEO + Approval fieldsets matching glossary conventions.

### Research-workflow inlines (important feature)
Add timeline inlines to **glossary** admins so placing researched material on the timeline happens in situ:
```python
class TimelineEntryInline(admin.StackedInline):
    model = TimelineEntry; fk_name = "source"; extra = 0
    fields = ["title", "slug", "date", "date_precision", "kind", "timeline_context"]
class TimelineEntryFromTermInline(TimelineEntryInline): fk_name = "term"
class TimelineSpanInline(admin.TabularInline):
    model = TimelineSpan; extra = 0
    fields = ["title", "start_date", "end_date", "start_fuzzy", "end_fuzzy", "category"]
```
`SourceAdmin.inlines = [TimelineEntryInline]`; `TermAdmin.inlines = [TimelineEntryFromTermInline, TimelineSpanInline]`. Import direction: glossary admin imports from timeline (avoid circular imports).

### Other admins
- `SpanCategoryAdmin`: `list_editable = ["weight"]`; color field uses a native `<input type="color">` widget; changelist shows a rendered color swatch (`format_html`).
- `TimelineSpanAdmin`: list start/end/category/fuzzy flags; `autocomplete_fields = ["term"]`; `ordering = ["-start_date"]`.
- `TimelineEraAdmin`: `list_display = ["year", "human_framing", "newsletter_title"]`; `list_editable = ["human_framing"]` (one-liners are written/edited in bulk from the changelist); `ordering = ["-year"]`.

---

## 5. Views (`timeline/views.py`)

### Lane assignment (computed per request)
```python
def assign_lanes(spans):
    """Greedy interval packing, like a git graph."""
    from datetime import date
    lanes = []  # end date of last span in each lane
    for span in sorted(spans, key=lambda s: s.start_date):
        span_end = span.end_date or date.max
        for i, lane_end in enumerate(lanes):
            if span.start_date > lane_end:   # strict >, so adjacent spans don't fuse
                span.lane = i
                lanes[i] = span_end
                break
        else:
            span.lane = len(lanes)
            lanes.append(span_end)
    return spans, len(lanes)
```

### TimelineView (TemplateView)
Assembly steps (single pass, all in `get_context_data`):
1. Query published entries (`select_related("source", "term")`, `prefetch_related("source__author")`, ordered `-date`) and published spans (`select_related("category", "term")`). Use the Approval manager/filter.
2. `assign_lanes(spans)`.
3. **Active years** = years having entries ∪ years any span passes through (`start_date.year .. (end_date or today).year`). Years outside this set are not rendered.
4. Group entries by year (`defaultdict`).
5. **Intensity per year**: for each active year, count spans active in that year, keyed by `SpanCategory`. O(years × spans) is fine at this scale — do not optimize.
6. Build `year_sections` sorted newest-first. Each: `{year, gap_before (bool: previous rendered year is not adjacent), era (TimelineEra or None), entries, intensity}`. `gap_before` renders a `···` divider. Years with only a passing span still render as a thin labeled row (the grid line must exist).
7. Context: `year_sections`, `spans`, `lane_count`, `categories` (ordered by weight), `current_year`, and `compass_payload` — a JSON dict keyed by year: `{year, framing, newsletter: {title, url} | null, intensity: [{category, color, count}]}`. Emit with `json_script`.

### Detail views
- `TimelineEntryDetail(DetailView)` — template pulls citation via `entry.source.chicago_authors` (already returns schema.org-marked-up HTML; render with `|safe`), research summary via `entry.term.summary` (already HTML due to glossary's save behavior), and connections via `related_entries`.
- Detail pages should emit JSON-LD structured data derived from the linked Source/Term (the glossary is already schema.org-shaped; this is low-effort and desired).
- Reverse discovery: glossary Term/Source detail templates get an "On the timeline" section using the `related_name`s (`term.timeline_entries`, `term.timeline_spans`, `source.timeline_entries`). Link entries to their timeline position (anchor `#y<year>` on the main timeline) and/or detail page.

### URLs
```
/timeline/            TimelineView
/timeline/<slug>/     TimelineEntryDetail
```

---

## 6. Template & CSS Architecture

### The positioning mechanism (critical — do not substitute JS measurement)
Because density is non-proportional, span bars are positioned with **CSS Grid named row lines per year**, declared on the container. Span bars are grid items spanning multiple year rows. Reverse chronology means a span's **end year is its top edge** (`grid-row: y{end_year}-start / y{start_year}-end`); ongoing spans use `current_year` as the top. `<details>` expansion reflows the grid automatically — no resize listeners.

Template tag generates the container style:
```python
@register.simple_tag
def grid_template(year_sections, lane_count):
    rows = []
    for sec in year_sections:
        if sec["gap_before"]:
            rows.append(f"[gap-{sec['year']}] min-content")
        rows.append(f"[y{sec['year']}-start] auto [y{sec['year']}-end]")
    cols = f"repeat({lane_count}, var(--lane-width, 14px)) 1fr"
    return mark_safe(f"grid-template-rows: {' '.join(rows)}; grid-template-columns: {cols};")
```

Skeleton (`timeline.html`):
```django
<div class="timeline-grid" style="{% grid_template year_sections lane_count %}">
  {% for span in spans %}
    <div class="span-bar {% if span.start_fuzzy %}fuzzy-bottom{% endif %} {% if span.end_fuzzy %}fuzzy-top{% endif %}"
         style="grid-column: {{ span.lane|add:1 }};
                grid-row: y{{ span.end_date.year|default:current_year }}-start / y{{ span.start_date.year }}-end;
                --span-color: {{ span.category.color }};">
      <span class="span-label">{{ span.title }}</span>
    </div>
  {% endfor %}
  {% for sec in year_sections %}
    {% if sec.gap_before %}<div class="year-gap" style="grid-row: gap-{{ sec.year }};">···</div>{% endif %}
    <section class="year-section" style="grid-row: y{{ sec.year }};" data-year="{{ sec.year }}" id="y{{ sec.year }}">
      <h2 class="year-label">{{ sec.year }}</h2>
      {% for entry in sec.entries %}{% include "timeline/entry_card.html" %}{% endfor %}
    </section>
  {% endfor %}
</div>
<aside id="era-compass" class="era-compass">…</aside>
{{ compass_payload|json_script:"compass-data" }}
```

Year sections occupy the final (content) grid column — set `grid-column: {{ lane_count|add:1 }}` or `grid-column: -2 / -1` in CSS.

### Fuzzy edges — gradient mask, not dashed borders
```css
.span-bar { background: var(--span-color); border-radius: 99px; width: 6px; justify-self: center; }
.span-bar.fuzzy-top    { mask-image: linear-gradient(to bottom, transparent, black 3rem); }
.span-bar.fuzzy-bottom { mask-image: linear-gradient(to top, transparent, black 3rem); }
.span-bar.fuzzy-top.fuzzy-bottom {
  mask-image: linear-gradient(to bottom, transparent, black 3rem, black calc(100% - 3rem), transparent);
}
```
(Include `-webkit-mask-image` fallbacks.)

### entry_card.html
- Kind icon/marker driven by `entry.display_kind` (distinct visual per kind: film, book, tech, event, idea, personal).
- Date string formatted per `date_precision`.
- Title + `timeline_context` (markdown-rendered) always visible.
- `<details>` containing the linked Term summary / Source citation when present; plus a "full entry →" link to the detail page when the entry warrants one.

### Era Compass markup
Sticky panel showing: year, `human_framing`, intensity bars (one row per category present, colored by category color, bar length/segments = count), newsletter link (when present). Hide rows for categories with zero active spans rather than showing empty bars.

---

## 7. Era Compass JS (`timeline.js`)

Snap-on-boundary via `IntersectionObserver` with a thin tripwire band near the viewport top — NOT scroll-position math:
```js
const data = JSON.parse(document.getElementById("compass-data").textContent);
const compass = document.getElementById("era-compass");
const observer = new IntersectionObserver((items) => {
  for (const item of items) {
    if (item.isIntersecting) updateCompass(data[item.target.dataset.year]);
  }
}, { rootMargin: "-15% 0px -80% 0px" });
document.querySelectorAll(".year-section").forEach((el) => observer.observe(el));
```
`updateCompass(d)` swaps year/framing/intensity/newsletter content with a brief CSS transition (a `.switching` class toggled around the swap). Years without an Era record show the bare year and whatever intensity data exists. The compass must degrade gracefully with JS disabled (e.g., initially rendered server-side with the newest year's data).

---

## 8. Implementation Order

1. ✅ Models + migrations (inspect `Approval`/`MetaSEO` mixins first; don't duplicate fields they provide).
2. ✅ Markdown template filter (raw-in-DB, render-at-template-time). → `timeline/templatetags/timeline_tags.py`, `markdown` filter.
3. ✅ Admin: glossary `search_fields` → timeline admins → cross-app inlines. → `timeline/admin.py`; glossary inlines added to `glossary/admin.py`.
4. ✅ `assign_lanes` + `TimelineView` assembly. → `timeline/views.py`, `timeline/urls.py`; wired into `cyborg/urls.py` at `/timeline/`.
5. ✅ Templates + grid template tag + CSS. → `timeline/templates/timeline/timeline.html`, `entry_card.html`; `grid_template`/`dict_get`/`kind_label` tags in `timeline_tags.py`; `static/css/timeline.css`.
6. ✅ Era Compass JS. → `static/js/timeline.js`; loaded via `{% block extra_scripts %}` in `timeline.html`.
7. Detail views, JSON-LD, reverse-discovery sections on glossary templates.

## 9. Deferred / Out of Scope for v1

- htmx lazy-loading of expanded entry bodies (add only if page weight becomes a real problem).
- Sub-year span positioning (explicitly rejected for v1).
- `lane_override` manual lane control (add only if real layouts demand it).
- Visual connection lines between related entries (the M2M data is captured now; visualization later).
- Fixing the glossary markdown double-conversion bug.
- Filtering UI by entry kind (the `kind` field supports it; UI later).

## 10. Known Constraints & Conventions

- Single contributor; standard Django admin (no Wagtail).
- Site: cyborgnewsletter.com — match existing project styling conventions/static file organization.
- The timeline must launch useful with partial data: every feature degrades gracefully when a year lacks an Era, an entry lacks a Source/Term, or a category has no active spans.
