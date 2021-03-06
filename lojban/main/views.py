
from httplib2 import Http

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson

from lojban.main.models import *

def home(request):
    news_items = NewsItem.objects.all()[:2]
    return render_to_response("home.html", {"news_items": news_items}, context_instance=RequestContext(request))

def news(request, year=None):
    years = NewsItem.objects.dates("pub_date", "year", order="DESC")
    years = list(years) # Workaround for Bug #6180
    if year is None:
        year = years[0].year
    year = int(year)
    news_items = NewsItem.objects.filter(pub_date__year=year)
    return render_to_response("news.html", {
        "news_items": news_items,
        "selected_year": year,
        "years": years,
    }, context_instance=RequestContext(request))

def faq(request):
    faqs = FAQ.objects.all()
    return render_to_response("faq.html", {"faqs": faqs}, context_instance=RequestContext(request))

def heard(request):
    heard_story = FirstTimeStory(text=request.POST['heard'], referrer=request.POST['referrer'])
    heard_story.save()
    return HttpResponseRedirect("/")

def community(request):

    # We only handle one weblog at the moment because we pass aggregation off onto LiveJournal.
    # Ideally, this should be changed so that we handle aggregation, in order to include non-LiveJournal weblogs.
    weblog = Weblog.objects.get()
    weblog_entries = WeblogEntry.objects.all()[:5]

    try:
        irc = IRCChannel.objects.get()
    except IRCChannel.DoesNotExist:
        irc = None

    return render_to_response("community.html", {
        "weblog": weblog,
        "weblog_entries": weblog_entries,
        "irc": irc,
    }, context_instance=RequestContext(request))

def irc(request):
    try:
        irc = IRCChannel.objects.get()
    except IRCChannel.DoesNotExist:
        irc = None

    return render_to_response("irc.html", {
        "irc": irc,
    }, context_instance=RequestContext(request))

def search(request):
    keywords = request.GET.get("keywords", "").split()
    matches = []
    for keyword in keywords:
        keyword = keyword.replace(".", " ").strip()
        for Valsi in Gismu, Cmavo, Lujvo, Fuhivla:
            try:
                valsi = Valsi.objects.get(name=keyword)
                valsi_type = type(valsi).__name__.lower()
                if valsi_type == "fuhivla":
                    valsi_type = "fu'ivla"
                autolink_regexp = re.compile(r'\{([a-zA-Z\']+)\}')
                valsi.notes = valsi.notes.replace("&", "&amp;").replace("<", "&lt;")
                valsi.notes = autolink_regexp.sub(r'<a href="/search/?keywords=\1">\1</a>', valsi.notes)
                matches.append((valsi, valsi_type))
            except Valsi.DoesNotExist:
                pass

    http = Http()
    headers = {
        "Referer": request.build_absolute_uri("/"),
    }
    response, content = http.request("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:lojban.com%20" + "%20".join(keywords))
    google_results = None
    if response.status == 200:
        google_results = simplejson.loads(content)["responseData"]["results"]

    return render_to_response("search.html", {
        "matches": matches,
        "google_results": google_results,
    }, context_instance=RequestContext(request))

def opensearch(request):
    return render_to_response("opensearch.xml", {
        "absolute_uri": request.build_absolute_uri("/"),
    }, context_instance=RequestContext(request), mimetype="application/opensearchdescription+xml ")

def opensearch_suggestions(request):
    keywords = request.GET.get("keywords", "")
    response = [
        keywords
    ]
    matches = []
    for Valsi in Gismu, Cmavo, Lujvo, Fuhivla:
        for match in Valsi.objects.filter(name__istartswith=keywords):
            matches.append(match.name)
    response.append(matches)
    return HttpResponse(simplejson.dumps(response), mimetype="application/x-suggestions+json")

