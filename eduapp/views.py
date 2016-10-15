from util import json_response
from models import SchoolDistrict

def home_view(request):
    alldistricts = SchoolDistrict.getAll()

    return json_response([d.__dict__ for d in alldistricts])
