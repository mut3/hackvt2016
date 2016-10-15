from util import json_response
from util import get_training
from util import get_model
from util import x_value_factor
from models import SchoolDistrict
import json

alldistricts = SchoolDistrict.getAll()

#return json_response([d.__dict__ for d in alldistricts])

x,y = get_training(alldistricts)
model = get_model(x,y)


def home_view(request):
    result = {}

    for district in alldistricts:
        result[district.name] = district.getPerformanceMetric()

    return json_response(result)

def calculate_view(request, x):
    return json_response(model.calculate(float(x) * x_value_factor))

def batch_calculate_view(request):
    data = json.loads(request.read())

    response = {}

    for name, x in data.iteritems():
        response[name] = model.calculate(float(x) * x_value_factor)

    return json_response(response)
