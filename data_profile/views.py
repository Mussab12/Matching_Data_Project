import json
import re
from io import BytesIO

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
import xlsxwriter
from geopy.exc import GeocoderTimedOut

from .models import *
from apis.tests import test_data
from apis.tests import profile_columns
import logging
from leven import levenshtein
from sklearn.cluster import dbscan
import numpy as np
from vihoapp.global_func import checkifDataType, checkDateType
import pandas as pd
from geopy.geocoders import Nominatim
from django.template.loader import render_to_string


@login_required(login_url="/login")
def profileList(request):
    """
        Return the profile list from db and renders to the html template
    """
    current_user = auth.get_user(request)
    profiles = DataProfile.objects.filter(user=current_user).values()
    template = loader.get_template(
        'applications/projects/data-profile/list.html')
    context = {"breadcrumb": {"parent": "Dashboard",
                              "child": "Profile List", }, "data": profiles}
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login")
def matchingConfig(request):
    """
        Return the profile list from db and renders to the html template
    """
    current_user = auth.get_user(request)
    profiles = DataProfile.objects.filter(user=current_user).values()
    template = loader.get_template(
        'applications/projects/data-profile/matchconfig.html')
    context = {"breadcrumb": {"parent": "Dashboard",
                              "child": "Match Config", }, "data": profiles}
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login")
def createProfile(request):
    """
        Renders the create profile form and saves the form info to the db
    """
    context = {"breadcrumb": {"parent": "Projects", "child": "Profile Create"}}
    if request.method == "POST":
        # if form is submitted, save to the db
        current_user = auth.get_user(request)
        try:
            name = request.POST.get('name')
            data_source = request.POST.get('data_source')
            email_address = request.POST.get('emails')
            details = request.POST.get('details')
            output_name = request.POST.get('data_source_output', None)
            if output_name is None:
                output_name = name + "_output"
            profile = DataProfile(name=name, data_source=data_source, email_address=email_address, details=details,
                                  user=current_user, data_source_output=output_name)
            profile.save()
            msg = "Project Create Successfully"
        except Exception as e:
            msg = "Project Create Failed"
            logging.getLogger().debug("Create Profile Failed")
        return redirect(reverse_lazy('data_profile:profile-list'), {"msg": msg, "name": name})

    return render(request, 'applications/projects/data-profile/create.html', context)


@login_required(login_url="/login")
def showProfile(request, pk):
    """
        Renders the detailed profile from db
        Arguments
            @pk - profile id
    """
    try:
        profile = DataProfileHistory.objects.get(pk=pk)
        data = json.loads(profile.profile_result)

        # Calculate the histogram and prepare the data to draw histogram bar
        histogram_data_keys = []
        histogram_data_values = []

        for index, column_item in enumerate(profile_columns.keys()):
            histogram_per_item_data = {}
            for item in test_data:
                column_data = item[column_item]
                if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
                    continue
                if column_data in histogram_per_item_data.keys():
                    histogram_per_item_data[column_data] += 1
                else:
                    histogram_per_item_data[column_data] = 1

            # sort histogram data asc order
            histogram_per_item_data = dict(
                sorted(histogram_per_item_data.items(), key=lambda kv: kv[1], reverse=True))
            histogram_per_item_data_keys = list(histogram_per_item_data.keys())
            histogram_per_item_data_values = list(
                histogram_per_item_data.values())
            # only shows 20 histogram data
            if len(histogram_per_item_data_keys) > 20:
                histogram_per_item_data_keys = histogram_per_item_data_keys[:20]
                histogram_per_item_data_values = histogram_per_item_data_values[:20]

            histogram_data_keys.append(
                json.dumps(histogram_per_item_data_keys))
            histogram_data_values.append(
                json.dumps(histogram_per_item_data_values))

            # calculate the invalid/total fields percentage
            if data["type_column"][index]["valid"] == 0 or data["type_column"][index]["valid"] < \
                    data["type_column"][index]["invalid"]:
                data["type_column"][index]["typePercent"] = 0
            else:
                data["type_column"][index]["typePercent"] = (data["type_column"][index]["valid"] -
                                                             data["type_column"][index]["invalid"]) / \
                    data["type_column"][index]["valid"] * 100
                data["type_column"][index]["typePercent"] = round(
                    data["type_column"][index]["typePercent"], 2)
            overallScore = 0
            overallScore_class = "bg-danger"

            overallScore = sum([data["score"][item] for item in data["score"]])
            if overallScore >= 90:
                overallScore_class = "bg-primary"
            elif overallScore >= 70:
                overallScore_class = "bg-warning"
    except Exception as e:
        logging.getLogger().debug("Get Detailed Profile is failed")

    context = {"breadcrumb": {"parent": "Projects", "child": "Profile"}, "data": data,
               "columns": profile_columns.keys(),
               "profile_id": pk, "histogram_data_keys": histogram_data_keys,
               "profile_time": profile.profile_time,
               "histogram_data_values": histogram_data_values,
               "overall_score": overallScore,
               "overallScore_class": overallScore_class}
    return render(request, 'applications/projects/data-profile/show.html', context)


@login_required(login_url="/login")
def patternList(request):
    """
        Render the list of patterns from db
    """
    context = {"breadcrumb": {"parent": "Projects", "child": "Patterns"}}
    return render(request, 'applications/projects/data-profile/patterns/list.html', context)


def storePattern(request):
    """
        Create a new pattern from pattern forms
        Returns a JsonResponse if pattern is created correctly.
    """
    patternName = request.POST.get('name', None)
    patternType = request.POST.get('type', None)
    patternPattern = request.POST.get('pattern', None)
    patternID = request.POST.get('id', None)

    patternID = int(patternID)
    if not (patternName is None or patternType is None or patternPattern is None or patternID is None):

        # check if pattern is valid or not
        try:
            patternRegEx = re.compile(patternPattern)
        except Exception as e:
            logging.getLogger().debug("New Pattern is invalid")
            return JsonResponse({"error": "pattern"}, status=500)
        # if we edit and save
        if patternID is not None and patternID != -1:
            try:
                pattern = DataPattern.objects.get(pk=patternID)

                pattern.name = patternName
                pattern.type = patternType
                pattern.pattern = patternPattern
                pattern.save()
            except Exception as e:
                logging.getLogger().debug("Pattern Edit is failed")
                return JsonResponse({"error": "error"}, status=500)
        # if we create a new pattern
        elif patternID is not None and patternID == -1:
            pattern = DataPattern(
                name=patternName, type=patternType, pattern=patternPattern)
            pattern.save()
        return JsonResponse({"success": "success"}, status=200)
    else:
        return JsonResponse({"error": "error"}, status=500)


def getPatternListAjax(request):
    """
        Returns a JsonResponse with all patterns from db
    """
    patterns = DataPattern.objects.all().values()
    return JsonResponse({"patterns": list(patterns)})


def deletePattern(request):
    """
        Delete a pattern using pattern id and
        Returns a JsonResponse of the result
    """
    patternID = request.POST.get('id', None)
    if patternID is not None:
        try:
            DataPattern.objects.get(pk=patternID).delete()
            return JsonResponse({"success": "success"}, status=200)
        except Exception as e:
            logging.getLogger().debug("Delete Pattern is failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def editPattern(request):
    """
        Get a pattern using id to edit pattern and
        Returns a JsonResponse with pattern
    """
    patternID = request.POST.get('id', None)
    if patternID is not None:
        pattern = DataPattern.objects.filter(pk=patternID).values()
        return JsonResponse({"pattern": list(pattern)}, status=200)
    else:
        return JsonResponse({"error": "error"}, status=500)


def storeSelectPattern(request):
    """
        Get marked patterns, updates these patterns to selected = true and
        Returns a JsonResponse with the updating result
    """
    patterns = DataPattern.objects.all().values()
    patterns.update(selected=False)
    selectedIDs = request.POST.getlist('selected[]', None)
    if selectedIDs is not None:
        for selectedID in selectedIDs:
            pattern = DataPattern.objects.get(pk=selectedID)
            pattern.selected = True
            pattern.save()
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "error"}, status=500)


def getNonPrintableDetail(request):
    """
        Get Non-Printable statistics with profile id and profile column name
        Returns a non-printable data
    """
    profileID = request.GET.get('profile_id', None)
    profileColumn = request.GET.get('profile_column', None)
    if profileID is not None and profileColumn is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(profileColumn)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            return JsonResponse({"data": [profile_result["character_columns"][profileColumn]["leading_space"],
                                          profile_result["character_columns"][profileColumn]["trailing_space"],
                                          profile_result["character_columns"][profileColumn][
                                              "non_printable_character"]]})
        except Exception as e:
            logging.getLogger().debug("Get NonPrintable Statistics failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def getNullFilledDetail(request):
    """
        Get Null/Filled Detail with profile id and profile column name
        Returns Null/Filled fields
    """
    profileID = request.GET.get('profile_id', None)
    profileColumn = request.GET.get('profile_column', None)
    if profileID is not None and profileColumn is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(profileColumn)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            return JsonResponse({"data": [profile_result["field_column"][profileColumn]["filled_fields"],
                                          profile_result["field_column"][profileColumn]["null_fields"]]})
        except Exception as e:
            logging.getLogger().debug("Get Null/Filled Data failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def getPunctuationDetail(request):
    """
        Get Punctuation Statistics with profile id and profile column name
        Returns Null/Filled fields
    """
    profileID = request.GET.get('profile_id', None)
    profileColumn = request.GET.get('profile_column', None)
    if profileID is not None and profileColumn is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(profileColumn)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            return JsonResponse({"data": profile_result["character_columns"][profileColumn]["punctuation_count"],
                                 "total_records": profile_result["total_rows"]})
        except Exception as e:
            logging.getLogger().debug("Get Punctuation Statistics failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def getPatternDetail(request):
    """
        Get Pattern Details with profile id and profile column name, sort by valid counts
        Returns sorted pattern detail
    """
    profileID = request.GET.get('profile_id', None)
    profileColumn = request.GET.get('profile_column', None)
    if profileID is not None and profileColumn is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(profileColumn)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            patternResult = []
            for index, item in enumerate(profile_result["pattern_columns"][profileColumn]):
                # only show valid Patterns
                if item > 0:
                    patternResult.append({
                        "pattern": {"id": index, "name": profile_result["selected_patterns"][index]["name"]},
                        "valid": item
                    })
            # sort by valid counts as asc order
            patternResult.sort(key=lambda x: x["valid"], reverse=True)
            return JsonResponse({"data": patternResult})
        except Exception as e:
            logging.getLogger().debug("Get Pattern Details failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def getPatternPerDetail(request):
    """
        Get Pattern Statistics with profile id, profile column name, selected pattern id
        Returns pattern records
    """
    profileID = request.GET.get('profile_id', None)
    profileColumn = request.GET.get('profile_column', None)
    patternID = request.GET.get('pattern_id', None)
    if profileID is not None and profileColumn is not None and patternID is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(profileColumn)
            patternID = int(patternID)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)

            # Get column of selected Pattern
            patternGraphData = [profile_result["total_rows"],
                                profile_result["pattern_columns"][profileColumn][patternID],
                                profile_result["total_rows"] - profile_result["pattern_columns"][profileColumn][
                                    patternID]]
            patternRegEx = re.compile(
                profile_result["selected_patterns"][patternID]["pattern"])

            # store detected columns
            patternDetectedData = []
            for item in test_data:
                if patternRegEx.match(item[list(profile_columns.keys())[profileColumn]]):
                    patternDetectedData.append({
                        "data": item[list(profile_columns.keys())[profileColumn]],
                        "valid": 1
                    })
                else:
                    patternDetectedData.append({
                        "data": item[list(profile_columns.keys())[profileColumn]],
                        "valid": 0
                    })
            return JsonResponse({"graphData": patternGraphData, "DetectedData": patternDetectedData})
        except Exception as e:
            logging.getLogger().debug("Get Pattern Statistics with pattern id failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def getDistinctDetail(request):
    """
        Get Pattern Statistics with profile id, profile column name
        Returns pattern records
    """
    profileID = request.GET.get('profile_id', None)
    profileColumn = request.GET.get('profile_column', None)
    _columns = ["key", "frequency", "percent"]
    if profileID is not None and profileColumn is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(profileColumn)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            histogram_per_item_data = {}
            for item in test_data:
                # check if data is null or blank.

                column_data = item[list(profile_columns.keys())[profileColumn]]
                if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
                    continue
                if column_data in histogram_per_item_data.keys():
                    histogram_per_item_data[column_data] += 1
                else:
                    histogram_per_item_data[column_data] = 1
            result_data = []
            histogram_index = 1
            # get distinct key, frequency, percent
            for histogram_column in histogram_per_item_data.keys():
                result_data.append({
                    "key": histogram_column,
                    "frequency": histogram_per_item_data[histogram_column],
                    "percent": histogram_per_item_data[histogram_column] /
                    profile_result["field_column"][profileColumn][
                        "filled_fields"] * 100,
                })
                histogram_index += 1

            r = dict(request.GET)
            # Generate datatable return data
            return_data = {
                'draw': r["draw"][0],
                'recordsTotal': len(result_data),
                'recordsFiltered': len(result_data),
                'data': []}

            dt_order_col = int(r["order[0][column]"][0])
            dt_order_dir = r["order[0][dir]"][0]

            # sort by datatable order
            if dt_order_dir == 'asc':
                result_data = sorted(
                    result_data, key=lambda d: d[_columns[dt_order_col]], reverse=False)
            else:
                result_data = sorted(
                    result_data, key=lambda d: d[_columns[dt_order_col]], reverse=True)

            dt_length = int(request.GET.get('length', 0))
            dt_start = int(request.GET.get('start', 0))
            return_data["data"] = result_data[dt_start:dt_start + dt_length]
            return JsonResponse(return_data, safe=False, status=200)
        except Exception as e:
            logging.getLogger().debug("Get DistinctDetail failed")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def exportProfile(request, pk):
    """
        Generate a excel report response for profile summary
    """

    output = BytesIO()
    profile = DataProfileHistory.objects.get(pk=pk)
    data = json.loads(profile.profile_result)

    # Define Excel sheet headers
    accuracy_header = ["Column Name", "Max Length", "Leading Spaces", "Trailing Spaces", "Non-Printable Characters",
                       "Null", "Filled", "Punctuation"]
    uniqueness_header = ["Column Name", "Total Rows", "Distinct"]
    conformity_header = ["Column Name", "Data Type",
                         "Date Format", "Valid", "Invalid", "Invalid Percent"]
    precision_header = ["Column Name", "Min", "Max", "Mean", "Median", "Mode"]
    workbook = xlsxwriter.Workbook(output)
    # Create an Accuracy Tab and write data
    worksheet = workbook.add_worksheet("Accuracy")

    # Write Header Name
    for index, name in enumerate(accuracy_header):
        worksheet.write(0, index, name)

    # Write Accuracy data
    for index, column in enumerate(profile_columns):
        worksheet.write(index + 1, 0, column)
        worksheet.write(index + 1, 1, data["maxlen_columns"][index])
        worksheet.write(
            index + 1, 2, data["character_columns"][index]["leading_space"])
        worksheet.write(
            index + 1, 3, data["character_columns"][index]["trailing_space"])
        worksheet.write(
            index + 1, 4, data["character_columns"][index]["non_printable_character"])
        worksheet.write(
            index + 1, 5, data["field_column"][index]["null_fields"])
        worksheet.write(
            index + 1, 6, data["field_column"][index]["filled_fields"])
        worksheet.write(index + 1, 7, sum([data["character_columns"][index]["punctuation_count"][item] for item in
                                           data["character_columns"][index]["punctuation_count"]]))

    worksheet = workbook.add_worksheet("Uniqueness")
    # Write Uniqueness data
    for index, name in enumerate(uniqueness_header):
        worksheet.write(0, index, name)
    for index, column in enumerate(profile_columns):
        worksheet.write(index + 1, 0, column)
        worksheet.write(
            index + 1, 1, data["field_column"][index]["filled_fields"])
        worksheet.write(
            index + 1, 2, data["field_column"][index]["distinct_fields"])

    worksheet = workbook.add_worksheet("Conformity")
    # Conformity
    worksheet.merge_range(0, 0, 0, 1, "")
    worksheet.merge_range(0, 2, 0, 5, "Type")
    for index, name in enumerate(conformity_header):
        worksheet.write(1, index, name)
    for index, column in enumerate(profile_columns):
        worksheet.write(index + 1, 0, column)
        worksheet.write(index + 1, 1, data["type_column"][index]["type"])
        worksheet.write(index + 1, 2, data["type_column"][index]["format"])
        worksheet.write(index + 1, 3, data["type_column"][index]["valid"])
        worksheet.write(index + 1, 4, data["type_column"][index]["invalid"])
        worksheet.write(index + 1, 4,
                        data["type_column"][index]["invalid"] / data["field_column"][index]["filled_fields"] * 100)

    # Precision
    worksheet = workbook.add_worksheet("Precision")
    for index, name in enumerate(precision_header):
        worksheet.write(1, index, name)
    for index, column in enumerate(profile_columns):
        worksheet.write(index + 1, 0, column)
        worksheet.write(index + 1, 1, data["precision_column"][index]["min"])
        worksheet.write(index + 1, 2, data["precision_column"][index]["max"])
        worksheet.write(index + 1, 3, data["precision_column"][index]["mean"])
        worksheet.write(
            index + 1, 4, data["precision_column"][index]["median"])
        worksheet.write(index + 1, 5, data["precision_column"][index]["mode"])
    workbook.close()

    # create a response
    response = HttpResponse(content_type='application/vnd.ms-excel')

    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename="profile_summary.xlsx"'

    # put the spreadsheet data into the response
    response.write(output.getvalue())

    # return the response
    return response


def showHistoryProfile(request, pk):
    """
        Shows the history results of profile
        returns a profile history view
            :param
                pk: profile id
    """
    profileHistoryData = DataProfileHistory.objects.filter(
        profile_id=pk).order_by("-created_at")

    template = loader.get_template(
        'applications/projects/data-profile/history/list.html')
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Profile History", }, "data": profileHistoryData,
               "profile_id": pk}
    return HttpResponse(template.render(context, request))


def getMaxLengthRecords(profileID, column_index, value):
    """
        Returns the MaxLength Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_item = item[list(profile_columns.keys())[column_index]]
        if column_item == "null" or column_item == "NULL" or column_item == "Null" or column_item == "":
            continue
        if len(column_item) == value:
            result.append({
                "name": column_item
            })
    return result


def getNullorFilledFields(profileID, column_index, value):
    """
        Returns the Null/Filled Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            if value == 0:
                result.append({
                    "name": column_data
                })
        else:
            if value == 1:
                result.append({
                    "name": column_data
                })

    return result


def getContainNumbersFields(profileID, column_index):
    """
        Returns the Contain Numbers Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        digit_contain = any(c.isdigit() for c in column_data)
        if digit_contain:
            result.append({
                "name": column_data
            })

    return result


def getNumbersOnlyFields(profileID, column_index):
    """
        Returns the Numbers Only Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        if column_data.isnumeric():
            result.append({
                "name": column_data
            })

    return result


def getContainLettersFields(profileID, column_index):
    """
        Returns the Contains Letters Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        letters_contain = any(not c.isdigit() for c in column_data)
        if letters_contain:
            result.append({
                "name": column_data
            })

    return result


def getLettersOnlyFields(profileID, column_index):
    """
        Returns the Letters Only Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        digit_contain = any(c.isdigit() for c in column_data)
        if not digit_contain:
            result.append({
                "name": column_data
            })

    return result


def getNumbersAndLettersFields(profileID, column_index):
    """
        Returns the Numbers and Letters Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        digit_contain = any(c.isdigit() for c in column_data)
        letter_contain = any(not c.isdigit() for c in column_data)
        if (digit_contain and letter_contain) and not (column_data.isnumeric() or not digit_contain):
            result.append({
                "name": column_data
            })

    return result


def getLeadingSpaceFields(profileID, column_index):
    """
        Returns the Records containing leading space
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue

        if column_data.startswith(' '):
            result.append({
                "name": column_data
            })

    return result


def getTrailingSpaceFields(profileID, column_index):
    """
        Returns the Records containing trailing space
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue

        if column_data.endswith(' '):
            result.append({
                "name": column_data
            })

    return result


def getNonPrintableCharacterFields(profileID, column_index):
    """
        Returns the Records containing non printable characters
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue

        if not column_data.isprintable():
            result.append({
                "name": column_data
            })

    return result


def getOutlierDetectionFields(profileID, column_index):
    """
        Returns the Outlier Detection fields
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []
    outlierData = []
    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        outlierData.append(column_data)

    def lev_metric(x, y):
        i, j = int(x[0]), int(y[0])  # extract indices
        return levenshtein(outlierData[i], outlierData[j])

    X = np.arange(len(outlierData)).reshape(-1, 1)
    core_samples, labels = dbscan(X, metric=lev_metric, eps=5, min_samples=2)
    for index, label in enumerate(labels):
        if label == -1:
            result.append({
                "name": outlierData[index]
            })
    return result


def getValidFields(profileID, column_index, type_data):
    """
        Returns the Valid data format records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []

    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        if checkifDataType(type_data["type"], column_data):
            result.append({
                "name": column_data
            })
        if type_data["type"] == "date":
            if checkDateType(column_data) != type_data["format"]:
                result.pop()

    return result


def getInValidFields(profileID, column_index, type_data):
    """
        Returns the Invalid Records
            :param
                profileID: profile ID
                column_index: column index
    """
    result = []

    for item in test_data:
        column_data = item[list(profile_columns.keys())[column_index]]
        if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
            continue
        if not checkifDataType(type_data["type"], column_data):
            result.append({
                "name": column_data
            })
        elif type_data["type"] == "date":
            if checkDateType(column_data) != type_data["format"]:
                result.append({
                    "name": column_data
                })

    return result


def showDetailRecords(request):
    """
        Returns the JsonResponse for detailed records
            :param
                profileID: profile ID
                attr: data attributes
                index: column index

    """
    profileID = request.GET.get('profile_id', None)
    attr = request.GET.get('attr', None)
    column_index = request.GET.get('index', None)
    _columns = ["name"]
    if profileID is not None and attr is not None and column_index is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(column_index)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            records_array = None
            if attr == "maxlen_columns":
                records_array = getMaxLengthRecords(profileID, profileColumn,
                                                    profile_result["maxlen_columns"][profileColumn])
            elif attr == "null_fields":
                records_array = getNullorFilledFields(
                    profileID, profileColumn, 0)
            elif attr == "filled_fields":
                records_array = getNullorFilledFields(
                    profileID, profileColumn, 1)
            elif attr == "contain_numbers":
                records_array = getContainNumbersFields(
                    profileID, profileColumn)
            elif attr == "numbers_only":
                records_array = getNumbersOnlyFields(profileID, profileColumn)
            elif attr == "contain_letters":
                records_array = getContainLettersFields(
                    profileID, profileColumn)
            elif attr == "letters_only":
                records_array = getLettersOnlyFields(profileID, profileColumn)
            elif attr == "contain_letters_numbers":
                records_array = getNumbersAndLettersFields(
                    profileID, profileColumn)
            elif attr == "leading_space":
                records_array = getLeadingSpaceFields(profileID, profileColumn)
            elif attr == "trailing_space":
                records_array = getTrailingSpaceFields(
                    profileID, profileColumn)
            elif attr == "non_printable_character":
                records_array = getNonPrintableCharacterFields(
                    profileID, profileColumn)
            elif attr == "outlier_detection":
                records_array = getOutlierDetectionFields(
                    profileID, profileColumn)
            elif attr == "valid":
                records_array = getValidFields(
                    profileID, profileColumn, profile_result["type_column"][profileColumn])
            elif attr == "invalid":
                records_array = getInValidFields(
                    profileID, profileColumn, profile_result["type_column"][profileColumn])
            r = dict(request.GET)
            # Generate datatable return data
            return_data = {
                'draw': r["draw"][0],
                'recordsTotal': len(records_array),
                'recordsFiltered': len(records_array),
                'data': []}

            dt_order_col = int(r["order[0][column]"][0])
            dt_order_dir = r["order[0][dir]"][0]

            # sort by datatable order
            if dt_order_dir == 'asc':
                records_array = sorted(
                    records_array, key=lambda d: d[_columns[dt_order_col]], reverse=False)
            else:
                records_array = sorted(
                    records_array, key=lambda d: d[_columns[dt_order_col]], reverse=True)

            dt_length = int(request.GET.get('length', 0))
            dt_start = int(request.GET.get('start', 0))
            return_data["data"] = records_array[dt_start:dt_start + dt_length]

            return JsonResponse(return_data, safe=False, status=200)
        except Exception as e:
            logging.getLogger().debug("Get Detail Records got errors")
            return JsonResponse({"error": "error"}, status=500)
    else:
        return JsonResponse({"error": "error"}, status=500)


def geoRecords(request):
    """
            Returns the JsonResponse for ZIP Records
                :param
                    profileID: profile ID
                    index: column index

        """
    profileID = request.GET.get('profile_id', None)
    column_index = request.GET.get('index', None)
    _columns = ["name"]
    if profileID is not None and column_index is not None:
        profileID = int(profileID)
        profileColumn = int(column_index)
        records_array = []

        for item in test_data:
            column_data = item[list(profile_columns.keys())[profileColumn]]
            if column_data == "null" or column_data == "NULL" or column_data == "Null" or column_data == "":
                continue
            records_array.append({
                "name": "<a role='button' onclick=" + "displayGEO('" + column_data + "')>" + column_data + "</a>"
            })
        r = dict(request.GET)
        # Generate datatable return data
        return_data = {
            'draw': r["draw"][0],
            'recordsTotal': len(records_array),
            'recordsFiltered': len(records_array),
            'data': []}

        dt_order_col = int(r["order[0][column]"][0])
        dt_order_dir = r["order[0][dir]"][0]

        # sort by datatable order
        if dt_order_dir == 'asc':
            records_array = sorted(
                records_array, key=lambda d: d[_columns[dt_order_col]], reverse=False)
        else:
            records_array = sorted(
                records_array, key=lambda d: d[_columns[dt_order_col]], reverse=True)

        dt_length = int(request.GET.get('length', 0))
        dt_start = int(request.GET.get('start', 0))
        return_data["data"] = records_array[dt_start:dt_start + dt_length]

        return JsonResponse(return_data, safe=False, status=200)


def exportDetail(request):
    """
            Returns the Excel File for detailed records
                :param
                    profileID: profile ID
                    attr: data attributes
                    index: column index

        """
    profileID = request.GET.get('profile_id', None)
    attr = request.GET.get('attr', None)
    column_index = request.GET.get('index', None)

    if profileID is not None and attr is not None and column_index is not None:
        try:
            profileID = int(profileID)
            profileColumn = int(column_index)
            profile_result = json.loads(
                DataProfileHistory.objects.get(pk=profileID).profile_result)
            records_array = None
            if attr == "maxlen_columns":
                records_array = getMaxLengthRecords(profileID, profileColumn,
                                                    profile_result["maxlen_columns"][profileColumn])
            elif attr == "null_fields":
                records_array = getNullorFilledFields(
                    profileID, profileColumn, 0)
            elif attr == "filled_fields":
                records_array = getNullorFilledFields(
                    profileID, profileColumn, 1)
            elif attr == "contain_numbers":
                records_array = getContainNumbersFields(
                    profileID, profileColumn)
            elif attr == "numbers_only":
                records_array = getNumbersOnlyFields(profileID, profileColumn)
            elif attr == "contain_letters":
                records_array = getContainLettersFields(
                    profileID, profileColumn)
            elif attr == "letters_only":
                records_array = getLettersOnlyFields(profileID, profileColumn)
            elif attr == "contain_letters_numbers":
                records_array = getNumbersAndLettersFields(
                    profileID, profileColumn)
            elif attr == "leading_space":
                records_array = getLeadingSpaceFields(profileID, profileColumn)
            elif attr == "trailing_space":
                records_array = getTrailingSpaceFields(
                    profileID, profileColumn)
            elif attr == "non_printable_character":
                records_array = getNonPrintableCharacterFields(
                    profileID, profileColumn)
            elif attr == "outlier_detection":
                records_array = getOutlierDetectionFields(
                    profileID, profileColumn)
            elif attr == "valid":
                records_array = getValidFields(
                    profileID, profileColumn, profile_result["type_column"][profileColumn])
            elif attr == "invalid":
                records_array = getInValidFields(
                    profileID, profileColumn, profile_result["type_column"][profileColumn])
            output = BytesIO()
            header = ["Records"]
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet("records")

            # Write Header Name
            for index, name in enumerate(header):
                worksheet.write(0, index, name)

            for index, column in enumerate(records_array):
                worksheet.write(index + 1, 0, column["name"])
            workbook.close()

            # create a response
            response = HttpResponse(content_type='application/vnd.ms-excel')

            # tell the browser what the file is named
            response['Content-Disposition'] = 'attachment;filename="ouput_detail.xlsx"'

            # put the spreadsheet data into the response
            response.write(output.getvalue())

            # return the response
            return response
        except Exception as e:
            logging.getLogger().debug("Get Detail Records got errors")
            return JsonResponse({"error": "error"}, status=500)


def get_coordinates_from_postal_code(postal_code):
    """
        Returns the latitude and longitude from postal code using Nominatim
            :param
                postal code: zip code value

    """
    geolocator = Nominatim(
        user_agent='my-vihoapp')  # Replace 'my-app' with your user agent
    location = None

    try:
        location = geolocator.geocode(postal_code, timeout=10)
    except GeocoderTimedOut:
        return get_coordinates_from_postal_code(postal_code)

    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None, None


def show_geomap(request):
    """
        Returns the iframe HTML with google map
    """
    postal_code = request.GET.get('postal_code', None)
    latitude, longitude = get_coordinates_from_postal_code(postal_code)
    api_key = settings.GMAP_API_KEY
    if latitude and longitude:
        # Pass the latitude and longitude, api key to the template
        html = render_to_string('applications/projects/data-profile/components/geomap.html', {
                                'latitude': latitude, 'longitude': longitude, 'api_key': api_key})
        return JsonResponse(html, safe=False)

    else:
        error_message = f"No location found for postal code: {postal_code}"
        html = render_to_string(
            'applications/projects/data-profile/components/geomap.html', {'error_message': error_message})
        return JsonResponse(html, safe=False)
