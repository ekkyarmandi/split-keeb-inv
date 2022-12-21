from django.urls import path

from .views import *

urlpatterns = [

    ### Build Logs
    path('', BuildLogView.as_view(), name='build-logs'),
    path('create/', NewBuildLog.as_view(), name='new-build'),
    path('<int:pk>/', EditBuildLog.as_view(), name='edit-build'),
    path('<int:pk>/delete/', delete_build_log, name='delete-build'),
    path('<int:pk>/sold/', build_sold_out, name='sold-build'),

    ### Item Out
    path('item-out/', ItemOutView.as_view(), name='item-out'),
    path('<int:pk>/cancel-item/', cancel_item_out, name="cancel-item"),

    ### API
    path('get-spareparts/', get_spareparts),
]