import grpc
from concurrent import futures
import resp_pb2
import resp_pb2_grpc
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from django.conf import settings
import os
import django
from math import ceil, isfinite
from ProjectDataBase import IrenderWoodcatalog as woodcat, IrenderWoodparameter as wood, IrenderDryertype as dryer
import sys
from os.path import dirname, abspath
from datetime import datetime
d = dirname(dirname(abspath(__file__)))
sys.path.append(d)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renderissues.settings')
django.setup()

# функция определяющая текущий сезон
def check_date_range():
    # Получаем текущую дату
    current_date = datetime.now().date()
    # Получаем даты начала и конца диапазона
    start = datetime.strptime("15.04." + str(datetime.now().year), "%d.%m.%Y").date()
    end = datetime.strptime("15.10." + str(datetime.now().year), "%d.%m.%Y").date()
    # Проверяем, попадает ли текущая дата в диапазон
    if start <= current_date <= end:
        return 1
    else:
        return 2


db_config = settings.DATABASES['default']
DATABASE_URL = f"postgresql://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"

# Создаем экземпляр движка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

# Создаем экземпляр сессии SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()


class CalculationServiceServicer(resp_pb2_grpc.CalculationServiceServicer):
    # Расчет удельного расхода теплоты на основе входных значений
    def CalculateHeatConsumption(self, request, context):
        method = request.method
        response = resp_pb2.CalculationResponse()
        if method == 'GET':
            # Обработка GET запроса
            response.error_message = 'GET запросы не поддерживаются'
            return response
        # URL адрес БД
        # Порода древесины и её валидация
        if isinstance(request.wood_id, int):
            if session.query(woodcat).filter(woodcat.id == request.wood_id).one():
                if isfinite(request.wood_id):
                    wood_id = request.wood_id
        else:
            response.error_message = 'Такой породы древесины не существует, проверьте вводные данные'
            return response

        # Начальная и конечная влажности и их валидация
        if isinstance(request.humidity_end, float) and isinstance(request.humidity_start, float):
            if isfinite(request.humidity_end) and isfinite(request.humidity_start):
                humidity_end = round(request.humidity_end, 1)
                humidity_start = round(request.humidity_start, 1)
        else:

            response.error_message = 'Введите правильное значение влажности'
            return response

        # разница влажности и её валидация
        if humidity_start > humidity_end:
            humidity_difference = humidity_start - humidity_end
        else:
            response.error_message = 'Начальная влажность должна быть больше конечной'
            return response

        # Тип сушилки и её валидация
        if isinstance(request.dryer_type, int):
            if session.query(dryer).filter(dryer.id == request.dryer_type).one():
                if isfinite(request.dryer_type):
                    dryer_type = request.dryer_type
        else:
            response.error_message = 'Неправильный тип сушильной установки'
            return response

        # Округление разницы влажности для работы с БД
        humidity_difference_round = ceil(humidity_difference / 10) * 10

        # Уменьшение разницы влажностей при достижении 100
        if humidity_difference_round == 100:
            humidity_difference_round = 90

        # Получаем плотность и тип сухого материала через запрос к БД
        record = session.query(woodcat).filter(woodcat.id == wood_id).one()

        # тип сухого материала(древесины)
        wood_type = record.wood_type_id

        # определение отопительного сезона
        time_period = check_date_range()

        # Запрос на получение удельного расхода теплоты на испарение 1 кг влаги
        record2 = session.query(wood).filter(
            and_(wood.temp_dif == humidity_difference_round, wood.period_id == time_period,
                 wood.wood_type_id == wood_type,
                 wood.dryer_id == dryer_type)).one()
        # Плотность сухого материала
        wood_density = record.density

        # удельный расход теплоты на испарение 1 кг влаги
        heat_consumption = record2.heat_value

        # масса влаги, испаряемая за время сушки из 1 м3 материала, кг/м3
        moisture_mass = 0.01 * wood_density * humidity_difference

        # Удельный расход теплоты, нормируемый на 1 м3 высушиваемой древесины
        heat_value = moisture_mass * heat_consumption * pow(10, -6)
        response.heat_value = float(heat_value)
        return response


# Включение микросервиса и открытие 50051 порта на прослушку
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    resp_pb2_grpc.add_CalculationServiceServicer_to_server(CalculationServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
