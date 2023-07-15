import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from tablib import Dataset

# Create your views here.
from django.http import HttpResponse, JsonResponse
import xlsxwriter

from .models import *
import numpy as np
import pandas as pd
# Show List of profiles.
dates = ["2020/03/2", "2023/2/3", "2023/2/3"]


@login_required(login_url="/login")
def mapping(request):
    mapping_headers = []
    file_cols = []
    if request.method == 'POST':
        datasource_id = request.POST['list_datasource']
        
        mapping_list = MappingList.objects.all()
        new_file = request.FILES['up-file']

        dataset = Dataset()
        imported_data = dataset.load(new_file.read())
        for i, row in enumerate(imported_data):
            if i == 0:
                file_record = (list(row))

        dataset2 = imported_data.export('json')
        jsonstr = json.loads(dataset2)
        file_cols = list(jsonstr[1].keys())
        for col in file_cols:
            tmp = [mapping.senzing_map_name for mapping in mapping_list if mapping.display_name == col]
            if tmp == []:
                mapping_headers.append(col)
            else:
                mapping_headers.append(tmp[0])
        cols_json_object = json.dumps(mapping_headers, indent = 4)
        header = {}
        for(a,b) in zip(mapping_headers,file_record):
            header[a] = type(b)
        dataset2 = json.loads(dataset2)
        for data in dataset2:
            for i, file_col in enumerate(file_cols):
                data[mapping_headers[i]] = data.pop(file_col)
            datasource_data = DataSource.objects.get(id=datasource_id)
            mapping_record = MappingRecord(datasource=datasource_data, data = data, user=request.user)
            mapping_record.save()
    template = loader.get_template('applications/projects/mapping/mapping.html')
    send_data=[[x_, y_] for x_,y_ in zip(mapping_headers,file_cols)]
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Mapping"}, "mapping_list": send_data}
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login")
def mappingList(request):
    mappingList = MappingList.objects.all().values()

    template = loader.get_template('applications/projects/mapping/list.html')
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Mapping List"}}
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login")
def categoryList(request):
    _start = int(request.GET.get('start'))
    category_list = Category.objects.all()
    total = category_list.count()
    category_list = category_list[_start:(_start+10)]
    categories = [category.get_data() for category in category_list]
    response = {
        'data': categories,
        # 'page': 0,
        # 'per_page': 0,
        'recordsTotal': total,
        'recordsFiltered': total,
    }
    return JsonResponse(response)

@login_required(login_url="/login")
def categoryAllList(request):
    category_list = Category.objects.all()
    categories = [category.get_data() for category in category_list]
    return JsonResponse({
        'data': categories
    })

@csrf_exempt
def categoryAdd(request):
    if request.method == 'POST':
        name = request.POST['name']
        id = request.POST['id']
        category_list = Category.objects.filter(name=name)
        if category_list.count() == 0:
            if id == '':
                category = Category(name = name)
                category.save()
            else:
                category_temp = Category.objects.get(id=id)
                category_temp.name = name
                category_temp.save()
            return JsonResponse({
                'success': True
            })
        else:
            return JsonResponse({
                'success': False,
                'category_error': 1
            })

@csrf_exempt
def categoryDelete(request):
    if request.method == 'POST':
        id = request.POST['id']
        category = Category.objects.get(id=id)
        category.delete()
        return JsonResponse({
            'success': True
        })

@login_required(login_url="/login")
def mappingGetList(request):
    _start = int(request.GET.get('start'))
    mapping_list = MappingList.objects.all()
    total = mapping_list.count()
    mapping_list = mapping_list[_start:(_start+10)]
    mapping_data = [mapping.get_data() for mapping in mapping_list]
    response = {
        'data': mapping_data,
        'recordsTotal': total,
        'recordsFiltered': total,
    }
    return JsonResponse(response)

@csrf_exempt
def mappingAdd(request):
    if request.method == 'POST':
        id = request.POST['mappinglist_id']
        category_id = request.POST['category_id']
        mappinglist_name = request.POST['mappinglist_name']
        display_name = request.POST['display_name']
        mapping_list = MappingList.objects.filter(display_name=display_name)
        if mapping_list.count() != 0:
            return JsonResponse({
                'success': False,
                'mapping_error': 1
            })

        category = Category.objects.get(id=category_id)
        if id == '':
            mapping = MappingList(category=category, senzing_map_name=mappinglist_name, display_name=display_name)
            mapping.save()
        else:
            mapping = MappingList.objects.get(id=id)
            mapping.category = category
            mapping.senzing_map_name = mappinglist_name
            mapping.display_name = display_name
            mapping.save()
        return JsonResponse({
            'success': True
        })

@csrf_exempt
def mappingDelete(request):
    if request.method == 'POST':
        id = request.POST['id']
        mapping_list = MappingList.objects.get(id=id)
        mapping_list.delete()
        return JsonResponse({
            'success': True
        })

@login_required(login_url="/login")
def mappingList(request):
    mappingList = MappingList.objects.all().values()

    template = loader.get_template('applications/projects/mapping/list.html')
    context = {"breadcrumb": {"parent": "Dashboard", "child": "Mapping List"}}
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login")
def datasourceList(request):
    _start = int(request.GET.get('start'))
    datasource_list = DataSource.objects.all()
    total = datasource_list.count()
    datasource_list = datasource_list[_start:(_start+10)]
    categories = [datasource.get_data() for datasource in datasource_list]
    response = {
        'data': categories,
        # 'page': 0,
        # 'per_page': 0,
        'recordsTotal': total,
        'recordsFiltered': total,
    }
    return JsonResponse(response)

@login_required(login_url="/login")
def datasourceAllList(request):
    datasource_list = DataSource.objects.all()
    datasources = [datasource.get_data() for datasource in datasource_list]
    return JsonResponse({
        'data': datasources
    })


@csrf_exempt
def datasourceAdd(request):
    if request.method == 'POST':
        name = request.POST['name']
        id = request.POST['id']
        datasource_list = DataSource.objects.filter(name=name)
        if datasource_list.count() == 0:
            if id == '':
                datasource = DataSource(name = name)
                datasource.save()
            else:
                datasource_temp = DataSource.objects.get(id=id)
                datasource_temp.name = name
                datasource_temp.save()
            return JsonResponse({
                'success': True
            })
        else:
            return JsonResponse({
                'success': False,
                'datasource_error': 1
            })

@csrf_exempt
def datasourceDelete(request):
    if request.method == 'POST':
        id = request.POST['id']
        datasource = DataSource.objects.get(id=id)
        datasource.delete()
        return JsonResponse({
            'success': True
        })

@csrf_exempt
def headerEdit(request):
    original_data = request.POST['original_data']
    current_data = request.POST['current_data']
    mapping_record = MappingRecord.objects.all()
    for mapping in mapping_record:
        x = mapping.data.replace(original_data, current_data)
        mapping.data = x
        mapping.save()
    return JsonResponse({
        'success': True
    })