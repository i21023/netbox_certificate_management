from django.urls import path
from . import models, views
from netbox.views.generic import ObjectChangeLogView

urlpatterns=(
    path('certificates/', views.CertificateListView.as_view(), name='certificate_list'),
    path('certificates/add', views.CertificateEditView.as_view(), name='certificate_add'),
    path('certificates/<int:pk>/edit/', views.CertificateEditView.as_view(), name='certificate_edit'),
    path('certificates/<int:pk>/', views.CertificateView.as_view(), name='certificate_detail'),
    path('certificates/<int:pk>/delete/', views.CertificateDeleteView.as_view(), name='certificate_delete'),
    path('certificates/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='certificate_changelog', kwargs={
        'model': models.Certificate
    }),
    path('certificates/upload/', views.upload_file, name='upload_file'),
    path('certificates/download/<int:pk>', views.download_file, name='download_file'),
    path('certificates/url/', views.URLFormView.as_view(), name='fetch_url'),
    path('certificates/<int:pk>/extensions', views.CertificateExtensionsTabView.as_view(), name='certificate_extensions'),
)