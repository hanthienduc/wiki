from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from . import util
from html.parser import HTMLParser


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


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
        return render(request, "encyclopedia/error.html", {
            "title": "Not found"
        })
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


class NewPageForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(
        label="content", widget=forms.Textarea)

    def editForm(self, title, content):
        self.title = forms.CharField(label="title", initial={title})
        self.content = forms.CharField(
            label="content", widget=forms.Textarea, initial={content})


def create_page(request):
    if request.method == "POST":

        form = NewPageForm(request.POST)

        if form.is_valid():

            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            checkEntry = util.get_entry(title)
            if not checkEntry:

                util.save_entry(title, content)
                return render(request, "encyclopedia/entry.html", {
                    "title": title,
                    "entry": util.get_entry(title)
                })
            else:
                return render(request, "encyclopedia/create.html", {
                    "title_page": title + " already included",
                    "showbutton": False
                })
        else:
            return render(request, "encyclopedia/error.html", {
                "title": "Form invalid"
            })

    return render(request, "encyclopedia/create.html", {
        "title_page": "Create Page",
        "showbutton": True,
        "pageform": NewPageForm()
    })


class EditForm(forms.Form):
    title = forms.CharField(label="title", initial={title})
    content = forms.CharField(
        label="content", widget=forms.Textarea, initial={content})


def edit_page(request):

    if(request.method == "POST"):

        if 'title' and 'content' in request.POST:
            title = 'You editing for: %r' % request.POST['title']
            f = HTMLFilter()
            f.feed(request.POST['content'])
            content = f.text
            return render(request, "encyclopedia/edit.html", {
                "formedit": EditForm(title, content)
            }
            )
        else:
            title = 'You submitted an empty form.'

    else:

        return HttpResponse("Invalid data")


    return render(request, "encyclopedia/edit.html", {
        "formedit": EditForm()
    }
    )
