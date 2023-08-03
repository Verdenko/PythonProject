import grpc
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
import resp_pb2, resp_pb2_grpc
from django.conf import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
import ProjectDataBase
from ProjectDataBase import IrenderWoodcatalog as woodcat

db_config = settings.DATABASES['default']
DATABASE_URL = f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"

# Создаем экземпляр движка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

# Создаем экземпляр сессии SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()


def get_wood_name(session):
    record = session.query(woodcat.id, woodcat.name).all()
    return record


@csrf_protect
def calculate(request):
    if request.method == 'POST':
        wood_id = int(request.POST['wood_id'])
        humidity_start = float(request.POST['humidity1'])
        humidity_end = float(request.POST['humidity2'])
        temperature = int(request.POST['temp'])
        method = 'POST'
    else:
        wood_id = None
        humidity_start = None
        humidity_end = None
        temperature = None
        method = 'GET'

        # Подключение к микросервису
    with grpc.insecure_channel(settings.GRPC_SERVER_ADDRESS) as channel:
        stub = resp_pb2_grpc.CalculationServiceStub(channel)

        # Создание запроса gRPC
        calculation_request = resp_pb2.CalculationRequest(wood_id=wood_id, humidity_start=humidity_start,
                                                          humidity_end=humidity_end, dryer_type=temperature,
                                                          method=method)

        # Выполнение запроса к микросервису
        response = stub.CalculateHeatConsumption(calculation_request)
        wood_name = get_wood_name(session)
        context = {
            'result': round(response.heat_value, 3),
            'error': response.error_message,
            'wood_name': wood_name
        }
        return render(request, 'main/index.html', context)


def index(request):
    wood_name = get_wood_name(session)
    return render(request, 'main/index.html', context={'wood_name': wood_name})
