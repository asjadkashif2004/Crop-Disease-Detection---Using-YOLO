from django.urls import path
from .views import ChatbotView, PredictView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
]
