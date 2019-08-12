__author__ = 'shiwei'
from django.conf.urls import *
import hufen.views

urlpatterns = [
    url(r"^$", hufen.views.hall),
    url(r"hall$", hufen.views.hall, name="hall"),

    url(r"list$", hufen.views.list, name="list"),
    url(r"listsuc$", hufen.views.suclist, name="suclist"),

    url(r"cancel$", hufen.views.cancel, name="cancel"),
    url(r"getsessionid$", hufen.views.getuser, name="getsessionid"),


]
