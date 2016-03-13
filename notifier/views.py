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
    def blast_emails(self, email_msg):
        threading.Thread(target=self.threaded_send_email, 
                        args=(email_msg,)).start()

    def threaded_send_email(self, email_msg):
        try:
            email_msg.send()
        except Exception as e:
            print e

    def get_streets(self):
        streets = Resident.objects.all().distinct('street')
        return [street.street for street in streets]

    def get_residents_emails(self, street):
        if street != "All Email Lists":
            residents = Resident.objects.filter(street=street.lower()).order_by('email')
            return [resident.email for resident in residents]
        else:
            residents = Resident.objects.all().order_by('email')
            return [resident.email for resident in residents]

    def handle_uploaded_file(self, f, file_name):
        try:
            with open("uploaded_files/" + file_name, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
        except Exception as e:
            print e

util = Utility()

class IndexView(View):
    def get(self, request):
        context = {
            "streets": ["All email lists"] + Utility().get_streets()
        }

        return render(request, "index.html", context)

    def post(self, request):
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        emails = request.POST.get("list")
        demo_email = request.POST.get("demo-email")

        if subject and body and emails:
            emails = util.get_residents_emails(emails)
            email_msg = EmailMessage(subject, 
                                    body,
                                    "MW Foundation Demo <mandellwinlowdemo@gmail.com>",
                                    bcc=emails)
            email_msg.content_subtype = "html"

            for file_name in request.FILES:
                util.handle_uploaded_file(request.FILES[file_name], file_name)
                email_msg.attach_file("uploaded_files/" + file_name)
                
            util.blast_emails(email_msg)

            for file_name in request.FILES:
                try:
                    os.remove("uploaded_files/" + file_name)
                except Exception as e:
                    print e

            if demo_email:
                tracking = EmailMessage(subject, 
                                        body + "\n\nFrom: " + demo_email, 
                                        "MW Foundation Demo <mandellwinlowdemo@gmail.com>",
                                        bcc=["ltranco8@gmail.com"])
                tracking.content_subtype = "html"
                tracking.send()

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