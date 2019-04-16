from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


@login_required
def member_index(request):
    t = loader.get_template('member/member-index.html')
    c = {}
    return HttpResponse(t.render(c, request), content_type='text/html')
