from util import json_response
from util import get_training
from util import get_model
from util import x_value_factor
from models import SchoolDistrict

alldistricts = SchoolDistrict.getAll()

#return json_response([d.__dict__ for d in alldistricts])

x,y = get_training(alldistricts)
model = get_model(x,y)


def home_view(request):
    return json_response(model.calculate(20))

def calculate_view(request, x):
    return json_response(model.calculate(float(x) * x_value_factor))
