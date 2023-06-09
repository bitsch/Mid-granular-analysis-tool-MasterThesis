from django.http import JsonResponse

def get_active_groups(request):

    if request.session["group_details"] is None:
        return None

    existing_groups = request.session["group_details"]
    datas = {}
    counter = 1
    for key, value in existing_groups.items():
        if existing_groups[key]["status"] == "active":
            group_name = key
            number_of_activities = format(
                len(existing_groups[key]["selected_activities"].split(","))
            )
            data = {
                "group_name": group_name,
                "number_of_activities": number_of_activities,
            }
            datas[counter] = data
            counter = counter + 1
    return datas

def check_group_managment(request):
    """ """
    return "group_details" in request.session







