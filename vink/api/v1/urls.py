from django.urls import include, path
from rest_framework import routers

from .views import ReceiveMessage, SendMessageGPT

router = routers.DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("gpt", SendMessageGPT.as_view(), name="send-message-gpt"),
    path("message", ReceiveMessage.as_view(), name="receive-message"),
]
