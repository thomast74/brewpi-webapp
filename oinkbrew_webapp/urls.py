from django.conf.urls import patterns, include, url
from django.contrib import admin


handler400 = 'api.views.errors.bad_request'
handler403 = 'api.views.errors.permission_denied'
handler404 = 'api.views.errors.page_not_found'
handler500 = 'api.views.errors.server_error'

urlpatterns = patterns('',
                       url(r'^api/', include('api.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )
