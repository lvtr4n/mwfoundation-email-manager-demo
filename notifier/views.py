from django.shortcuts import render, redirect
from django.views.generic import View
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from notifier.models import Resident

import threading
import json
import os

class Utility():
    """ Send email to a list of email addresses in the background. """
    def blast_emails(self, subject, body, emails, html=False):
        threading.Thread(target=self.threaded_send_email, 
            args=(subject, body, emails, html)).start()

    def threaded_send_email(self, subject, body, emails, html=False):
        if html:
            for email in emails:
                send_mail(subject, "", 'MW Security Foundation', [email],
                    fail_silently=False, 
                    html_message=body)
        else:
            for email in emails:
                send_mail(subject, body, 'ltranco8@gmail.com', [email], 
                    fail_silently=False)

    def get_streets(self):
        streets = Resident.objects.all().distinct('street')
        return [street.street for street in streets]

    def get_residents_emails(self, street):
        residents = Resident.objects.filter(street=street.lower()).order_by('email')
        return [resident.email for resident in residents]

    def handle_uploaded_file(self, f, file_name):
        with open("uploaded_files/" + file_name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

util = Utility()

class IndexView(View):
    def get(self, request):
        context = {
            "streets": ["All streets"] + Utility().get_streets()
        }

        return render(request, "index.html", context)

    def post(self, request):
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        emails = request.POST.get("list")

        if subject and body and emails:
            if emails == "All Streets":
                emails = [resident.email for resident in Resident.objects.all()]
            else:
                emails = util.get_residents_emails(emails)

            #emails = ["ltranco8@gmail.com"]
            email_msg = EmailMessage(subject, body, 'MW Foundation', emails)
            email_msg.content_subtype = "html"

            for file_name in request.FILES:
                util.handle_uploaded_file(request.FILES[file_name], file_name)
                email_msg.attach_file("uploaded_files/" + file_name)

            email_msg.send()

            for file_name in request.FILES:
                os.remove("uploaded_files/" + file_name)

            #util.blast_emails(subject, body, emails, html=True)
            return HttpResponse('true')
        return HttpResponse('false')

class ListView(View):
    def get_context(self):
        streets = util.get_streets()
        emails = [util.get_residents_emails(street) for street in streets]
        context = {
            "data": zip(streets, emails)
        }
        return context

    def get(self, request):
        context = self.get_context()
        return render(request, "list.html", context)

    def post(self, request):
        list_name = request.POST.get("list_name")
        if list_name:
            if "create_list" in request.POST:
                    if not Resident.objects.filter(street=list_name):
                        resident = Resident()
                        resident.street = list_name
                        resident.email = "example@mwpatrol.com"
                        resident.save()             
            elif "delete_list" in request.POST:
                Resident.objects.filter(street=list_name).delete()
            elif "export" == list_name:
                return JsonResponse(self.get_context())
            else:
                try:
                    emails = request.POST.getlist("emails[]")
                    Resident.objects.filter(street=list_name).delete()
                    for email in emails:
                        resident = Resident()
                        resident.email = email
                        resident.street = list_name
                        resident.save()
                    return HttpResponse('200')
                except Exception as e:
                    print e
                    return HttpResponse('500')
        context = self.get_context()
        return render(request, "list.html", context)