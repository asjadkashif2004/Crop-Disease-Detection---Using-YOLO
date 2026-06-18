"""
views.py
Django REST API view for crop disease prediction.
Endpoint: POST /api/predict/
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .groq_chat import GroqChatError, get_chat_response
from .model_loader import get_model
from .utils import validate_image, preprocess_image, format_prediction, get_recommendation


@method_decorator(csrf_exempt, name='dispatch')
class PredictView(APIView):
    """
    POST /api/predict/
    Accepts an image file and returns disease prediction.
    """
    parser_classes = [MultiPartParser]

    def post(self, request):

        # ── 1. Check image was provided ──────────────────────────
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'success': False, 'error': 'No image file provided. Send image as multipart/form-data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── 2. Validate the image ─────────────────────────────────
        is_valid, error_msg = validate_image(image_file)
        if not is_valid:
            return Response(
                {'success': False, 'error': error_msg},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )

        # ── 3. Load model ─────────────────────────────────────────
        try:
            model = get_model()
        except Exception as e:
            return Response(
                {'success': False, 'error': f'Model failed to load: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ── 4. Preprocess & run inference ─────────────────────────
        try:
            image   = preprocess_image(image_file)
            results = model.predict(source=image, conf=0.25, verbose=False)
        except Exception as e:
            return Response(
                {'success': False, 'error': f'Inference error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ── 5. Format & return result ─────────────────────────────
        try:
            prediction = format_prediction(results, model)
        except Exception as e:
            return Response(
                {'success': False, 'error': f'Result processing error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                'success'   : True,
                'prediction': prediction['display_name'],
                'class_raw' : prediction['class_name'],
                'confidence': prediction['confidence'],
                'detected'  : prediction['detected'],
                'recommendation': get_recommendation(prediction['class_name']),
            },
            status=status.HTTP_200_OK
        )


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(APIView):
    """
    POST /api/chatbot/
    Sends a crop-health question to Groq and returns the assistant reply.
    """
    parser_classes = [JSONParser]

    def post(self, request):
        message = request.data.get('message', '')

        if not isinstance(message, str) or not message.strip():
            return Response(
                {'success': False, 'error': 'Message is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(message) > 2200:
            return Response(
                {'success': False, 'error': 'Message is too long. Please keep it under 2200 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reply = get_chat_response(
                message=message,
                history=request.data.get('history', []),
                context=request.data.get('context', {}),
            )
        except GroqChatError as exc:
            return Response(
                {'success': False, 'error': exc.user_message},
                status=exc.status_code
            )
        except Exception:
            return Response(
                {'success': False, 'error': 'Chatbot failed to generate a response.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {'success': True, 'reply': reply},
            status=status.HTTP_200_OK
        )
