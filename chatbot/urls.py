from django.urls import path
from chatbot import views

urlpatterns = [
    path("chat/", views.rasa_chat, name="rasa_chat"),
    path("", views.chatbot_page, name="chat_page"),
]
