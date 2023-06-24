from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
from events.acl import get_photo, get_weather_data
import json


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]
    

class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]

@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Location object and put it in the content dict
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )

        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


# def api_list_conferences(request):
#     """
#     Lists the conference names and the link to the conference.

#     Returns a dictionary with a single key "conferences" which
#     is a list of conference names and URLS. Each entry in the list
#     is a dictionary that contains the name of the conference and
#     the link to the conference's information.

#     {
#         "conferences": [
#             {
#                 "name": conference's name,
#                 "href": URL to the conference,
#             },
#             ...
#         ]
#     }
#     """
#     response = []
#     conferences = Conference.objects.all()
#     for conference in conferences:
#         response.append(
#             {
#                 "name": conference.name,
#                 "href": conference.get_api_url(),
#             }
#         )
#     return JsonResponse({"conferences": response})

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        city = conference.location.city
        state = conference.location.state
        weather = get_weather_data(city, state)
        
        return JsonResponse(
            {"conference": conference, "weather": weather},
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)

        # Get the Location object and put it in the content dict
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )

        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


    # conference = Conference.objects.get(id=id)
    # return JsonResponse(
    #     {
    #         "name": conference.name,
    #         "starts": conference.starts,
    #         "ends": conference.ends,
    #         "description": conference.description,
    #         "created": conference.created,
    #         "updated": conference.updated,
    #         "max_presentations": conference.max_presentations,
    #         "max_attendees": conference.max_attendees,
    #         "location": {
    #             "name": conference.location.name,
    #             "href": conference.location.get_api_url(),
    #         },
    #     }
    # )


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder
        )
    else:
        content = json.loads(request.body)

        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
        
        picture_url = get_photo(
            content["city"], content["state"].abbreviation 
        )
        content.update(picture_url)

        location = Location.objects.create(**content)
        
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

    """
    Lists the location names and the link to the location.

    Returns a dictionary with a single key "locations" which
    is a list of location names and URLS. Each entry in the list
    is a dictionary that contains the name of the location and
    the link to the location's information.

    {
        "locations": [
            {
                "name": location's name,
                "href": URL to the location,
            },
            ...
        ]
    }
    """


    # response = []
    # locations = Location.objects.all()
    # for location in locations:
    #     response.append(
    #         {
    #             "name": location.name,
    #             "href": location.get_api_url()
    #         }
    #     )
    # return JsonResponse({"locations": response})

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    if request.method == "GET":
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    
    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        # new code
        Location.objects.filter(id=id).update(**content)

        # copied from get detail
        location = Location.objects.get(id=id)
        if location.picture_url is None:
            picture_url = get_photo(
                location.city, location.state.abbreviation
            )
            location.picture_url = picture_url["picture_url"]
            location.save()
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

        
        
    

# def api_show_location(request, id):
    """
    Returns the details for the Location model specified
    by the id parameter.

    This should return a dictionary with the name, city,
    room count, created, updated, and state abbreviation.

    {
        "name": location's name,
        "city": location's city,
        "room_count": the number of rooms available,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "state": the two-letter abbreviation for the state,
    }
    """

    location = Location.objects.get(id=id)
    return JsonResponse(
        {
            "name": location.name,
            "city": location.city,
            "room_count": location.room_count,
            "created": location.created,
            "updated": location.updated,
            "state": location.state.abbreviation,
        }
    )