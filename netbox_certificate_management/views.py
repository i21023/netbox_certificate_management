from netbox.views import generic
from . import forms, models, tables, parser
from dcim.models import Device
from utilities.views import ViewTab, register_model_view
from django.shortcuts import render, get_object_or_404
from django.db.models import F, ExpressionWrapper, fields
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from datetime import datetime, timezone 

class CertificateView(generic.ObjectView):
    queryset = models.Certificate.objects.all()

class CertificateListView(generic.ObjectListView):
    queryset = models.Certificate.objects.annotate(
        valid_days_left=ExpressionWrapper(
            F('not_valid_after') - datetime.now(timezone.utc),
            output_field=fields.DurationField()
        )
    )
    #template_name = 'generic/object_list.html'
    table = tables.CertificateTable

class CertificateEditView(generic.ObjectEditView):
    queryset = models.Certificate.objects.all()
    form = forms.CertificateForm

class CertificateDeleteView(generic.ObjectDeleteView):
    queryset = models.Certificate.objects.all()

@register_model_view(Device, name='certificates')
class DeviceCertificatesView(generic.ObjectChildrenView):
    queryset=Device.objects.all().prefetch_related('certificate_set')
    child_model=models.Certificate
    table=tables.CertificateTable
    template_name='netbox_certificate_management/device_certificates.html'
    hide_if_empty=True
    tab = ViewTab(
        label='Certificates',
        permission='dcim.view_device'
    )

    def get_children(self, request, parent):
        return parent.certificate_set.all()
    # def get(self, request, pk):
    #     device = get_object_or_404(Device, pk=pk)
    #     certificates = device.certificate_set.all()
    #     table = tables.CertificateTable(certificates)
    #     return render(request, 'netbox_certificate_management/device_certificates.html', {'table': table})

class CertificateUploadView(FormView):
    template_name = 'netbox_certificate_management/upload_certificate.html'
    form_class = forms.CertificateUploadForm
    success_url = reverse_lazy('plugins:netbox_certificate_management:certificate_list')  # Redirect after successful upload

    def form_valid(self, form):
        messages.info(self.request, 'Certificate upload in progress...')
        pem_file = form.cleaned_data['pem_file']
        pem_data = pem_file.read()
        
        try:
            parser.parse_certificate(pem_data)             

            messages.success(self.request, 'Certificate uploaded and parsed successfully.')
        except Exception as e:
            messages.error(self.request, f'Error parsing certificate: {e}')
            return super().form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with the file upload.')
        return super().form_invalid(form)
    
