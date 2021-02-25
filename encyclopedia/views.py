from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from . import util
from html.parser import HTMLParser

from random import randint

import markdown2


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
            "entry": markdown2.markdown(util.get_entry(name)),
            "entryToSend": util.get_entry(name),
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
                    "title": search.upper(),
                    "entry": markdown2.markdown(util.get_entry(search)),
                    "entryToSend": util.get_entry(search),
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
                    "title": title.upper(),
                    "entry": markdown2.markdown(util.get_entry(title)),
                    "entryToSend": util.get_entry(title),
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
    content = forms.CharField(
        label="content", widget=forms.Textarea)


def edit_page(request):

    if(request.method == "POST"):

        if 'title' and 'content' in request.POST:
            title = request.POST['title']
            f = HTMLFilter()
            f.feed(request.POST['content'])
            content = f.text

            initial_dict = {
                "content": content
            }

            form = EditForm(request.POST or None, initial=initial_dict)

            return render(request, "encyclopedia/edit.html", {
                "formedit": form,
                "title": title,
                "content": content
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


class SaveEditForm(forms.Form):
    title = forms.CharField(label="title")
    content = forms.CharField(
        label="content", widget=forms.Textarea)


def save_edit(request):

    if(request.method == "POST"):

        form = SaveEditForm(request.POST)

        if form.is_valid():

            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            checkEntry = util.get_entry(title)

            if checkEntry:

                util.save_entry(title, content)
                return render(request, "encyclopedia/entry.html", {
                    "title": title.upper(),
                    "entry": markdown2.markdown(util.get_entry(title)),
                    "entryToSend": util.get_entry(title),
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "title": "Form invalid"
                })
        else:
            initial_dict = {
                "title": title,
                "content": content
            }
            form = SaveEditForm(request.POST or None, initial=initial_dict)

            return render(request, "encyclopedia/edit.html", {
                "formedit": form,
                "title": title,
                "content": content
            }
            )


def random_page(request):
    # get all entries title
    entriesTitle = util.list_entries()

    # create random number based on entries length
    value = randint(0, len(entriesTitle) - 1)
    # create random title based on random number
    ranDomTitle = entriesTitle[value]
    # get list entry based on random number
    entry = util.get_entry(ranDomTitle)

    # render the entry with the data
    return render(request, "encyclopedia/entry.html", {
        "title": ranDomTitle.upper(),
        "entry": markdown2.markdown(entry),
        "entryToSend": entry,
    })
