"""Store URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.generators import OpenAPISchemaGenerator

from product.views import ProductView, ProductManagerView, ProductReceiptView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


class CustomerGeneratorSchema(OpenAPISchemaGenerator):
    def get_operation(self, *args, **kwargs):
        operation = super().get_operation(*args, **kwargs)
        your_header = openapi.Parameter(
        name='HTTP_AUTHORIZATION',
        description="Description",
        required=True,
        in_=openapi.IN_HEADER,
        type=openapi.TYPE_STRING,
        )
        operation.parameters.append(your_header)
        return operation


schema_view = get_schema_view(
   openapi.Info(
      title="jCircle API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="jimmy.lin@cyan.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   # generator_class=CustomerGeneratorSchema
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/products/<str:account>', ProductView.as_view()),
    path('v1/products/<str:pattern>/<str:browser>/<int:page>/<str:mode>/<str:keyword>/<str:account>', ProductView.as_view()),
    path('v1/managers/<str:account>', ProductManagerView.as_view()),
    path('v1/managers/<str:mid>/<str:account>', ProductManagerView.as_view()),
    path('v1/receipts/', ProductReceiptView.as_view()),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]



#生成媒體資源路由
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)