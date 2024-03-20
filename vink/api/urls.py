from django.urls import include, path

from api.v1 import urls as urls_v1

app_name = "api"

urlpatterns = [path("v1/", include(urls_v1))]
