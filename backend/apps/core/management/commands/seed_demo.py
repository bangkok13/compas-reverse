from io import BytesIO
import math
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw
from apps.materials.models import Material
from apps.services.models import Service, FAQ
from apps.portfolio.models import Project, Category, ProjectImage
from apps.site_settings.models import SiteSettings
from apps.core.demo_geometry import gear_stl


def illustration(kind=0, before=False):
    """Original schematic illustrations, deliberately not presented as client photos."""
    image = Image.new("RGB", (1200, 900), "#dce2e8")
    draw = ImageDraw.Draw(image)
    for y in range(0, 900, 50):
        draw.line([(0, y), (1200, y)], fill="#d0d8e2")
    for x in range(0, 1200, 50):
        draw.line([(x, 0), (x, 900)], fill="#d0d8e2")
    if kind % 3 == 0:
        points = []
        for i in range(96):
            angle = i * math.pi / 48
            r = 285 if i % 4 in (1, 2) else 244
            points.append((600 + math.cos(angle) * r, 410 + math.sin(angle) * r * 0.67))
        draw.polygon([(x, y + 90) for x, y in points], fill="#192a3e")
        draw.polygon(points, fill="#3874c7" if not before else "#758496")
        draw.ellipse((480, 330, 720, 490), fill="#0f1e30", outline="#739dd9", width=6)
        draw.ellipse((512, 373, 688, 490), fill="#b6c4d5")
    elif kind % 3 == 1:
        draw.polygon([(310, 340), (720, 245), (920, 390), (510, 495)], fill="#6c89b0")
        draw.polygon([(310, 340), (510, 495), (510, 690), (310, 530)], fill="#2c405f")
        draw.polygon([(510, 495), (920, 390), (920, 580), (510, 690)], fill="#1e2c40")
        draw.polygon([(400, 350), (710, 280), (825, 375), (520, 452)], fill="#132238")
        for x in range(555, 840, 35):
            draw.line([(x, 535 - (x - 555) // 4), (x, 620 - (x - 555) // 4)], fill="#7490b8", width=8)
    else:
        for x, y in [(320, 340), (620, 460), (420, 600)]:
            draw.polygon([(x, y), (x+180, y-65), (x+280, y+10), (x+95, y+80)], fill="#407ed0")
            draw.polygon([(x+95, y+80), (x+280, y+10), (x+280, y+70), (x+95, y+140)], fill="#213c65")
            draw.polygon([(x, y), (x+95, y+80), (x+95, y+140), (x, y+60)], fill="#315785")
            draw.ellipse((x+100, y-10, x+170, y+35), fill="#162941")
    if before:
        draw.line([(520, 190), (560, 320), (490, 390), (625, 560), (570, 690)], fill="#dce2e8", width=20)
    output = BytesIO()
    image.save(output, "WEBP", quality=90)
    return output.getvalue()


class Command(BaseCommand):
    help = "Create explicitly marked demo content once; never overwrites existing content."

    def add_arguments(self, parser):
        parser.add_argument("--content-only", action="store_true", help="Create baseline catalog without demo projects.")

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["content_only"]:
            raise CommandError("Demo seeding is only allowed with DEBUG=true.")
        config, created = SiteSettings.objects.get_or_create(pk=1)
        if created:
            config.process = [
                {"title": "Расскажите о задаче", "text": "Пришлите фотографию, чертёж или 3D-модель. Можно начать со сломанной детали."},
                {"title": "Согласуем решение", "text": "Уточним нагрузки, размеры и условия работы. Подберём материал и способ изготовления."},
                {"title": "Создадим деталь", "text": "Восстановим геометрию, подготовим модель и изготовим согласованный вариант."},
                {"title": "Передадим результат", "text": "Проверим согласованные параметры. Вы получите деталь в мастерской или доставкой."},
            ]
            config.advantages = [
                {"title": "От образца до изделия", "text": "Сканирование, моделирование и печать в рамках одной задачи."},
                {"title": "Материал под условия", "text": "Учитываем температуру, нагрузки, контакт с влагой и солнечным светом."},
                {"title": "Понятное согласование", "text": "Обсуждаем геометрию, ограничения технологии и стоимость до изготовления."},
            ]
            config.business_text = "Прототипы, оснастка и небольшие серии для бизнеса. Пришлите техническое задание — обсудим объём, документы, сроки и порядок согласования образца."
            config.privacy_text = "ШАБЛОН ДЛЯ ЮРИДИЧЕСКОЙ ПРОВЕРКИ\n\nОператор: [полное наименование, адрес, реквизиты]. Контакт по вопросам обработки данных: [email].\n\nЦель: обработка обращения и подготовка предложения. Состав данных: имя, телефон, email, описание задачи и переданные файлы. Основание, сроки хранения, порядок отзыва согласия и удаления: [заполнить после юридической проверки].\n\nПервичное хранение: [указать оператора, страну и адрес инфраструктуры]. Получатели и обработчики: [перечислить]. Порядок реализации прав субъекта и меры защиты: [уточнить].\n\nНе публиковать без заполнения реквизитов и проверки применимых требований."
            config.consent_text = "ШАБЛОН ДЛЯ ЮРИДИЧЕСКОЙ ПРОВЕРКИ\n\nЯ даю [наименование оператора, адрес] согласие на обработку имени, телефона, email, описания задачи и приложенных файлов для ответа на обращение и расчёта стоимости.\n\nПеречень действий, способ обработки, получатели, срок действия и порядок отзыва: [заполнить]. Контакт для отзыва: [email].\n\nСогласие не распространяется на рекламные рассылки. Перед публикацией текст должен быть проверен и дополнен."
            config.save()
        materials = [
            ("PLA", "pla", "Для макетов и проверки формы.", "Концепт-модели, примерочные образцы.", "Жёсткость и удобство изготовления.", "Не подходит для нагретых и нагруженных узлов."),
            ("PETG", "petg", "Практичный материал для корпусов и функциональных прототипов.", "Корпуса, держатели, приспособления.", "Умеренная ударная стойкость и стойкость к влаге.", "Ползучесть под длительной нагрузкой; нужна проверка температуры."),
            ("ABS", "abs", "Инженерный пластик для корпусных деталей.", "Кожухи, корпуса, элементы салона.", "Возможность механической обработки.", "Чувствительность к УФ; усадка требует учёта в модели."),
            ("ASA", "asa", "Материал для изделий, работающих на открытом воздухе.", "Наружные корпуса и крепления.", "Стойкость к погодным условиям зависит от марки.", "Требует контроля усадки и режима печати."),
            ("PA6-CF", "pa6-cf", "Полиамид с углеродным наполнителем.", "Оснастка и жёсткие функциональные детали.", "Повышенная жёсткость по сравнению с ненаполненной базой.", "Гигроскопичность; свойства зависят от влажности и направления слоёв."),
            ("PA12-CF", "pa12-cf", "Наполненный полиамид для инженерных задач.", "Кронштейны, приспособления, прототипы.", "Стабильность размеров после правильной подготовки.", "Абразивность и зависимость прочности от ориентации печати."),
            ("PET-CF", "pet-cf", "PET с углеродным наполнителем.", "Оснастка, держатели и корпуса.", "Жёсткость и стабильность формы.", "Необходимы сушка и подбор режима обработки."),
            ("PA-GF", "pa-gf", "Полиамид со стеклянным наполнителем.", "Технические корпуса и крепления.", "Жёсткость и возможность изготовления сложной формы.", "Влагопоглощение и абразивность наполнителя."),
            ("PC", "pc", "Поликарбонат для требовательных прототипов.", "Кожухи и функциональные образцы.", "Потенциальная ударная стойкость при корректной печати.", "Чувствительность к условиям печати и некоторым химическим средам."),
        ]
        for order, row in enumerate(materials):
            name, slug, description, applications, advantages, limitations = row
            Material.objects.get_or_create(slug=slug, defaults=dict(
                name=name, description=description, applications=applications, advantages=advantages,
                limitations=limitations, sort_order=order,
                properties="Свойства зависят от марки, влажности, ориентации слоёв и режима печати. Численные параметры выбираются по паспорту конкретного материала. Для ответственных узлов необходимы испытания.",
            ))
        services = [
            ("3d-printing", "3D-печать", "Функциональные детали из инженерных пластиков — от одного экземпляра до небольшой серии.", "Печать по готовой модели с подбором материала, ориентации слоёв и параметров изготовления.", "Корпуса, кронштейны, оснастка, прототипы."),
            ("3d-scanning", "3D-сканирование", "Переносим геометрию физического объекта в цифровую модель.", "Оцифровываем доступные поверхности детали. До начала работы согласуем размеры объекта, требуемую детализацию и формат результата.", "Оцифровка образцов, контроль геометрии, подготовка к восстановлению."),
            ("reverse-engineering", "Реверс-инжиниринг", "Восстанавливаем геометрию по образцу, скану или сохранившимся фрагментам.", "Создаём CAD-модель и согласуем функциональные размеры. Если геометрия утрачена, уточняем сопряжения и условия эксплуатации.", "Детали без чертежей, адаптация изделий, восстановление посадок."),
            ("part-restoration", "Восстановление деталей", "Даём сломанному элементу новую форму и функцию.", "Изучаем причину поломки и возможность изготовления замены. Проверяем ограничения материала и согласуем конструкцию.", "Крепления, защёлки, крышки и элементы корпусов."),
            ("cad-modeling", "CAD-моделирование", "Разрабатываем деталь под вашу задачу и способ производства.", "От эскиза и технического задания до геометрии, пригодной для изготовления. Форматы и состав документации согласуются отдельно.", "Новые изделия, прототипы, адаптация готовых конструкций."),
            ("small-batch-production", "Малые серии", "Изготавливаем повторяющиеся детали после согласования образца.", "Готовим пробный экземпляр, согласуем параметры и организуем выпуск партии. Размер партии и сроки определяются по задаче.", "Оснастка, корпуса электроники, держатели, комплектующие."),
        ]
        for order, (slug, title, summary, description, applications) in enumerate(services):
            service, created = Service.objects.get_or_create(slug=slug, defaults=dict(
                title=title, summary=summary, description=description, applications=applications, sort_order=order,
                seo_title=f"{title} в Волгограде — 3D-мастерская",
                seo_description=summary + " Волгоград, Волжский и доставка по России.",
            ))
            if created:
                service.materials.set(Material.objects.filter(slug__in=["petg", "abs", "asa", "pa6-cf"]))
                FAQ.objects.create(service=service, question="Что нужно для расчёта стоимости?", answer="Пришлите модель, чертёж или фотографии, размеры и количество. Если готовой модели нет, опишите задачу — обсудим, как её подготовить.")
                FAQ.objects.create(service=service, question="Можно отправить образец из другого города?", answer="Да. Сначала обсудим задачу и согласуем способ передачи и возврата образца.")
        categories = [
            ("auto", "Автомобильные детали"), ("moto", "Мотоциклетные детали"),
            ("industrial", "Промышленное оборудование"), ("electronics", "Корпуса электроники"),
            ("restoration", "Восстановление элементов"), ("prototypes", "Прототипирование"),
            ("series", "Серийные изделия"), ("other", "Прочее"),
        ]
        for order, (slug, name) in enumerate(categories):
            Category.objects.get_or_create(slug=slug, defaults={"name": name, "sort_order": order})
        demos = [] if options["content_only"] else [
            ("demo-gear", "Шестерня механизма", "restoration", "pa6-cf"),
            ("demo-enclosure", "Корпус электронного модуля", "electronics", "petg"),
            ("demo-brackets", "Серия монтажных кронштейнов", "series", "asa"),
        ]
        for i, (slug, title, category, material) in enumerate(demos):
            if Project.objects.filter(slug=slug).exists():
                continue
            project = Project(
                slug=slug, title=title, category=Category.objects.get(slug=category),
                material=Material.objects.get(slug=material), technology="FDM / CAD",
                summary="Демонстрационный пример оформления проекта. Иллюстрация, не фотография выполненного заказа.",
                description="Этот проект показывает возможности портфолио. Все изображения — схемы для демонстрации интерфейса.",
                problem="Пример: исходная деталь повреждена, а готовая замена недоступна.",
                solution="Пример: исследовать образец, восстановить геометрию, согласовать материал и изготовить прототип.",
                result="Учебная иллюстрация процесса. Здесь владелец сможет описать результат реальной работы.",
                status=Project.Status.PUBLISHED, featured=True, is_demo=True, sort_order=i,
            )
            project.cover.save(f"demo-{i}.webp", ContentFile(illustration(i)), save=False)
            project.save()
            project.services.set(Service.objects.filter(slug__in=["3d-printing", "reverse-engineering"]))
            for before in [True, False]:
                photo = ProjectImage(project=project, caption="Демонстрационная схема: " + ("до" if before else "после"),
                                     role="before" if before else "after", sort_order=0 if before else 1)
                photo.image.save(f"demo-{i}-{'before' if before else 'after'}.webp", ContentFile(illustration(i, before)), save=True)
        for name, apps in [("Редактор контента", ["portfolio", "services", "materials", "site_settings"]),
                           ("Менеджер заявок", ["leads"])]:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                group.permissions.set(Permission.objects.filter(content_type__app_label__in=apps))
        for project in Project.objects.filter(is_demo=True, slug__in=[row[0] for row in demos]):
            if project.cover and not project.thumbnail:
                project.save()
            if project.slug == "demo-gear" and not project.model_file:
                project.model_file.save("demo-gear.stl", ContentFile(gear_stl()), save=False)
                project.viewer_enabled = True
                project.save()
            for image in project.images.filter(thumbnail=""):
                image.save()
        label = "Начальный каталог готов." if options["content_only"] else "Демонстрационные данные готовы."
        self.stdout.write(self.style.SUCCESS(label + " Существующий контент сохранён."))
