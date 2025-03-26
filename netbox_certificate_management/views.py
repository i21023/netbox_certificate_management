import json
from types import NoneType

from django.urls import reverse
from django.views.decorators.http import require_POST
from netbox.views import generic
from dcim.tables import DeviceTable
from rest_framework.reverse import reverse_lazy
from virtualization.tables import VirtualMachineTable
from openid.fetchers import fetch

from . import forms, models, tables
from .tables import CertificateTable
from .utils import return_days_valid
from django.http import HttpResponse, JsonResponse
from .parser import parse_certificate, convert_pem_to_der, fetch_https_certificate
from utilities.querydict import normalize_querydict
from utilities.forms import restrict_form_fields
from utilities.htmx import htmx_partial
from netbox.views.generic.utils import get_prerequisite_model
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db import transaction
import logging
from utilities.exceptions import AbortRequest, PermissionsViolation
from django.utils.safestring import mark_safe
from django.utils.html import escape
from utilities.querydict import normalize_querydict, prepare_cloned_fields
from core.signals import clear_events
import base64
from django.views.generic.edit import FormView
from dcim.models import Device
from virtualization.models import VirtualMachine
from utilities.views import register_model_view, ViewTab
from django.utils.translation import gettext_lazy as _
from . import filtersets
from .models import Certificate


class URLFormView(FormView):
    template_name = "netbox_certificate_management/url_form.html"
    form_class = forms.URLForm
    success_url = reverse_lazy("plugins:netbox_certificate_management:certificate_add")

    def form_valid(self, form):
        url = form.cleaned_data["url"]

        try:
            cert_data = fetch_https_certificate(url)
        except Exception as e:
            messages.error(self.request, str(e))
            return super().form_invalid(form)

        # parse the certificate
        try:
            parsed_cert_data, cert_b64 = parse_certificate(cert=cert_data)
        except Exception as e:
            return JsonResponse(
                {"error": f"Error parsing certificate: {e}"}, status=400
            )

        self.request.session["parsed_certificate"] = parsed_cert_data
        self.request.session["uploaded_file_binary"] = cert_b64

        return super().form_valid(form)

class CertificateBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Certificate.objects.prefetch_related('tags')
    filterset = filtersets.CertificateFilterSet
    table = tables.CertificateTable

class CertificateView(generic.ObjectView):
    queryset = models.Certificate.objects.all()
    template_name = "netbox_certificate_management/certificate.html"

    def get_extra_context(self, request, instance):
        device_table = DeviceTable(instance.devices.all())
        vm_table = VirtualMachineTable(instance.virtual_machines.all())
        children_table = CertificateTable(
            instance.certificates.annotate(valid_days_left=return_days_valid())
        )

        models.Certificate.objects.annotate(
            valid_days_left=return_days_valid()
        ).order_by("tree_id", "lft")

        children_table.configure(request)
        device_table.configure(request)
        vm_table.configure(request)

        return {
            "related_devices": device_table,
            "related_vms": vm_table,
            "children_certificates": children_table,
        }


class CertificateListView(generic.ObjectListView):
    queryset = models.Certificate.objects.annotate(
        valid_days_left=return_days_valid()
    ).order_by("tree_id", "lft")
    table = tables.CertificateTable
    template_name = "netbox_certificate_management/certificate_list.html"
    filterset = filtersets.CertificateFilterSet
    filterset_form = forms.CertificateFilterForm


class CertificateEditView(generic.ObjectEditView):
    queryset = models.Certificate.objects.all()
    form = forms.CertificateForm
    default_return_url = "plugins:netbox_certificate_management:certificate_list"
    template_name = "netbox_certificate_management/certificate_edit.html"

    def get(self, request, *args, **kwargs):
        """
        GET request handler.
        """
        obj = self.get_object(**kwargs)
        obj = self.alter_object(obj, request, args, kwargs)
        model = self.queryset.model

        try:
            passed_fields = request.session.pop("parsed_certificate")
            parent = models.Certificate.objects.filter(
                subject=passed_fields["issuer_name"]
            ).first()

            issuer_reference = None

            if parent:
                issuer_reference = parent if parent.pk != obj.pk else None

            if issuer_reference:
                passed_fields["issuer"] = issuer_reference
        except KeyError:
            passed_fields = None

        initial_data = {}
        if passed_fields:
            initial_data.update(passed_fields)
        elif not obj:
            return redirect("plugins:netbox_certificate_management:certificate_list")

        initial_data.update(normalize_querydict(request.GET))
        form = self.form(instance=obj, initial=initial_data)
        restrict_form_fields(form, request.user)
        if not obj:
            disable_pre_populated_fields(form, passed_fields)

        form.fields["subject"].widget.attrs["readonly"] = "disabled"

        if htmx_partial(request):
            return render(
                request,
                self.htmx_template_name,
                {
                    "form": form,
                },
            )

        return render(
            request,
            self.template_name,
            {
                "model": model,
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                "prerequisite_model": get_prerequisite_model(self.queryset),
                **self.get_extra_context(request, obj),
            },
        )

    def post(self, request, *args, **kwargs):
        """
        POST request handler.

        Args:
            request: The current request
        """
        logger = logging.getLogger("netbox.views.ObjectEditView")
        obj = self.get_object(**kwargs)

        # Take a snapshot for change logging (if editing an existing object)
        if obj.pk and hasattr(obj, "snapshot"):
            obj.snapshot()

        obj = self.alter_object(obj, request, args, kwargs)

        form = self.form(data=request.POST, files=request.FILES, instance=obj)
        restrict_form_fields(form, request.user)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                with transaction.atomic():
                    object_created = form.instance.pk is None
                    obj = form.save(commit=False)

                    file_base64 = request.session.pop("uploaded_file_binary", None)
                    if file_base64:
                        file_binary = base64.b64decode(file_base64)
                        obj.file = file_binary

                    if obj.issuer_name == obj.subject:
                        obj.is_root = True

                    obj.save()
                    form.save_m2m()

                    # Check that the new object conforms with any assigned object-level permissions
                    if not self.queryset.filter(pk=obj.pk).exists():
                        raise PermissionsViolation()

                    try:
                        # update certificates with the current objects as issuer
                        self.update_certificates_issuer(obj)
                    except Exception as e:
                        print(e)

                msg = "{} {}".format(
                    "Created" if object_created else "Modified",
                    self.queryset.model._meta.verbose_name,
                )
                logger.info(f"{msg} {obj} (PK: {obj.pk})")
                if hasattr(obj, "get_absolute_url"):
                    msg = mark_safe(
                        f'{msg} <a href="{obj.get_absolute_url()}">{escape(obj)}</a>'
                    )
                else:
                    msg = f"{msg} {obj}"
                messages.success(request, msg)

                if "_addanother" in request.POST:
                    redirect_url = request.path

                    # If cloning is supported, pre-populate a new instance of the form
                    params = prepare_cloned_fields(obj)
                    params.update(self.get_extra_addanother_params(request))
                    if params:
                        if "return_url" in request.GET:
                            params["return_url"] = request.GET.get("return_url")
                        redirect_url += f"?{params.urlencode()}"

                    return redirect(redirect_url)

                return_url = self.get_return_url(request, obj)

                return redirect(return_url)

            except (AbortRequest, PermissionsViolation) as e:
                logger.debug(e.message)
                form.add_error(None, e.message)
                clear_events.send(sender=self)

        else:
            logger.debug("Form validation failed")
            print(form.errors)

        return render(
            request,
            self.template_name,
            {
                "object": obj,
                "form": form,
                "return_url": self.get_return_url(request, obj),
                **self.get_extra_context(request, obj),
            },
        )

    def update_certificates_issuer(self, current_certificate) -> bool:
        """
        Update the issuer for certificates with the same subject as the current certificate
        that have no issuer set.

        Args:
            current_certificate: The current certificate object being saved
        """
        # Find certificates with the same subject and no issuer
        certificates_to_update = Certificate.objects.filter(
            issuer_name=current_certificate.subject,
            issuer__isnull=True,
        ).exclude(is_root=True)

        if certificates_to_update.exists():
            for certificate in certificates_to_update:
                certificate.issuer = current_certificate
                certificate.save()
            return True

        return False


def disable_pre_populated_fields(form, passed_fields):
    for field in passed_fields:
        form.fields[field].widget.attrs["readonly"] = True


class CertificateDeleteView(generic.ObjectDeleteView):
    queryset = models.Certificate.objects.all()


@require_POST
def upload_file(request):
    file = request.FILES.get("file")
    password = request.POST.get("password")

    pk_id = request.GET.get("pk_id")

    if not file:
        messages.error(request, "No file uploaded")
        return JsonResponse({"error": "No file uploaded"}, status=400)

    # the filename needs to be checked again here because there is no way to check if the password send by ajax was 'null' or null (not provided, i.e. no pkcs12 format)
    if not file.name.endswith(".p12") and not file.name.endswith(".pfx"):
        password = None

    # handle other cert file formats (pem, der)
    try:
        parsed_cert_data, cert_b64 = parse_certificate(
            cert=file.read(), password=password
        )
    except Exception as e:
        return JsonResponse({"error": f"Error parsing certificate: {e}"}, status=400)

    # Process the file and password as needed
    # Save file data to session or database, etc.
    request.session["parsed_certificate"] = parsed_cert_data
    request.session["uploaded_file_binary"] = cert_b64

    # upload new file
    if pk_id == "-1":
        redirect_url = reverse("plugins:netbox_certificate_management:certificate_add")
    else:  # update existing file
        element = models.Certificate.objects.get(pk=pk_id)
        if element.subject != parsed_cert_data.get(
            "subject"
        ) or element.issuer_name != parsed_cert_data.get("issuer_name"):
            return JsonResponse(
                {
                    "error": "The Subject of the uploaded Certificate does not match the current one"
                },
                status=400,
            )
        # if element.serial_number == parsed_cert_data.get('serial_number'):
        #    return JsonResponse({'error': 'The two certificates have the same serial number, no update needed'}, status=400)
        redirect_url = reverse(
            "plugins:netbox_certificate_management:certificate_edit", args=[pk_id]
        )

    return JsonResponse({"redirect": redirect_url})


def download_file(request, pk):
    # Get the object by primary key (or however you identify it)
    obj = get_object_or_404(models.Certificate, pk=pk)

    # Check if the user wants to convert the file to DER format
    convert_to_der = request.GET.get("convert_to_der", "False") == "True"

    # Ensure there is a file to download
    if obj.file:
        # if user wants to download in DER format, convert the file to DER
        if convert_to_der:
            response = HttpResponse(
                convert_pem_to_der(obj.file), content_type="application/x-x509-ca-cert"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{obj.subject}.der"'
            )
            return response
        response = HttpResponse(obj.file, content_type="application/x-pem-file")
        response["Content-Disposition"] = f'attachment; filename="{obj.subject}.pem"'
        return response
    else:
        return HttpResponse("No file found", status=404)


@register_model_view(Device, name="certificates")
class DeviceCertificatesView(generic.ObjectChildrenView):
    queryset = Device.objects.all().prefetch_related("certificates")
    child_model = models.Certificate
    table = tables.CertificateTable
    template_name = "netbox_certificate_management/certificates_tab.html"
    hide_if_empty = True
    tab = ViewTab(
        label=_("certificates"),
        badge=lambda obj: obj.certificates.count(),
        permission="dcim.view_device",
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.certificates.annotate(valid_days_left=return_days_valid())


@register_model_view(VirtualMachine, name="certificates")
class DeviceCertificatesView(generic.ObjectChildrenView):
    queryset = VirtualMachine.objects.all().prefetch_related("certificates")
    child_model = models.Certificate
    table = tables.CertificateTable
    template_name = "netbox_certificate_management/certificates_tab.html"
    hide_if_empty = True
    tab = ViewTab(
        label=_("certificates"),
        badge=lambda obj: obj.certificates.count(),
        permission="virtualization.view_virtualmachine",
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return parent.certificates.annotate(valid_days_left=return_days_valid())


@register_model_view(Certificate, name="extensions")
class CertificateExtensionsTabView(generic.ObjectView):
    queryset = models.Certificate.objects.all()
    template_name = "netbox_certificate_management/certificate_extensions.html"
    hide_if_empty = True
    tab = ViewTab(
        label="Extensions",
        hide_if_empty=True,
    )
