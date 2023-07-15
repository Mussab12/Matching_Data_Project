from django.urls import path
from . import views


"""
URLs for mapping
"""
app_name = 'mapping'
urlpatterns = [
    path("", views.mapping, name="mapping"),
    path("list", views.mappingList, name="mapping-list"),
    path("category/list", views.categoryList, name="mapping-category-list"),
    path("category/all", views.categoryAllList, name="mapping-category-list"),
    path("category/add", views.categoryAdd, name="mapping-category-add"),
    path("category/delete", views.categoryDelete, name="mapping-category-delete"),
    path("mapping/list", views.mappingGetList, name='mapping-getlist'),
    path("mapping/add", views.mappingAdd, name='mapping-add'),
    path("mapping/delete", views.mappingDelete, name='mapping-delete'),
    path("datasource/list", views.datasourceList, name="mapping-datasource-list"),
    path("datasource/all", views.datasourceAllList, name="mapping-datasource-list"),
    path("datasource/add", views.datasourceAdd, name="mapping-datasource-add"),
    path("datasource/delete", views.datasourceDelete, name="mapping-datasource-delete"),
    path("header/edit", views.headerEdit, name="mapping-header-edit")
]
