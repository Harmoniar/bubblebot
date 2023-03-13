import os
from django.shortcuts import redirect


modules = os.listdir(os.path.dirname(__file__))
modules.remove('__init__.py')
modules = [i.rstrip('.py') for i in modules if i.endswith('.py')]

for i in modules:
    exec(f"from .{i} import *")


def empty_url(request):
    return redirect("admin_home")
