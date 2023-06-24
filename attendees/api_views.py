from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee
from events.models import Conference
from events.api_views import ConferenceListEncoder, ConferenceDetailEncoder
from attendees.api_views import Attendee
from django.views.decorators.http import require_http_methods
import json


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder()
    }


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceDetailEncoder()
    }


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


    """
    Lists the attendees names and the link to the attendee
    for the specified conference id.

    Returns a dictionary with a single key "attendees" which
    is a list of attendee names and URLS. Each entry in the list
    is a dictionary that contains the name of the attendee and
    the link to the attendee's information.

    {
        "attendees": [
            {
                "name": attendee's name,
                "href": URL to the attendee,
            },
            ...
        ]
    }
    """
    # response = []
    # attendees = Attendee.objects.all()
    # for attendee in attendees:
    #     response.append(
    #         {
    #             "name": attendee.name,
    #             "href": attendee.get_api_url(),
    #         }
    #     )
    # return JsonResponse({"attendees": response})


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, id):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})

    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference = Conference.objects.get(id=content["conference"])
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Attendee does not exist"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    # attendee = Attendee.objects.get(id=id)
    # return JsonResponse(
    #     {
    #         "email": attendee.email,
    #         "name": attendee.name,
    #         "company_name": attendee.company_name,
    #         "created": attendee.created,
    #         "conference": {
    #             "name": attendee.conference.name,
    #             "href": attendee.conference.get_api_url(),
    #         },
    #     }
    # )

