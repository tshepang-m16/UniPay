# The_App_Code/views/chatbot_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('user_input', '').strip()
        
        if not user_input:
            return JsonResponse({'reply': 'Please enter a message.'})
        
        # Simple response logic (no API needed)
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
            reply = "Hello! I'm your UniPay Assistant. How can I help you with money transfers, savings, or donations today?"
        elif any(word in user_input_lower for word in ['remittance', 'transfer', 'send money']):
            reply = "I can help with money transfers! Our platform supports secure remittances to multiple countries with competitive fees."
        elif any(word in user_input_lower for word in ['fee', 'cost', 'charge']):
            reply = "Transfer fees vary by destination and amount. You can check our fees page for detailed pricing information."
        elif any(word in user_input_lower for word in ['saving', 'goal']):
            reply = "You can set up savings goals in your dashboard to track your progress towards financial targets!"
        elif any(word in user_input_lower for word in ['donation', 'donate', 'pad']):
            reply = "Our donation feature helps you contribute to meaningful causes. Every donation makes a difference!"
        elif any(word in user_input_lower for word in ['thank', 'thanks']):
            reply = "You're welcome! Is there anything else I can help you with?"
        elif any(word in user_input_lower for word in ['bye', 'goodbye']):
            reply = "Goodbye! Feel free to ask if you need more help with remittances!"
        else:
            reply = "I'm here to help with remittances, savings goals, and donations. Could you please rephrase your question?"
        
        return JsonResponse({'reply': reply})
        
    except Exception as e:
        return JsonResponse({'reply': 'Sorry, I encountered an error. Please try again.'})