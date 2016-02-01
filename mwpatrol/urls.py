from django.conf.urls import patterns, include, url
from django.contrib import admin

from notifier import views as notifier_views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', notifier_views.IndexView.as_view()),
    url(r'^send/', notifier_views.IndexView.as_view()),
    url(r'^lists/', notifier_views.ListView.as_view()),
    url(r'^save-list/', notifier_views.ListView.as_view()),
    url(r'^export-list/', notifier_views.ListView.as_view()),
]
