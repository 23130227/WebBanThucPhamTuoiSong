from .models import *


def categories(request):
    return {'categories': Category.objects.all().order_by('name')}
