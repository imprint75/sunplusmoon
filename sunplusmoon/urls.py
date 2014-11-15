from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from sunplusmoon.views import HomeView

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
    # url(r'^sunplusmoon/', include('sunplusmoon.foo.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
