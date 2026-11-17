from django.http import JsonResponse
from .models import Job

def jobs_list_api(request):
    jobs = Job.objects.live().order_by('-id')
    return JsonResponse([j.to_dict() for j in jobs], safe=False)
