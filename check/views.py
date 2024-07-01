from django.template import loader
from django.http import HttpResponse
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def check(request):
    template = loader.get_template('check.html')
    return HttpResponse(template.render(request=request))

@csrf_exempt
def results(request):
    if request.method == 'POST':
        try:
            print(request.POST.get('language'))
            content = request.POST.get('content')
            language = request.POST.get('language')

            api_url = "http://127.0.0.1:8000/predict"
            data = {
                'content': content,
                'language': language
            }
            headers = {
                'Content-Type': 'application/json',
            }

            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return JsonResponse(result)
            else:
                return JsonResponse({'error': f"Error: {response.status_code}"}, status=response.status_code)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400) 

@csrf_exempt
@require_POST
def file_upload(request):
    file = request.FILES.get('file')
    language = request.POST.get('language')
    file_content = request.POST.get('fileContent')
    
    if file and file_content:
        # Process the file and content as needed
        print("Received File")

        return JsonResponse({'status': 'success', 'message': 'File uploaded successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to upload file'})