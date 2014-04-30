import uuid
from django.contrib import admin
from django.shortcuts import get_object_or_404
from multiupload.admin import MultiUploadAdmin
from indicator.models import Indicator, IndicatorData, IndicatorSource, IncomeLevel, LendingType, IndicatorTopic, CsvUploadLog
from django.conf.urls import patterns
from indicator.admin_tools import IndicatorAdminTools
from django.http import HttpResponse
from indicator.upload_indicators_helper import find_country, find_city, get_countries, get_cities, get_value, save_log, save_city_data, save_country_data
from indicator.wbi_parser import WBI_Parser


class IndicatorAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(IndicatorAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^update-indicator/$', self.admin_site.admin_view(self.update_indicators)),
            (r'^update-indicator-data/$', self.admin_site.admin_view(self.update_indicator_data)),
            (r'^update-indicator-city-data/$', self.admin_site.admin_view(self.update_indicator_city_data)),
            (r'^update-wbi-indicator/$', self.admin_site.admin_view(self.update_WBI_indicators))
        )
        return my_urls + urls

    def update_indicator_data(self, request):
        admTools = IndicatorAdminTools()
        admTools.update_indicator_data()
        return HttpResponse('Success')

    def update_indicator_city_data(self, request):
        admTools = IndicatorAdminTools()
        admTools.update_indicator_city_data()
        return HttpResponse('Success')

    def update_indicators(self, request):
        admTools = IndicatorAdminTools()
        admTools.update_indicators()
        return HttpResponse('Success')

    def update_WBI_indicators(self, request):
        wbi_parser = WBI_Parser()
        wbi_parser.import_wbi_indicators()
        return HttpResponse('Success')

    def update_WBI_indicator_data(self, request):
        wbi_parser = WBI_Parser()
        wbi_parser.import_wbi_indicator_data()
        return HttpResponse('Success')

class IndicatorDataAdmin(admin.ModelAdmin):
    list_display = ['indicator', 'city','country', 'region', 'year', 'value']
    search_fields = ['year', 'indicator__friendly_label', 'value']
    list_filter = ['indicator', 'city', 'country', 'year']

class IndicatorDataUploadAdmin(MultiUploadAdmin):
    list_display = ['indicator','selection_type', 'city','country', 'region', 'year', 'value']
    search_fields = ['year', 'indicator__friendly_label', 'value']
    list_filter = ['indicator','selection_type', 'city', 'country', 'year']
    # default value of all parameters:
    change_form_template = 'multiupload/change_form.html'
    change_list_template = 'multiupload/change_list.html'
    multiupload_template = 'multiupload/upload.html'
    # if true, enable multiupload on list screen
    # generaly used when the model is the uploaded element
    multiupload_list = True
    # if true enable multiupload on edit screen
    # generaly used when the model is a container for uploaded files
    # eg: gallery
    # can upload files direct inside a gallery.
    multiupload_form = True
    # max allowed filesize for uploads in bytes
    multiupload_maxfilesize = 3 * 2 ** 20 # 3 Mb
    # min allowed filesize for uploads in bytes
    multiupload_minfilesize = 0
    # tuple with mimetype accepted
    multiupload_acceptedformats = ( "text/csv",)

    def process_uploaded_file(self, uploaded, object,request, **kwargs):
        '''
        This method will be called for every csv file uploaded.
        Parameters:
            :uploaded: instance of uploaded file
            :object: instance of object if in form_multiupload else None
            :kwargs: request.POST received with file
        Return:
            It MUST return at least a dict with:
            {
                'url': 'url to download the file',
                'thumbnail_url': 'some url for an image_thumbnail or icon',
                'id': 'id of instance created in this method',
                'name': 'the name of created file',
            }
        '''

        #getting the title of the file
        title = kwargs.get('title', [''])[0] or uploaded.name

        import csv
        try:
            dialect = csv.Sniffer().sniff(uploaded.read(4048))
        except csv.Error:
            dialect = csv.excel

        file = csv.DictReader(uploaded, dialect=dialect)

        line_counter = 0
        indicator_from_db = None
        city_found = []
        city_not_found = []
        country_found = []
        country_not_found = []
        total_items_saved = 0

        cities = get_cities()
        countries = get_countries()
        for line in file:
            #getting data from the csv file
            city_csv = line.get('city')
            deprivation_type_csv = line.get('deprivation_type')
            description_csv = line.get('description')
            selection_type_csv = line.get('selection_type')
            country_csv = line.get('country')
            region_csv = line.get('region_csv')
            friendly_label_csv = line.get('friendly_name')
            value_csv = line.get('value')
            year_range_csv = line.get('year_range')
            indicator_id_csv = line.get('indicator_id')
            year_csv = line.get('year')
            type_data_csv = line.get('type_data')

            #here we are checking if this indicator already exists, or if we have to create a new one
            if line_counter == 0:
                #try to find the indicator that is uploaded or create a new one
                indicator_from_db = Indicator.objects.get_or_create(id=indicator_id_csv)[0]

                #update the indicator fields
                indicator_from_db.description = description_csv
                indicator_from_db.friendly_label = friendly_label_csv
                indicator_from_db.type_data = type_data_csv
                indicator_from_db.selection_type = selection_type_csv
                indicator_from_db.deprivation_type = deprivation_type_csv
                indicator_from_db.save()

            #getting city from our database
            city_from_db = find_city(city_name=city_csv, cities=cities)

            #getting country from our database
            country_from_db = find_country(country_name=country_csv, countries=countries)

            #add country to the log array
            if country_from_db:
                country_found.append(country_csv)
            else:
                if country_csv:
                    country_not_found.append(country_csv)

            #add city to the log array
            if city_from_db:
                city_found.append(city_csv)
            else:
                if city_csv:
                    city_not_found.append(city_csv)

            #this block is for storing data related to cities
            if save_city_data(
                city_from_db=city_from_db,
                country_from_db=country_from_db,
                selection_type_csv=selection_type_csv,
                indicator_from_db=indicator_from_db,
                year_csv=year_csv,
                value_csv=value_csv
            ): total_items_saved += 1

            #this block is for storing country related indicator data
            if save_country_data(
                    country_from_db=country_from_db,
                    city_csv=city_csv,
                    selection_type_csv=selection_type_csv,
                    year_csv=year_csv,
                    indicator_from_db=indicator_from_db,
                    value_csv=value_csv
            ): total_items_saved += 1

            line_counter += 1


        log = save_log(file=uploaded,
                 uploaded_by_user=request.user,
                 cities_not_found=city_not_found,
                 countries_not_found=country_not_found,
                 total_cities_found=city_found,
                 total_countries_found=country_found,
                 total_cities_not_found=city_not_found,
                 total_countries_not_found=country_not_found,
                 total_items_saved=total_items_saved
        )


        return {
            'url': '/admin/indicator/csvuploadlog/%s/' % str(log.id),
            'thumbnail_url': '',
            'id': str(log.id),
            'name' : title,
            'country_not_found' : log.countries_not_found,
            'total_countries_not_found' : country_not_found.__len__(),
            'city_not_found' : log.cities_not_found,
            'total_cities_not_found' : city_not_found.__len__(),
            'total_items_saved' : str(total_items_saved),

        }

    def delete_file(self, pk, request):
        '''
        Function to delete a file.
        '''
        # This is the default implementation.
        obj = get_object_or_404(self.queryset(request), pk=pk)
        obj.delete()



admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(IndicatorData, IndicatorDataUploadAdmin)
admin.site.register(IndicatorSource)
admin.site.register(IncomeLevel)
admin.site.register(LendingType)
admin.site.register(IndicatorTopic)
admin.site.register(CsvUploadLog)
