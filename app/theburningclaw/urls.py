from django.urls import path

from theburningclaw.views import Do

urlpatterns = [
    path('do/', Do.as_view()),
]
