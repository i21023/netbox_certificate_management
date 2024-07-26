from netbox.views import generic
from netbox.views.generic.utils import get_prerequisite_model
from . import forms, models, tables, parser
from dcim.models import Device
from dcim.tables import DeviceTable
from utilities.views import ViewTab, register_model_view
from utilities.querydict import normalize_querydict
from utilities.forms import restrict_form_fields
from utilities.htmx import htmx_partial
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.functions import Cast, ExtractDay
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from datetime import datetime, timezone, timedelta
from .utils import return_days_valid



class CertificateView(generic.ObjectView):
    queryset = models.Certificate.objects.all()
    
    def get_extra_context(self, request, instance):
        print(instance)
        print(request)
        table = DeviceTable(instance.devices.all())
        table.configure(request)

        return {
            'related_devices': table
        }

class CertificateListView(generic.ObjectListView):
    queryset = models.Certificate.objects.annotate(
        valid_days_left=return_days_valid()
    )
    table = tables.CertificateTable


class CertificateEditView(generic.ObjectEditView):
    queryset = models.Certificate.objects.all()
    form = forms.CertificateForm

    def get_initial(self):
        initial = {}
        parsed_data=self.request.session.pop('parsed_certificate', None)
        print('parsed_data:', parsed_data)
        if(parsed_data):
            initial.update(parsed_data)
        return initial
    
    #this method is basically the same as in the ObjectEditView class, but it is overridden here to prepopulate the form with session data if a pem file is uploaded
    def get(self, request, *args, **kwargs):
        """
        GET request handler.

        Args:
            request: The current request
        """
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)
        model = self.queryset.model

        # this code is added to prepopulate the form with session data if a pem file is uploaded
        initial_data = self.get_initial()
        initial_data.update(normalize_querydict(request.GET))
        form = self.form(instance=obj, initial=initial_data)
        restrict_form_fields(form, request.user)

        # If this is an HTMX request, return only the rendered form HTML
        if htmx_partial(request):
            return render(request, self.htmx_template_name, {
                'form': form,
            })

        return render(request, self.template_name, {
            'model': model,
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            'prerequisite_model': get_prerequisite_model(self.queryset),
            **self.get_extra_context(request, obj),
        })

class CertificateDeleteView(generic.ObjectDeleteView):
    queryset = models.Certificate.objects.all()

@register_model_view(Device, name='certificates')
class DeviceCertificatesView(generic.ObjectChildrenView):
    queryset = Device.objects.all().prefetch_related('certificate_set')
    child_model=models.Certificate
    table=tables.CertificateTable
    template_name='netbox_certificate_management/device_certificates.html'
    hide_if_empty=True
    tab = ViewTab(
        label='Certificates',
        permission='dcim.view_device'
    )

    def get_children(self, request, parent):
        return parent.certificate_set.annotate(
            valid_days_left=return_days_valid()
        )

class CertificateUploadView(FormView):
    template_name = 'netbox_certificate_management/upload_certificate.html'
    form_class = forms.CertificateUploadForm
    success_url = reverse_lazy('plugins:netbox_certificate_management:certificate_list')  # Redirect after successful upload

    def form_valid(self, form):
        print('Certificate upload in progress...')
        pem_file = form.cleaned_data['file']
        pem_data = pem_file.read()
        
        try:
            parsed_data = parser.parse_certificate(pem_data)
            self.request.session['parsed_certificate'] = parsed_data           
            messages.success(self.request, 'Certificate uploaded and parsed successfully.')
            return redirect('plugins:netbox_certificate_management:certificate_add')
        except Exception as e:
            print(e)
            messages.error(self.request, f'Error parsing certificate: {e}')
            return super().form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with the file upload.')
        return super().form_invalid(form)
    
