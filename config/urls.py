"""who_owns URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

from who_owns import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("filings/", views.FilingList.as_view()),
    path("filings/<int:pk>/", views.FilingDetail.as_view()),
    path("judges/", views.JudgeList.as_view()),
    path("companies/", views.get_company_by_name, name="get-company-by-name"), 
    path(
        "companies/<pk>/portfolio/",
        views.CompanyPortfolioDetail.as_view(),
        name="get-company-portfolio",
    ),
    path(
        "companies/<pk>/", views.CompanyDetail.as_view(), name="get-company-details"
    ),
    path("meta/<pk>/", views.MetaCorpDetail.as_view(), name="get-metacorp-detials"),
    path("meta/", views.MetaCorpList.as_view(), name="get-metacorp-detials"),
]
