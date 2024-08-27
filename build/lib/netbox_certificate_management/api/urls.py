from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()
router.register('certificates', views.CertificateViewSet)

urlpatterns = router.urls