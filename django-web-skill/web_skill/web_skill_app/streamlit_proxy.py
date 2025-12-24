
# import httpx
# from django.conf import settings
# from django.http import StreamingHttpResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def streamlit_proxy(request, path=""):
#     """
#     Vista proxy que reenvía las solicitudes a un servidor de Streamlit local.
#     """
#     streamlit_url = settings.STREAMLIT_SERVER_URL
#     full_path = request.get_full_path()

#     # Construir la URL completa del backend de Streamlit
#     backend_url = f"{streamlit_url}{full_path}"

#     try:
#         # Realizar la solicitud al servidor de Streamlit
#         with httpx.stream(
#             request.method,
#             backend_url,
#             headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
#             content=request.body,
#             timeout=60.0,
#         ) as response:
#             # Transmitir la respuesta de vuelta al cliente
#             return StreamingHttpResponse(
#                 response.iter_bytes(),
#                 content_type=response.headers.get('Content-Type'),
#                 status=response.status_code,
#                 reason=response.reason_phrase,
#             )
#     except httpx.RequestError as e:
#         # Manejar errores de conexión con el servidor de Streamlit
#         error_message = f"Error al conectar con el servidor de Streamlit: {e}"
#         return HttpResponse(error_message, status=502)
