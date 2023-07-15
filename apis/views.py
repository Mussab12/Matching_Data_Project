import json
import operator
import re
from string import punctuation
import simplejson as json
import numpy as np
from django.core.cache import cache
import traceback

from collections import defaultdict


from celery.result import AsyncResult
from django.contrib import auth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from leven import levenshtein
from rest_framework.parsers import JSONParser
from django.apps import apps
import requests


from sklearn.cluster import dbscan
from django.http import Http404
from rest_framework import status
from data_profile.models import DataProfile, DataPattern
from vihoapp.global_func import checkifDataType, checkDateType
from .tasks import test_data, profile_columns, data_profile_task
from viho.celery import app
import pandas as pd
from apis.models import exceldata, CustomerMaster, NewProsectRecords, MatchingConfig
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.response import Response
from .serializers import ExceldataSerializer, CustomerMasterSerializer, ModelNameSerializer, MatchingConfigSerializer
import re
from datetime import datetime
import logging


# Check if the celery worker is alive or dead
def get_celery_worker_status():
    try:
        app.broker_connection().ensure_connection(max_retries=1)
    except Exception as ex:
        return "error"


"""
@desc
    api for data_profile
@param
    pk:id of DataProfile
@response
    id of task event
"""


@csrf_exempt
def run_data_profile(request):
    pk = request.POST.get('id', None)
    d = get_celery_worker_status()
    if d == "error":
        return JsonResponse({"error": "error"}, status=500)

    current_user = auth.get_user(request)

    # Run the celery task
    try:
        task = data_profile_task.delay(pk, current_user.id)
        return JsonResponse({"task_id": task.id}, status=202)
    except Exception as e:
        logging.getLogger().debug("Profile Task is failed")
        return JsonResponse({"error": "error"}, status=500)


@csrf_exempt
def run_data_profile_status(request):
    taskIDs = request.POST.get('task_ids', None)

    if taskIDs is not None:
        taskIDs = json.loads(taskIDs)
        result = []
        for task in taskIDs:
            task_result = AsyncResult(task["task_id"])
            if task_result.state == "FAILURE":
                result.append({
                    'task_id': task["task_id"],
                    'state': task_result.state
                })
            else:
                result.append({
                    'task_id': task["task_id"],
                    'state': task_result.state,
                    'progress': task_result.info,
                })
        return JsonResponse({"result": result}, status=200)
    else:
        return JsonResponse({"error": "error"}, status=500)

# @api to make the data in uppercase


class ExceldataupperView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            upper1 = str(i.Company_Name).upper()
            print(upper1)
            data1.append(upper1)
            data = {"company_name": upper1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to make the data in lowercase


class ExceldatalowerView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            lower1 = str(i.Company_Name).lower()
            print(lower1)
            data1.append(lower1)
            data = {"company_name": lower1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to make the data capitalize


class ExceldatacapitalizeView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            capitalize1 = str(i.Company_Name).capitalize()
            print(capitalize1)
            data1.append(capitalize1)
            data = {"company_name": capitalize1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to remove the punctuations from data


class ExceldataremovepunctuationsView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            companyname = str(i.Company_Name)
            punctuations1 = re.sub(r'[^\w\s]', '', companyname)
            data1.append(punctuations1)
            data = {"company_name": punctuations1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to remove the spaces from data


class ExceldataremovespaceView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            space1 = str(i.Company_Name).replace(" ", "")
            data1.append(space1)
            data = {"company_name": space1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)


# @api to remove the numbers from data
class ExceldataremovenumbersView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            companyname = str(i.Company_Name)
            numbers1 = re.sub(r'\d+', '', companyname)
            data1.append(numbers1)
            data = {"company_name": numbers1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to remove the letters from data


class ExceldataremovelettersView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            companyname = str(i.Company_Name)
            letters1 = re.sub(r'[a-zA-Z]', '', companyname)
            data1.append(letters1)
            data = {"company_name": letters1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to remove the leading spaces from data


class ExceldataremovelspaceView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            lspace1 = str(i.Company_Name).lstrip()
            data1.append(lspace1)
            data = {"company_name": lspace1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to remove the trailing spaces from data


class ExceldataremoverspaceView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            rspace1 = str(i.Company_Name).rstrip()
            data1.append(rspace1)
            data = {"company_name": rspace1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to remove the non printable characters from data


class ExceldataremovenpcView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            companyname = str(i.Company_Name)
            pattern = r'[\x00-\x1F\x7F-\x9F]'
            npcharacter1 = re.sub(pattern, '', companyname)
            data1.append(npcharacter1)
            data = {"company_name": npcharacter1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

 # @api to replace string with another string


class ExceldatareplacestringView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            replace1 = str(i.Company_Name).replace("A", "B")
            data1.append(replace1)
            data = {"company_name": replace1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)

# @api to fill blanks with static test


class ExceldatafillblanksView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data1 = []
        if exceldata.objects.all():
            exceldata.objects.all().delete()
        for i in dataframe1.itertuples():
            blank1 = str(i.Company_Name).replace("nan", "test")
            data1.append(blank1)
            data = {"company_name": blank1}
            serializer = ExceldataSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return Response({"company_name": data1}, status=201)


# @api to copy data from one column to another column
class ExceldatacopycolumnView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        copy_column = dataframe1['Company_Name'].copy()
        insert_index = dataframe1.columns.get_loc('Company_Name') + 1
        dataframe1.insert(insert_index, 'Copy_Column', copy_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/copy1.xlsx', index=False)
        return HttpResponse("Excel created with copy column", status=201)

# @api to insert new column left


class ExceldatanewcolumnleftView(APIView):
    def post(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        new_column_left = ""
        column = request.data["column"]
        range1 = request.data["range1"]
        range2 = int(range1)
        for i in range(range2):
            insert_index = dataframe1.columns.get_loc(column)
            dataframe1.insert(
                insert_index, f'New_Column_left+{i}', new_column_left)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/newcolumnleft.xlsx', index=False)
        return HttpResponse("Excel created with new column left", status=201)

# @api to insert new column right


class ExceldatanewcolumnrightView(APIView):
    def post(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        new_column_right = ""
        column = request.data["column"]
        range1 = request.data["range1"]
        range2 = int(range1)
        for i in range(range2):
            insert_index = dataframe1.columns.get_loc(column) + 1
            dataframe1.insert(
                insert_index, f'New_Column_Right+{i}', new_column_right)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/newcolumnright.xlsx', index=False)
        return HttpResponse("Excel created with new column right", status=201)

# @api to merge column


class ExceldatamergecolumnView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        separator = ','
        merged_column = dataframe1['Company_Name'].astype(
            str).str.cat(sep=separator)
        insert_index = dataframe1.columns.get_loc('Company_Name') + 1
        # dataframe1 = dataframe1.drop('Company_Name', axis=1)
        dataframe1.insert(insert_index, 'Company_name', merged_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/mergecolumn.xlsx', index=False)
        return HttpResponse("Excel created with merge column", status=201)

# @api to split column


class ExceldatasplitcolumnView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        dataframe1[['Emailfirst', 'Emaillast']
                   ] = dataframe1['Email'].str.split("@", expand=True)
        insert_index = dataframe1.columns.get_loc('Email')+1
        dataframe1.insert(insert_index, 'EmailFirst', dataframe1['Emailfirst'])
        dataframe1 = dataframe1.drop('Email', axis=1)
        dataframe1.insert(insert_index, 'EmailLast', dataframe1['Emaillast'])
        dataframe1.to_excel(
            '/home/codenomad/Downloads/splitcolumn.xlsx', index=False)
        return HttpResponse("Excel created with split column", status=201)

# @api to date conversion


class ExceldatadateconversionView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        Birthdate_new1 = Birthdate_new.dt.date
        insert_index = dataframe1.columns.get_loc('Birthdate') + 1
        dataframe1.insert(insert_index, 'Birthdate_New', Birthdate_new1)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/dateformated.xlsx', index=False)
        return HttpResponse("Excel created with new column with formated date", status=201)

# @api to search char


class ExceldatasearchcharView(APIView):
    def post(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        column = request.data["column"]
        search_char = request.data["search_char"]
        newcolumn = request.data["newcolumn"]
        # The character you want to search for
        newcolumn = np.where(
            (dataframe1[column].str.contains(search_char)), 'True', 'False')
        insert_index = dataframe1.columns.get_loc(column) + 1
        dataframe1.insert(insert_index, newcolumn, newcolumn)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/searchchar.xlsx', index=False)
        return HttpResponse("Excel created with new column for search char", status=201)


# @api to search text
class ExceldatasearchtextView(APIView):
    def post(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        column = request.data["column"]
        search_text = request.data["search_text"]
        newcolumn = request.data["newcolumn"]
        newcolumn = np.where(
            (dataframe1[column].str.contains(search_text)), 'True', 'False')
        insert_index = dataframe1.columns.get_loc(column) + 1
        dataframe1.insert(insert_index, 'search_text', newcolumn)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/searchtext.xlsx', index=False)
        return HttpResponse("Excel created with new column for search text", status=201)

# @api to dynamic text for columnn


class ExceldatadynamictextView(APIView):
    def post(self, request, format=None):
        # dataframe1 = pd.read_excel('/home/codenomad/Downloads/Example Data 1.xlsx')
        column1_val = request.data["column1values"]
        column2_val = request.data["column2values"]
        columnn_val = request.data["column3values"]
        data = {"COLUMN1": column1_val,
                "COLUMN2": column2_val,
                "COLUMN3": columnn_val}
        df = pd.DataFrame(data)
        columns = ['COLUMN1', 'COLUMN2', 'COLUMN3']
        dynamic_string = "Text ({}, ({}, ({})))".format(*df[columns].values[0])
        df.to_excel('/home/codenomad/Downloads/searchtext.xlsx', index=False)
        return HttpResponse("Excel created with new column for dynamic text", status=201)

# @api to date coversion in new column


class ExceldatadateconversionView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        Birthdate_new1 = Birthdate_new.dt.date
        insert_index = dataframe1.columns.get_loc('Birthdate') + 1
        dataframe1.insert(insert_index, 'Birthdate_New', Birthdate_new1)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/dateformated.xlsx', index=False)
        return HttpResponse("Excel created with new column with formated date", status=201)

# @api to date coversion overwrite


class ExceldatadateconversionoverwriteView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        dataframe1['Birthdate'] = Birthdate_new.dt.date
        dataframe1.to_excel(
            '/home/codenomad/Downloads/dateformated.xlsx', index=False)
        return HttpResponse("Excel created overwrite in same column with formated date", status=201)

# @api to date coversion with date-month-year


class ExceldatadateconversiondmyView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        Birthdate_new1 = Birthdate_new.dt.strftime('%d-%m-%Y')
        insert_index = dataframe1.columns.get_loc('Birthdate') + 1
        dataframe1.insert(insert_index, 'Birthdate_New', Birthdate_new1)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/date-dmy-formated.xlsx', index=False)
        return HttpResponse("Excel created with new column with formated date(date-month-year)", status=201)

# @api to date coversion date-month-year overwrite


class ExceldatadateconversionodmyView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        dataframe1['Birthdate'] = Birthdate_new.dt.strftime('%d-%m-%Y')
        dataframe1.to_excel(
            '/home/codenomad/Downloads/date-dmyo-formated.xlsx', index=False)
        return HttpResponse("Excel created overwrite in same column with date-month-year formated date", status=201)


# @api to date coversion with month-date-year
class ExceldatadateconversionmdyView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        Birthdate_new1 = Birthdate_new.dt.strftime('%m-%d-%Y')
        insert_index = dataframe1.columns.get_loc('Birthdate') + 1
        dataframe1.insert(insert_index, 'Birthdate_New', Birthdate_new1)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/date-mdy-formated.xlsx', index=False)
        return HttpResponse("Excel created with new column with formated date(monthe-date-year)", status=201)

# @api to date coversion month-date-year overwrite


class ExceldatadateconversionomdyView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Birthdate_new = pd.to_datetime(dataframe1['Birthdate'])
        dataframe1['Birthdate'] = Birthdate_new.dt.strftime('%m-%d-%Y')
        dataframe1.to_excel(
            '/home/codenomad/Downloads/date-mdyo-formated.xlsx', index=False)
        return HttpResponse("Excel created overwrite in same column with month-date-year formated date", status=201)

# @api to extract pattern in new column with matching pattern


class ExceldatapatternmatchView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        pattern = '1065'
        Address_pattern = dataframe1['Address']
        Address_pattern1 = Address_pattern.str.extractall(
            f'({pattern})').unstack()
        print(Address_pattern1)
        Address_pattern1.columns = [
            f'Match {i+1}' for i in range(Address_pattern1.shape[1])]
        print(Address_pattern1.columns)
        insert_index = dataframe1.columns.get_loc('Address') + 1
        dataframe1.insert(insert_index, 'Address_Pattern', Address_pattern1)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/address-pattern.xlsx', index=False)
        return HttpResponse("Excel created with new column with address pattern", status=201)

# @api to extract pattern using regex for number in new column with matching pattern


class ExceldatapatternregexnumbernmatchView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        pattern = r'(?P<zipcode>\d{5})(?:-(?P<extension>\d{4}))?'
        dataframe1[['ZipCode1', 'Extension']
                   ] = dataframe1['ZIP'].str.extract(pattern)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/zip-pattern1.xlsx', index=False)
        return HttpResponse("Excel created with new column with  pattern", status=201)

# @api to extract pattern using regex for string in new column with matching pattern


class ExceldatapatternregexstringnmatchView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        pattern = r'(?P<emailname>[a-z\s]+)(?:@(?P<emailafter>[a-z^\s]+))(?:.(?P<emailafterdot>[a-z\s]+))?'
        dataframe1[['emailname', 'emailafter', 'emailafterdot']
                   ] = dataframe1['Email'].str.extract(pattern)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/email-pattern1.xlsx', index=False)
        return HttpResponse("Excel created with new column with address pattern", status=201)

# @api to extract pattern using regex entered by user in new columns with matching pattern


class ExceldatapatternregexusernmatchView(APIView):
    def post(self, request):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        data = request.data
        print(data)
        column = request.data["column"]
        pattern1 = request.data["pattern"]
        print(pattern1)
        string = pattern1.strip('r')
        pattern2 = r'<([^>]+)>'
        matches = re.findall(pattern2, string)
        i = 0
        patterncolumn = []
        if matches:
            for match in matches:
                i = i+1
                print(f"Match{i}:", match)
                patterncolumn.append(match)
        print(patterncolumn)
        dataframe1[patterncolumn] = dataframe1[column].str.extract(pattern1)
        print(dataframe1[patterncolumn])
        dataframe1.to_excel(
            '/home/codenomad/Downloads/user-pattern1.xlsx', index=False)
        return HttpResponse("Excel created with new column with user pattern", status=201)

# @api to data coversion in meter to inches in new column


class ExceldatadataconversionView(APIView):
    def get(self, request, format=None):
        inch = 39.37
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        distance_new = dataframe1['Distance']*inch
        distance_new1 = distance_new
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'distance_New', distance_new1)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/dateformated.xlsx', index=False)
        return HttpResponse("Excel created with new column with distance", status=201)

# @api to compare two columns data value in new column


class ExceldatadatacomparetcView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        compared_column = dataframe1[['Distance3', 'Distance']].max(axis=1)
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'compared_column', compared_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/comparedcolumn.xlsx', index=False)
        return HttpResponse("Excel created with compared two column result in new column", status=201)

# @api to compare two columns data static value in new column


class ExceldatadatacomparesvView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        compared_column = np.where(
            dataframe1['Distance'] > dataframe1['Distance3'], 'Greater', 'Not Greater')
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'compared_column', compared_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/comparedcolumnsv.xlsx', index=False)
        return HttpResponse("Excel created with compared two column static result in new column", status=201)

# @api to compare two columns data with AND operator in new column


class ExceldatadatacomparesandView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        comparedand_column = np.where(((dataframe1['Distance'] > 40) & (
            dataframe1['Distance3'] > 30)), 'True', 'False')
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'compared_column', comparedand_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/comparedwithand.xlsx', index=False)
        return HttpResponse("Excel created with compared two column with AND operator in new column", status=201)

# @api to compare two columns data with OR operator in new column


class ExceldatadatacomparesorView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        comparedor_column = np.where(((dataframe1['Distance'] > 40) | (
            dataframe1['Distance3'] > 30)), 'True', 'False')
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'compared_column', comparedor_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/comparedwithor.xlsx', index=False)
        return HttpResponse("Excel created with compared two column with OR operator in new column", status=201)

# @api to compare two columns data with Not operator in new column


class ExceldatadatacomparesnotView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        comparednot_column = np.where(
            dataframe1['Distance'] != 40, 'True', 'False')
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'compared_column', comparednot_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/comparedwithnot.xlsx', index=False)
        return HttpResponse("Excel created with compared two column with NOT operator in new column", status=201)

# @api to find two columns sum in new column


class ExceldatacolumnsumView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        sumnew_column = dataframe1['Distance']+dataframe1['Distance3']
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'Sum_column', sumnew_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/columnsum.xlsx', index=False)
        return HttpResponse("Excel created with two columns sum in new column", status=201)

# @api to find two columns Average in new column


class ExceldatacolumnaverageView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        averagenew_column = dataframe1[['Distance', 'Distance3']].mean(axis=1)
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'Average_column', averagenew_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/columnaverage.xlsx', index=False)
        return HttpResponse("Excel created with  two columns average in new column", status=201)

 # @api to find two columns difference in new column


class ExceldatacolumndifferenceView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        Difference_column = dataframe1['Distance']-dataframe1['Distance3']
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'Difference', Difference_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/columndifference.xlsx', index=False)
        return HttpResponse("Excel created with two columns difference in new column", status=201)


# @api to find two columns multiplication in new column
class ExceldatacolumnmultiplyView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        multiply_column = dataframe1['Distance'] * dataframe1['Distance3']
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'Multiply', multiply_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/columnmultiply.xlsx', index=False)
        return HttpResponse("Excel created with two columns multiplication in new column", status=201)

# @api to find two columns division in new column


class ExceldatacolumndivideView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        divide_column = dataframe1['Distance'] / dataframe1['Distance3']
        insert_index = dataframe1.columns.get_loc('Distance3') + 1
        dataframe1.insert(insert_index, 'Divide', divide_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/columndivide.xlsx', index=False)
        return HttpResponse("Excel created with two columns division in new column", status=201)

# @api to find date in range in new column


class ExceldatacolumndaterangeView(APIView):
    def get(self, request, format=None):
        dataframe1 = pd.read_excel(
            '/home/codenomad/Downloads/Example Data 1.xlsx')
        dataframe1['From_Date'] = pd.to_datetime(
            dataframe1['From_Date'], format="%d-%m-%Y")
        dataframe1['To_Date'] = pd.to_datetime(
            dataframe1['To_Date'], format="%d-%m-%Y")
        daterange_column = np.where(
            (dataframe1['From_Date'] < dataframe1['To_Date']), 'InRange', 'OutRange')
        insert_index = dataframe1.columns.get_loc('To_Date')+1
        dataframe1.insert(insert_index, 'DateRange', daterange_column)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/columndaterange.xlsx', index=False)
        return HttpResponse('Excel created with date in range or out of range in new colummn')

# @api to validate date in range in new column


class ExceldatadatevalidateView(APIView):
    def get(self, request, format=None):
        from_date_str = "2023-06-01"
        to_date_str = "2023-06-15"
        # Convert the date strings to datetime objects
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d")
        if from_date < to_date:
            return HttpResponse('date is valid')
        else:
            return HttpResponse('date is invalid')

# @api to validate email


class ExceldataemailvalidateView(APIView):
    def get(self, request, format=None):
        email = "test@gmail.com"
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        emailvalid = re.fullmatch(regex, email)
        if emailvalid:
            return HttpResponse('email is  valid')
        else:
            return HttpResponse('email is not valid')

# @api to validate phone number


class ExceldataphonevalidateView(APIView):
    def get(self, request, format=None):
        phone = "+114455778899"
        regex = r'^\+?\d{1,3}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
        phonevalid = re.fullmatch(regex, phone)
        if phonevalid:
            return HttpResponse('phone is  valid')
        else:
            return HttpResponse('phone is not valid')

# @api to validate list for string values


class ListdatastringvalidateView(APIView):
    def post(self, request, format=None):
        data1 = request.data
        dataframe1 = pd.DataFrame(data1)
        dataframe1.columns = ['Column1']
        pattern = r'^[a-zA-Z]+$'
        dataframe1['Column2'] = dataframe1['Column1'].astype(
            str).str.match(pattern)
        dataframe1.to_excel(
            '/home/codenomad/Downloads/uploadlist.xlsx', index=False)
        return HttpResponse('uploaded list converted in excel')

# @api to upload dictionary


class UploaddictionaryView(APIView):
    def post(self, request):
        data1 = request.data
        print(data1)
        df = pd.DataFrame(data1)
        df.to_excel(
            '/home/codenomad/Downloads/uploaddictionary.xlsx', index=False)
        return HttpResponse('uploaded dictionary converted in excel')

# @api to replace value in upload dictionary


class DictionaryreplacevaluesView(APIView):
    def post(self, request):
        data1 = request.data
        string1 = request.data["string1"]
        string2 = request.data["string2"]
        columname = request.data["column"]
        newcolumname = request.data["newcolumn"]
        df = pd.DataFrame(data1)
        df[newcolumname] = df[columname].str.replace(string1, string2)
        df.to_excel(
            '/home/codenomad/Downloads/dictionaryvaluesreplaced.xlsx', index=False)
        return HttpResponse('dictionary values replaced in column')

# @api to remove duplicates value in dictionary


class DictionaryremoveduplicatesView(APIView):
    def post(self, request):
        data1 = request.data
        print(data1)
        df = pd.DataFrame(data1)
        columname = request.data["column"]
        newcolumname = request.data["newcolumn"]
        df[newcolumname] = df[columname].drop_duplicates()
        df.to_excel(
            '/home/codenomad/Downloads/dictionaryremoveuplicates.xlsx', index=False)
        return HttpResponse('dictionary values remove duplicates in column')

# @api to length of string in dictionary


class DictionarystringlenView(APIView):
    def post(self, request):
        data1 = request.data
        print(data1)
        df = pd.DataFrame(data1)
        columname = request.data["column"]
        newcolumname = request.data["newcolumn"]
        df[newcolumname] = df[columname].str.len()
        df.to_excel(
            '/home/codenomad/Downloads/dictionarystringlen.xlsx', index=False)
        return HttpResponse('dictionary for length of string in column')

# @api to parse the string in dictionary


class DictionarystringparseView(APIView):
    def post(self, request):
        data1 = request.data["data1"]
        print(data1)
        delimiter = request.data["delimiter"]
        newcolumn = request.data["newcolumn"]
        values = re.split(delimiter, data1)
        data_array = [values[i] for i in range(0, len(values))]
        df = pd.DataFrame(data_array, columns=[newcolumn])
        df.to_excel(
            '/home/codenomad/Downloads/dictionarystringparse.xlsx', index=False)
        return HttpResponse(f'dictionary for string parse  in column')

# @api to parse the string in dictionary


class DictionarystringdeleteView(APIView):
    def post(self, request):
        data1 = request.data["data1"]
        string1 = request.data["string1"]
        column = request.data["column"]
        newcolumn = request.data["newcolumn"]
        df = pd.DataFrame(data1, columns=[column])
        print(data1)
        df[newcolumn] = df.replace(string1, '')
        df.to_excel(
            '/home/codenomad/Downloads/dictionarystringparse.xlsx', index=False)
        return HttpResponse(f'dictionary for string parse  in column')

# @api to count the string in dictionary


class DictionarystringcountView(APIView):
    def post(self, request):
        data1 = request.data
        print(data1)
        df = pd.DataFrame(data1)
        columname = request.data["column"]
        stringcount = request.data["stringcount"]
        string_count = df[columname].value_counts()
        desired_string = stringcount
        count1 = string_count[desired_string]
        # df.to_excel('/home/codenomad/Downloads/dictionarystringcount.xlsx', index=False)
        return HttpResponse(f'dictionary for string {stringcount} counts are {count1}  in column')

# @api to get values for valid and invalid


class ExceldatagetvalidinvalidView(APIView):
    def post(self, request):
        df = pd.read_excel('/home/codenomad/Downloads/columndaterange.xlsx')
        column = request.data["column"]
        newcolumn = request.data["newcolumn"]
        # condition1=request.data["condition"]
        df[newcolumn] = np.where((df[column] < 70), 'valid', 'invalid')
        df.to_excel('/home/codenomad/Downloads/columndategetvalidinvalid.xlsx')
        return HttpResponse('Excel get the valid & invalid values from the excel')


# @api to delete values for valid and invalid
class ExceldatadeletevaluesView(APIView):
    def post(self, request):
        df = pd.read_excel('/home/codenomad/Downloads/columndaterange.xlsx')
        column1 = request.data['column1']
        value = request.data['value']
        column2 = request.data['column2']

        # df = df[df['DateRange'] == 'InRange']
        df.loc[df[column1] == value, column2] = ''
        df.to_excel('/home/codenomad/Downloads/columndatedeleteinvalid.xlsx')
        return HttpResponse('Excel deleted the invalid values from the excel')

# @api to change static values for valid and invalid


class ExceldatastaticvaluesView(APIView):
    def post(self, request):
        df = pd.read_excel('/home/codenomad/Downloads/columndaterange.xlsx')
        # df = df[df['DateRange'] == 'InRange']
        column1 = request.data['column1']
        value = request.data['value']
        column2 = request.data['column2']
        rep_value = request.data['replacevalue']
        df.loc[df[column1] == value, column2] = rep_value
        df.to_excel('/home/codenomad/Downloads/columndatestaticvalues.xlsx')
        return HttpResponse('Excel deleted the static values from the excel')

# @api to change use original values for valid and invalid


class ExceldataoriginalvaluesView(APIView):
    def post(self, request):
        df = pd.read_excel('/home/codenomad/Downloads/columndaterange.xlsx')
        column1 = request.data['column1']
        value1 = request.data['value1']
        value2 = request.data['value2']
        df = df[(df[column1] == value1) | (df[column1] == value2)]
        df.to_excel('/home/codenomad/Downloads/columndateoriginalvalues.xlsx')
        return HttpResponse('Excel deleted the original values from the excel')

# @api to convert excel records to JSON


class ExcelToJson(APIView):
    def post(self, request, format=None):
        try:
            xlsx_file = request.FILES['xlsxFile']  # Access the uploaded file

            dataframe1 = pd.read_excel(xlsx_file)
            dataframe2 = pd.read_excel(xlsx_file)

            extracteddata = dataExtraction(dataframe1)

            json_data1 = convertExceltoJson(extracteddata)
            # json_data2 = json.loads(dataframe2.to_json(orient='records'))
            # customer_master = CustomerMaster(data1=json_data1)
            # customer_master.save()
            newprospect_records = CustomerMaster(data1=json_data1)
            newprospect_records.save()

            # Separate status code and JSON data
            return Response({'message': 'Successfully Added', 'data': json_data1})
        except Exception as e:
            # Log the error or perform any necessary error handling steps
            traceback_str = traceback.format_exc()
            print(f"An error occurred: {str(e)}")
            print(traceback_str)

            # Return an error response
            return Response({'error': f'An error occurred. Please try again later. {str(e)}'}, status=500)

    def get(self, request, format=None):
        customer_master = CustomerMaster.objects.all()

        serializer = CustomerMasterSerializer(customer_master, many=True)

        return Response(serializer.data)

    def delete(self, request, format=None):
        customer_master = CustomerMaster.objects.all()
        customer_master.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


get_checked_values = []

# @api to define matching configuration


class MatchingConfigView(APIView):
    def post(self, request, format=None):
        checked_values = request.data.get('checked_values', [])

        if 'customer_master' in checked_values:

            queryset = CustomerMaster.objects.all()
            for model in queryset:
                related_model = CustomerMaster.objects.filter(
                    data1=model.data1).first()
                model.relationship = related_model
                model.save()
            serializer = CustomerMasterSerializer(queryset, many=True)

            return Response({'relationship_data': serializer.data})

    def get(self, request, format=None):
        # Retrieve the matching configuration or perform any additional processing
        matching_config = MatchingConfig.objects.all()
        serializer = MatchingConfigSerializer(matching_config, many=True)
        return Response(serializer.data)

        # Return the matching configuration in the response


# @api to get modal names
class ModelNameAPIView(APIView):
    def get(self, request, format=None):
        model_names = [
            CustomerMaster._meta.verbose_name,
            NewProsectRecords._meta.verbose_name,
            # Add more model verbose names as needed
        ]
        return JsonResponse(model_names, safe=False, json_dumps_params={'ensure_ascii': False})


# Function to read excel file

def readExcelfile():
    dataframe = pd.read_excel("apis\Example Data 1.xlsx")
    return dataframe

# Function to Convert Excel to Json


def convertExceltoJson(exceldata):
    return json.loads(exceldata.to_json(
        orient='records'))


# Function to Extract Data From Excel File
def dataExtraction(dataframe):
    dataframe['Account Code'] = extractDigits(dataframe['Account Code'])
    dataframe['Phone'] = extractDigits(dataframe['Phone'])
    dataframe['ZIP'] = extractDigits(dataframe['ZIP'])
    dataframe['National ID'] = extractDigits(dataframe['National ID'])
    dataframe['Birthdate'] = extractDate(dataframe['Birthdate'])
    dataframe['Creation Date'] = extractDate(dataframe['Creation Date'])
    dataframe['Modify Date'] = extractDate(dataframe['Modify Date'])
    dataframe['City'] = capitalizeFirstLetter(dataframe['City'])

    return dataframe


# Function to remove unwanted data from columns that contain numbers and extract numbers from Excel File
def extractDigits(column):
    return column.apply(lambda x: re.sub(r'\D', '', str(x)) if pd.notnull(x) else '')


def extractDate(column):
    if column.dtype == 'datetime64[ns]':
        return column.dt.strftime('%d-%m-%Y')
    elif column.dt.strftime('%m-%d-%Y'):
        return column.dt.strftime('%m-%d-%Y')


def capitalizeFirstLetter(column):
    return column.str.capitalize()
