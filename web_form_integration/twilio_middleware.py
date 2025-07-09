# from werkzeug.wrappers import Response

# class TwilioResponseValidator:
#     def __init__(self, app):
#         self.app = app

#     def __call__(self, environ, start_response):
#         def custom_start_response(status, headers, exc_info=None):
#             # Filter and replace headers
#             filtered_headers = [
#                 (k, v) for k, v in headers 
#                 if k.lower() in ('content-type', 'content-length')
#             ]
#             return start_response(status, filtered_headers, exc_info)

#         response = self.app(environ, custom_start_response)
        
#         # For Twilio endpoints, verify size
#         if environ.get('PATH_INFO', '').startswith('/twilio/'):
#             content = b''.join(response)
#             if len(content) > 65536:  # 64KB
#                 return Response(
#                     '<?xml version="1.0" encoding="UTF-8"?><Response><Reject/></Response>',
#                     content_type='text/xml',
#                     status=413
#                 )(environ, start_response)
        
#         return response