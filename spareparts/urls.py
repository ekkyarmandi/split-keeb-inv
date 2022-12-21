from django.urls import path

from . import views

urlpatterns = [

    ### Home
    path('', views.Home.as_view(), name="home"),
    path('summary/', views.Summary.as_view(), name="summary"),

    ### Orders
    path('orders/', views.OrdersView.as_view(), name="orders"),
    path('orders/<int:pk>/edit/', views.EditOrderView.as_view(), name="edit-order"),
    path('orders/<int:pk>/delete/', views.delete_order, name="delete-order"),
    path('new-order/', views.NewOrderView.as_view(), name="new-order"),

    ### Spareparts
    path('spareparts/', views.SparepartsView.as_view(), name="spareparts"),
    path('update-arrival/<int:pk>/', views.update_arrival, name="update-arrival"),
    path('edit-sparepart/<int:pk>/', views.edit_sparepart, name="edit-sparepart"),

]