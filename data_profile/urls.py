from django.urls import path
from . import views

app_name = 'data_profile'
urlpatterns = [
    path("", views.profileList, name="profile-list"),

    path("profile/create/", views.createProfile, name="profile-create"),
    path("profile/<int:pk>", views.showProfile, name="profile-show"),
    path("patterns/", views.patternList, name="pattern-list"),
    path("patterns/list", views.getPatternListAjax, name="pattern-list-ajax"),
    path("patterns/store", views.storePattern, name="pattern-store"),
    path("patterns/delete", views.deletePattern, name="pattern-delete"),
    path("patterns/edit", views.editPattern, name="pattern-edit"),
    path("patterns/store/select", views.storeSelectPattern,
         name="pattern-select-store"),
    path("profile/result/nonPrintableDetail", views.getNonPrintableDetail),
    path("profile/result/nullFilled", views.getNullFilledDetail),
    path("profile/result/punctuation", views.getPunctuationDetail),
    path("profile/result/pattern", views.getPatternDetail),
    path("profile/result/pattern/detail", views.getPatternPerDetail),
    path("profile/result/distinct", views.getDistinctDetail),
    path("profile/result/export/<int:pk>",
         views.exportProfile, name="profile-export"),
    path("profile/history/<int:pk>",
         views.showHistoryProfile, name="profile-history"),
    path("profile/result/detail", views.showDetailRecords),
    path("profile/result/detail/export", views.exportDetail),
    path("profile/result/geo", views.geoRecords),
    path("profile/result/showGEO", views.show_geomap)
]
