from django.template.context_processors import csrf
from django.shortcuts import render_to_response, RequestContext



def render_reviews_page(request):
    args = {
        "title": "Reviews | ",
        "cat": "Reviews"
    }
    args.update(csrf(request))
    return render_to_response("close_reviews.html", args, context_instance=RequestContext(request))

def render_startups_page(request):
    args = {
        "title": "Startups | ",
        "cat": "Startups",
    }
    args.update(csrf(request))
    return render_to_response("close_startups.html", args, context_instance=RequestContext(request))