# views.py - SIMPLE VERSION (NO API NEEDED)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '').lower().strip()
            
            # Simple response logic
            if not user_input:
                reply = "Please type a message!"
            elif any(word in user_input for word in ['hello', 'hi', 'hey']):
                reply = "Hello! I'm your UniPay Assistant. How can I help you today?"
            elif any(word in user_input for word in ['remittance', 'transfer', 'send money']):
                reply = "I can help with money transfers! Our platform supports secure remittances to multiple countries."
            elif any(word in user_input for word in ['fee', 'cost', 'charge']):
                reply = "Transfer fees vary by destination and amount. Check our fees page for detailed pricing."
            elif any(word in user_input for word in ['saving', 'goal']):
                reply = "You can set up savings goals in your dashboard. Track your progress and achieve your targets!"
            elif any(word in user_input for word in ['donation', 'donate']):
                reply = "Our donation feature helps you contribute to meaningful causes. Every donation makes a difference!"
            elif any(word in user_input for word in ['thank', 'thanks']):
                reply = "You're welcome! Is there anything else I can help you with?"
            elif any(word in user_input for word in ['bye', 'goodbye']):
                reply = "Goodbye! Feel free to ask if you need more help with remittances!"
            else:
                reply = "I'm here to help with remittances, savings, and donations. Could you please rephrase your question?"
            
            return JsonResponse({'reply': reply})
            
        except Exception as e:
            return JsonResponse({'reply': 'Sorry, I encountered an error. Please try again.'})
    
    return JsonResponse({'reply': 'Only POST requests are supported.'})