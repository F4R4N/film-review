from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

from rest_framework import permissions, routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
	openapi.Info(
		title="Film Review Api Documentation",
		default_version='v1',
		description="all you need to know about the film review api is in the following documentation please dont bother.",
		contact=openapi.Contact(email="farantgh@gmail.com"),
		license=openapi.License(name="BSD License"),
	),
	public=True,
	permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/auth/', include('customauth.urls')),
    path('v1/api/', include('api.urls')),
    path('v1/blog/', include('blog.urls')),
    path('v1/', include('contactus.urls')),
	path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema_swagger_ui')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
