from netbox.views import generic
from . import forms, models, tables
from dcim.models import Device
from utilities.views import ViewTab, register_model_view
from django.shortcuts import render, get_object_or_404

class CertificateView(generic.ObjectView):
    queryset = models.Certificate.objects.all()

class CertificateListView(generic.ObjectListView):
    queryset = models.Certificate.objects.all()
    table = tables.CertificateTable

class CertificateEditView(generic.ObjectEditView):
    queryset = models.Certificate.objects.all()
    form = forms.CertificateForm

class CertificateDeleteView(generic.ObjectDeleteView):
    queryset = models.Certificate.objects.all()

# @register_model_view(Device, name='certificates')
# class DeviceCertificatesView(generic.ObjectChildrenView):
#     queryset=Device.objects.all().prefetch_related('certificate_set')
#     child_model=models.Certificate
#     table=tables.CertificateTable
#     template_name='netbox_certificate_management/device_certificates.html'
#     hide_if_empty=True
#     tab = ViewTab(
#         label='Certificates',
#         permission='dcim.view_device'
#     )

#     def get_children(self, request, parent):
#         return parent.certificate_set.all()
    # def get(self, request, pk):
    #     device = get_object_or_404(Device, pk=pk)
    #     certificates = device.certificate_set.all()
    #     table = tables.CertificateTable(certificates)
    #     return render(request, 'netbox_certificate_management/device_certificates.html', {'table': table})
