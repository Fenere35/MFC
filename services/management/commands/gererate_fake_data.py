import os
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from services.models import *

class Command(BaseCommand):
    help = 'Generate fake data for MFC project'

    def handle(self, *args, **options):
        self.stdout.write('Generating fake data...')

        # Очистка старых данных (осторожно!)
        # News.objects.all().delete()
        # Appointment.objects.all().delete()
        # Application.objects.all().delete()
        # OfficeService.objects.all().delete()
        # Employee.objects.all().delete()
        # Service.objects.all().delete()
        # ServiceCategory.objects.all().delete()
        # MFCOffice.objects.all().delete()
        # ApplicationStatus.objects.all().delete()

        # Создание статусов заявлений
        statuses = ['Подано', 'В работе', 'Выполнено', 'Отклонено']
        for status in statuses:
            ApplicationStatus.objects.get_or_create(name=status)

        # Создание категорий услуг
        categories_data = [
            'Паспортные услуги',
            'Налоговые услуги', 
            'Социальные услуги',
            'Регистрационные услуги',
            'Жилищно-коммунальные услуги'
        ]
        categories = []
        for cat_name in categories_data:
            cat, created = ServiceCategory.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'Описание категории {cat_name}'}
            )
            categories.append(cat)

        # Создание услуг
        services_data = [
            ('Замена паспорта в 20 лет', 'Паспортные услуги', '10 дней', 300),
            ('Замена паспорта в 45 лет', 'Паспортные услуги', '10 дней', 300),
            ('Выдача загранпаспорта', 'Паспортные услуги', '1 месяц', 2000),
            ('Регистрация брака', 'Регистрационные услуги', '1 день', 350),
            ('Регистрация рождения', 'Регистрационные услуги', '1 день', 0),
            ('Постановка на налоговый учет', 'Налоговые услуги', '5 дней', 0),
            ('Получение ИНН', 'Налоговые услуги', '5 дней', 0),
            ('Оформление пенсии', 'Социальные услуги', '30 дней', 0),
            ('Оформление детского пособия', 'Социальные услуги', '14 дней', 0),
            ('Оформление субсидии ЖКХ', 'Жилищно-коммунальные услуги', '21 день', 0),
        ]
        services = []
        for service_name, cat_name, term, cost in services_data:
            category = next(cat for cat in categories if cat.name == cat_name)
            service, created = Service.objects.get_or_create(
                name=service_name,
                defaults={
                    'category': category,
                    'description': f'Описание услуги {service_name}',
                    'execution_term': term,
                    'cost': cost
                }
            )
            services.append(service)

        # Создание офисов МФЦ
        offices_data = [
            ('МФЦ на Ленина', 'ул. Ленина, д. 1', '+74951234567', 'пн-пт 9:00-18:00'),
            ('МФЦ на Мира', 'ул. Мира, д. 15', '+74957654321', 'пн-пт 8:00-20:00, сб 10:00-15:00'),
            ('МФЦ Центральный', 'пл. Центральная, д. 5', '+74951122334', 'пн-чт 9:00-17:00, пт 9:00-16:00'),
            ('МФЦ Западный', 'ул. Западная, д. 25', '+74953344556', 'пн-пт 9:00-19:00'),
            ('МФЦ Восточный', 'пр. Восточный, д. 10', '+74954455667', 'пн-пт 8:00-20:00, сб 9:00-14:00'),
        ]
        offices = []
        for name, address, phone, schedule in offices_data:
            office, created = MFCOffice.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'phone': phone,
                    'work_schedule': schedule
                }
            )
            offices.append(office)

        # Создание сотрудников
        employees_data = [
            ('Иванов Иван Иванович', 'specialist'),
            ('Петров Петр Петрович', 'manager'),
            ('Сидорова Мария Сергеевна', 'consultant'),
            ('Кузнецов Алексей Владимирович', 'operator'),
            ('Смирнова Ольга Дмитриевна', 'specialist'),
            ('Васильев Дмитрий Николаевич', 'consultant'),
            ('Николаева Екатерина Андреевна', 'specialist'),
            ('Федоров Сергей Иванович', 'operator'),
            ('Александрова Анна Павловна', 'manager'),
            ('Дмитриев Максим Олегович', 'specialist'),
        ]
        employees = []
        for name, position in employees_data:
            office = random.choice(offices)
            employee, created = Employee.objects.get_or_create(
                full_name=name,
                defaults={
                    'office': office,
                    'position': position
                }
            )
            employees.append(employee)

        # Создание связей офисов и услуг (OfficeService)
        for office in offices:
            # Каждый офис предоставляет случайный набор услуг (от 3 до всех)
            office_services = random.sample(services, random.randint(3, len(services)))
            for service in office_services:
                OfficeService.objects.get_or_create(office=office, service=service)

        # Создание пользователей и профилей
        users_data = [
            ('user1', 'user1@example.com', '12345678901'),
            ('user2', 'user2@example.com', '12345678902'),
            ('user3', 'user3@example.com', '12345678903'),
            ('user4', 'user4@example.com', '12345678904'),
            ('user5', 'user5@example.com', '12345678905'),
        ]
        users = []
        for username, email, snils in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': username.capitalize(),
                    'last_name': 'Фамилия',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': '+7999' + str(random.randint(1000000, 9999999)),
                    'snils': snils,
                }
            )
            users.append(user)

        # Создание заявлений (Application)
        status_objs = list(ApplicationStatus.objects.all())
        for user in users:
            for _ in range(random.randint(1, 5)):
                service = random.choice(services)
                status = random.choice(status_objs)
                application, created = Application.objects.get_or_create(
                    user=user,
                    service=service,
                    status=status,
                    defaults={
                        'application_data': {'key': 'value'},
                        'created_at': timezone.now() - timezone.timedelta(days=random.randint(1, 30))
                    }
                )

        # Создание записей на прием (Appointment)
        for user in users:
            for _ in range(random.randint(1, 3)):
                office = random.choice(offices)
                service = random.choice(services)
                # Проверяем, что услуга доступна в выбранном офисе
                if OfficeService.objects.filter(office=office, service=service).exists():
                    date_time = timezone.now() + timezone.timedelta(days=random.randint(1, 30))
                    Appointment.objects.get_or_create(
                        user=user,
                        office=office,
                        service=service,
                        appointment_datetime=date_time,
                        defaults={
                            'status': random.choice(['active', 'completed', 'cancelled'])
                        }
                    )

        # Создание новостей
        news_titles = [
            'Открытие нового офиса МФЦ',
            'Введение новых услуг',
            'Изменение графика работы',
            'Проведение дня открытых дверей',
            'Внедрение электронной очереди',
            'Новые меры поддержки семей',
            'Упрощение процедуры регистрации',
            'Расширение перечня услуг',
            'Обновление оборудования',
            'Повышение качества обслуживания',
        ]
        for title in news_titles:
            News.objects.get_or_create(
                title=title,
                defaults={
                    'content': f'Содержание новости: {title}. Подробности будут позже.',
                    'author': random.choice(employees),
                    'published_at': timezone.now() - timezone.timedelta(days=random.randint(1, 100))
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data'))