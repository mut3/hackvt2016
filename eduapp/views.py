from util import json_response
from util import get_training
from util import get_model
from models import SchoolDistrict

def home_view(request):
    alldistricts = SchoolDistrict.getAll()

    #return json_response([d.__dict__ for d in alldistricts])

    x,y = get_training(alldistricts)

    return json_response(get_model(x,y))
