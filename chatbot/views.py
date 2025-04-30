from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def rasa_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        # Rasa API URL (Make sure Rasa is running)
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"

        payload = {"sender": "user", "message": user_message}
        headers = {"Content-Type": "application/json"}

        response = requests.post(rasa_url, json=payload, headers=headers)

        # Extract response text from Rasa
        rasa_response = response.json()
        bot_reply = rasa_response[0]["text"] if rasa_response else "Sorry, I didn't understand."

        return JsonResponse({"message": bot_reply})

    return JsonResponse({"error": "Invalid request"}, status=400)

def chatbot_page(request):
    return render(request, "chatbot.html")