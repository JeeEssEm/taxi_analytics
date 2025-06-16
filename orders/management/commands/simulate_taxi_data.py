from django.contrib.gis.geos import Point
import random
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction

from orders.models import TaxiOrder
from users.models import TaxiUser
from drivers.models import TaxiDriver
from cars.models import TaxiCar

from orders.utils import get_address_coords, get_order_summary
import string
import time

middlenames = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
    "Попов", "Васильев", "Павлов", "Семёнов", "Голубев"
]

firstnames = [
    "Александр", "Дмитрий", "Сергей", "Андрей", "Алексей",
    "Максим", "Иван", "Артём", "Кирилл", "Егор"
]

lastnames = [
    "Александрович", "Дмитриевич", "Сергеевич", "Андреевич", "Алексеевич",
    "Максимович", "Иванович", "Артёмович", "Кириллович", "Егорович"
]

coords = [
    [55.749676, 37.590022],  # Москва, ул. Арбат, дом 42
    [55.707357, 37.578466],  # Москва, Ленинский пр-т, дом 76
    # Москва, Бульварное кольцо, дом 12 (Чистопрудный бульвар)
    [55.761590, 37.609466],
    [55.760936, 37.649321],  # Москва, ул. Покровка, дом 31
    [55.716914, 37.793020],  # Москва, Рязанский пр-т, дом 18
    [55.748611, 37.588056],  # Москва, пер. Сивцев Вражек, дом 15
    [55.781247, 37.633502],  # Москва, пр-т Мира, дом 101
    [55.760833, 37.610833],  # Москва, ул. Большая Дмитровка, дом 7
    [55.758056, 37.608056],  # Москва, Б. Козловский пер., дом 6
    [55.758333, 37.638889],  # Москва, ул. Маросейка, дом 9
    [55.770833, 37.663056],  # Москва, 1-й Басманный пер., дом 5
    [55.752222, 37.589722],  # Москва, ул. Новый Арбат, дом 24
    [55.750833, 37.598611],  # Москва, Гоголевский бульвар, дом 11
    [55.743056, 37.597222],  # Москва, ул. Пречистенка, дом 30
    [55.766389, 37.631944],  # Москва, Сретенский бульвар, дом 8
    [55.760833, 37.605833],  # Москва, ул. Тверская, дом 17
    [55.765833, 37.608056],  # Москва, Страстной бульвар, дом 4
    [55.771944, 37.603611],  # Москва, 2-й Тверской-Ямской пер., дом 10
    [55.761389, 37.623611],  # Москва, ул. Кузнецкий Мост, дом 3
    [55.764722, 37.638889],  # Москва, Чистопрудный бульвар, дом 12
    [55.741111, 37.627222],  # Москва, ул. Пятницкая, дом 25
    [55.718611, 37.608056],  # Москва, Шаболовка ул., дом 14
    [55.670833, 37.506944],  # Москва, пр. Вернадского, дом 82
    [55.698611, 37.573056],  # Москва, ул. Вавилова, дом 7
    [55.703056, 37.530556],  # Москва, Ломоносовский пр-т, дом 27
    [55.643056, 37.527778],  # Москва, ул. Профсоюзная, дом 65
    [55.652222, 37.596944],  # Москва, Севастопольский пр-т, дом 28
    [55.662778, 37.605278],  # Москва, Нахимовский пр-т, дом 31
    [55.688611, 37.561944],  # Москва, ул. Кржижановского, дом 15
    [55.658333, 37.513889],  # Москва, ул. Обручева, дом 11
    [55.643889, 37.506944],  # Москва, ул. Академика Челомея, дом 3
    [55.673611, 37.554167],  # Москва, ул. Гарибальди, дом 6
    [55.681944, 37.573611],  # Москва, ул. Наметкина, дом 10
    [55.676389, 37.503611],  # Москва, ул. Удальцова, дом 71
    [55.683056, 37.491944]   # Москва, ул. Лобачевского, дом 92
]
emails = [
    "quantum2024@mail.ru",
    "neonbeam@yandex.ru",
    "steelfox@bk.ru",
    "phantom99@inbox.ru",
    "cosmicrush@list.ru",
    "lunarphase@rambler.ru",
    "novastorm@mail.ru",
    "irongate@yandex.ru",
    "digitalpulse@bk.ru",
    "stellarcore@inbox.ru",
    "voidlight@list.ru",
    "chaosmode@rambler.ru",
    "meteoroid@mail.ru",
    "radarscan@yandex.ru",
    "polaris88@bk.ru",
    "vortexx@inbox.ru",
    "orbit456@list.ru",
    "thunderzz@rambler.ru",
    "zenith777@mail.ru",
    "photonx@yandex.ru",
    "typhoon01@bk.ru",
    "rainbowx@inbox.ru",
    "satellite@list.ru",
    "laser42@rambler.ru",
    "volcano99@mail.ru",
    "tornadoX@yandex.ru",
    "comet1986@bk.ru",
    "echowave@inbox.ru",
    "cyclone404@list.ru",
    "gravityx@rambler.ru"
]

plates = [
    # Москва (коды 77, 97, 99, 177, 197, 199, 777, 797, 799)
    "А123БС777", "Х987ОР197", "Е555КТ199",
    "М321АХ77", "В666РС97", "О789УХ99",
    "С234КМ177", "Т543НЕ797", "У876ВС799",
    # Санкт-Петербург (78, 98, 178)
    "А234РС78", "Е321ТУ98", "К567ОХ178",
    # Московская область (50, 90, 150, 190, 750)
    "В123ТК50", "М555АУ90", "Н777СЕ150",
    "У345РА190", "Х901ОВ750",
    # Краснодарский край (23, 93, 123)
    "А567НС23", "О432РМ93", "С789АХ123",
    # Татарстан (16, 116, 716)
    "В234ЕК16", "Т678ОР116", "Х456УМ716",
    # Другие регионы
    "А890ВР02",  # Башкортостан (02)
    "Е123СН63",  # Самарская область (63)
    "М456ТК54",  # Новосибирская область (54)
    "О789РА66",  # Свердловская область (66)
    "С012УХ42"   # Кемеровская область (42)
]

colors = ['Red', 'White', 'Yellow', 'Black']

manufactureres = ['UAZ']

models = ['Bukhanka']

ONE_HOUR_SEC_DURATION = 5
START_DRIVERS = 10
START_USERS = 50


class Command(BaseCommand):
    def handle(self, *args, **options):
        for i in range(START_DRIVERS):
            self.register_random_user(True)
        for i in range(START_USERS):
            self.register_random_user(False)

        base_datetime = datetime.datetime.now(pytz.timezone('Europe/Moscow'))

        while(True):
            for count in range(2, random.randint(2, 4)):
                self.register_random_user(True)
            for count in range(5, random.randint(5, 10)):
                self.register_random_user(False)
            current_datetime = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            for count in range(10, random.randint(10, 100)):
                self.register_random_order(
                    random.choice([TaxiOrder.StatusChoices.DONE, TaxiOrder.StatusChoices.ON_THE_WAY, TaxiOrder.StatusChoices.PENDING]), current_datetime)
            self.stdout.write(f'{current_datetime}')
            time.sleep(5)

    def register_random_car(self):
        return TaxiCar.objects.create(
            plate_number=random.choice(plates),
            car_manufacture=random.choice(manufactureres),
            car_model=random.choice(models),
            car_color=random.choice(colors),
            year=1984
        )

    def register_random_driver(self):
        car = self.register_random_car()
        return TaxiDriver.objects.create(
            car=car,
            status=TaxiDriver.StatusChoices.WAITING
        )

    def register_random_user(self, is_driver=False):
        if is_driver:
            driver = self.register_random_driver()
        else:
            driver = None

        return TaxiUser.objects.create(
            email=f'{''.join(random.choice(string.ascii_lowercase) for i in range(10))}@rambler.ru',
            username=''.join(random.choice(string.ascii_lowercase)
                             for i in range(10)),
            first_name=random.choice(firstnames),
            middle_name=random.choice(middlenames),
            last_name=random.choice(lastnames),
            taxi=driver
        )

    def register_random_order(self, status: TaxiOrder.StatusChoices, pickup_datetime):
        flip_coin = random.randint(1, 3)

        user = random.choice(
            TaxiUser.objects.filter(taxi__isnull=True).all())
        driver = random.choice(TaxiDriver.objects.all())
        if status == TaxiOrder.StatusChoices.DONE or status == TaxiOrder.StatusChoices.PENDING:
            driver.status = TaxiDriver.StatusChoices.WAITING
        else:
            driver.status = TaxiDriver.StatusChoices.WORKING
        driver.save()
        pickup_coords = random.choice(coords)
        dropoff_coords = random.choice(
            [x for x in coords if x != pickup_coords])

        def coords_to_string(coords: list[2]):
            return f"{coords[0]},{coords[1]}"

        trip_distance_km = random.randint(1,20)
        expected_duration = random.randint(5,120)
        # order = get_order_summary(coords_to_string(
        #     pickup_coords), coords_to_string(dropoff_coords), 1)
        if flip_coin == 1:  # висящий заказ
            return TaxiOrder.objects.create(
                client=user,
                status="PENDING",
                pickup_datetime=pickup_datetime,
                pickup_coords=Point(pickup_coords, srid=4326),
                payment_type = random.randint(0,1),
                extra=0,
                total=random.randint(300,2000),
                passenger_count=1,
                trip_distance_km=trip_distance_km,
                expected_duration=expected_duration,
            )
        if flip_coin == 2:  # в работе
            return TaxiOrder.objects.create(
                client=user,
                driver=driver,
                car=driver.car,
                status=random.choice(["WAITING_FOR_DRIVER", "ON_THE_WAY"]),
                pickup_datetime=pickup_datetime,
                pickup_coords=Point(pickup_coords, srid=4326),
                payment_type = random.randint(0,1),
                extra=0,
                total=random.randint(300,2000),
                passenger_count=1,
                trip_distance_km=trip_distance_km,
                expected_duration=expected_duration,
            )
        if flip_coin == 3:  # завершен
            return TaxiOrder.objects.create(
                driver=driver,
                car=driver.car,
                client=user,
                status=random.choice(["DONE", "CANCELLED"]),
                pickup_datetime=pickup_datetime,
                pickup_coords=Point(pickup_coords, srid=4326),
                dropoff_datetime=pickup_datetime +
                datetime.timedelta(minutes=expected_duration),
                dropoff_coords=Point(dropoff_coords, srid=4326),
                payment_type = random.randint(0,1),
                extra=0,
                total=random.randint(300,2000),
                passenger_count=1,
                trip_distance_km=trip_distance_km,
                expected_duration=expected_duration,
            )
