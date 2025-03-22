from django.http import HttpResponse
from django.urls.exceptions import NoReverseMatch
import csv, json, io
from django.core.management import call_command


class ExportModelCSVMixin:
    def export_content_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}-content.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:

            obj_content = [getattr(obj, field) for field in field_names]

            row = writer.writerow(obj_content)

        return response

    def export_urls_as_csv(self, request, queryset):
        meta = self.model._meta
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}-urls.csv'.format(meta)
        writer = csv.writer(response)

        for obj in queryset:
            try:
                row = writer.writerow([obj.get_absolute_url()])
            except NoReverseMatch:
                row = writer.writerow(["ERROR: No slug found on page ID: " + str(obj.id)])

        return response

    

    def export_content_as_json(self, request, queryset):
        meta = self.model._meta

        with io.StringIO() as json_data:
            call_command('dumpdata', meta.app_label + "." + meta.model_name, stdout=json_data)

            # Change string into actual JSON and use it in the downloaded file
            download_info = json.loads(json_data.getvalue())
            response = HttpResponse(json.dumps(download_info), content_type='application/json')

        response['Content-Disposition'] = 'attachment; filename={}-response-content.json'.format(meta)

        return response
    


    # This does seem to download all models, not just selected pages, so in the admin, you might have only selected one page and this does all of them...
    def export_all_related_content_as_json(self, request, queryset):
        meta = self.model._meta

        inlines = []
        for obj in queryset:
            inlines = [x for x in self.get_inlines(request, obj) if x not in inlines]

        with io.StringIO() as json_data:
            call_command('dumpdata', meta.app_label + "." + meta.model_name, stdout=json_data)

            # Change string into actual JSON and use it in the downloaded file
            download_info = json.loads(json_data.getvalue())

        inline_download_data = None
        if inlines:
            for inline in inlines:
                inline_meta = inline.model._meta

                with io.StringIO() as inlines_json_data:
                    call_command('dumpdata', inline_meta.app_label + "." + inline_meta.model_name, stdout=inlines_json_data)

                    # Change string into actual JSON and use it in the downloaded file
                    inline_download_data = json.loads(inlines_json_data.getvalue())
                    download_info += inline_download_data

        
        response = HttpResponse(json.dumps(download_info), content_type='application/json')

        response['Content-Disposition'] = 'attachment; filename={}-response-content.json'.format(meta)

        return response


    export_content_as_csv.short_description = "Export selected content"
    export_urls_as_csv.short_description = "Export selected URLs"
    export_all_related_content_as_json.short_description = "Export all as JSON"