from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from . import util


class searchForm(forms.Form):
    search = forms.CharField(label="Search encyclopedia")


def index(request):
    if "subsearch" not in request.session:

        # if not, create a new list
        request.session["subsearch"] = []

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search": searchForm()
    })


def entry(request, name):

    if not util.get_entry(name):
        return render(request, "encyclopedia/error.html")
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": name.upper(),
            "entry": util.get_entry(name),
        })


def search(request):

    request.session["subsearch"] = []

    if request.method == "POST":

        form = searchForm(request.POST)

        if form.is_valid():

            search = form.cleaned_data["search"]

            searchResult = util.get_entry(search)

            if searchResult:
                return render(request, "encyclopedia/entry.html", {
                    "title": search,
                    "entry": util.get_entry(search)
                })

            else:
                for entry in util.list_entries():
                    if entry.lower().startswith(search.lower()):
                        request.session["subsearch"] += [entry]
                        return render(request, "encyclopedia/index.html", {
                            "title": search,
                            "entries": request.session["subsearch"]
                        })
                    
            return HttpResponseRedirect(reverse("encyclopedia:index"))     
