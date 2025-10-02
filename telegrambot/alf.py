import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен вашего бота
import os
TOKEN = os.environ.get('BOT_TOKEN')

# Структура всех продуктов
CREDIT_PRODUCTS = {
    "credit_cash": {
        "name": "💰 Кредит наличными",
        "description": "Оформите кредит наличными на любые цели со ставкой от 19,9%. Для зарплатных клиентов сумма кредита до 7 500 000 ₽.",
        "url": "https://alfabank.ru/get-money/credit/credit-cash/welcome/?platformId=alfapartners_msv_PIL-PIL_567050_4921952&utm_source=alfapartners&utm_medium=msv&utm_term=PIL-PIL&utm_campaign=567050&utm_content=alfapartners_msv_PIL-PIL_567050_4921952"
    },
    "credit_card_60": {
        "name": "💳 Кредитная карта 60 дней без %",
        "description": "Бесплатное обслуживание и кэшбэк за все покупки.",
        "url": "https://alfabank.ru/get-money/credit-cards/land/60-days-partners/?platformId=alfapartners_msv_CC-60_567050_3469224&utm_source=alfapartners&utm_medium=msv&utm_term=CC-60&utm_campaign=567050&utm_content=alfapartners_msv_CC-60_567050_3469224"
    },
    "credit_big_plans": {
        "name": "🎯 Кредит на большие планы",
        "description": "Процентная ставка всегда меньше, чем по стандартному кредиту наличными.",
        "url": "https://alfa.me/Fns0ch?prefilledDataID=567050"
    },
    "credit_preapproved": {
        "name": "✅ Кредит наличными — предодобренное предложение",
        "description": "Предварительно одобренный кредит наличными, который можно получить в день оформления не выходя из дома.",
        "url": "https://alfa.me/0WwZ1h?url=https%3A%2F%2Fweb.alfabank.ru%2Fupsale-credits%2Fcredits%2FRP%3FisWebView%3Dtrue%26source%3Dalfapartners_msv%26referralId%3D567050&referralId=567050"
    },
    "mortgage": {
        "name": "🏠 Ипотека",
        "description": "Ипотечный кредит на покупку недвижимости",
        "url": "https://alfa.me/y-6Bns?url=https%3A%2F%2Fipoteka.alfabank.ru%2Fam%3Futm_source%3Dalfapartners%26utm_medium%3Dmsv%26platformId%3Dalfapartners_msv_mortgage_567050_0&platformId=alfapartners_msv_mortgage_567050_0"
    }
}

DEBIT_PRODUCTS = {
    "debit_cashback": {
        "name": "💎 Дебетовая Альфа-Карта с любимым кэшбэком",
        "description": "Дебетовая Альфа-Карта с любимым кэшбэком.",
        "url": "https://alfabank.ru/lp/retail/dc/flexible-agent/?platformId=alfapartners_msv_DC-flexible_567050_3469097&utm_source=alfapartners&utm_medium=msv&utm_term=DC-flexible&utm_campaign=567050be&utm_content=alfapartners_msv_DC-flexible_567050_3469097"
    },
    "acquiring": {
        "name": "💼 Торговый эквайринг",
        "description": "Бесплатная установка терминала для оплаты картой офлайн.",
        "url": "https://alfabank.ru/sme/payservice/msv-acq/?platformId=alfapartners_msv_acq_567050_3469346&utm_source=alfapartners&utm_medium=msv&utm_term=acq&utm_campaign=567050&utm_content=alfapartners_msv_acq_567050_3469346"
    },
    "child_card": {
        "name": "👶 Детская карта",
        "description": "Детская карта\nКарта, как у взрослого, для ребёнка от 6 до 14 лет",
        "url": "https://alfabank.ru/lp/retail/dc/childcard-agent/?platformId=alfapartners_msv_DC-childcard_567050_3469164&utm_source=alfapartners&utm_medium=msv&utm_term=DC-childcard&utm_campaign=567050&utm_content=alfapartners_msv_DC-childcard_567050_3469164"
    },
    "business_reg": {
        "name": "📋 Регистрация бизнеса",
        "description": "Удобный сервис для регистрации ИП и ООО",
        "url": "https://alfabank.ru/sme/start/partner/ag/?platformId=alfapartners_msv_RKOregbiz_567050_3469325&utm_source=alfapartners&utm_medium=msv&utm_term=RKOregbiz&utm_campaign=567050&utm_content=alfapartners_msv_RKOregbiz_567050_3469325"
    },
    "business_account": {
        "name": "🏢 Расчётный счёт для бизнеса",
        "description": "Выгодные тарифы под любые цели",
        "url": "https://alfabank.ru/sme/partner/ag/?platformId=alfapartners_msv_rko-anketa_567050_3469333&utm_source=alfapartners&utm_medium=msv&utm_term=rko-anketa&utm_campaign=567050&utm_content=alfapartners_msv_rko-anketa_567050_3469333"
    },
    "travel_card": {
        "name": "✈️ Дебетовая карта Alfa Travel",
        "description": "Дебетовая карта, которая копит на ваши путешествия",
        "url": "https://alfabank.ru/lp/retail/debit/promo/partner/travel/?platformId=alfapartners_msv_DC-travel_567050_4582633&utm_source=alfapartners&utm_medium=msv&utm_term=DC-travel&utm_campaign=567050&utm_content=alfapartners_msv_DC-travel_567050_4582633"
    }
}

INVESTMENT_PRODUCTS = {
    "broker_account": {
        "name": "📈 Брокерский счёт",
        "description": "Нужен для покупки и продажи акций, облигаций и фондов, а также для обмена валюты по выгодному курсу.",
        "url": "https://alfabank.ru/make-money/investments/brokerskij-schyot/?platformId=alfapartners_msv_investment-ba_567050_3469359&utm_source=alfapartners&utm_medium=msv&utm_term=investment-ba&utm_campaign=567050&utm_content=alfapartners_msv_investment-ba_567050_3469"
    }
}

INSURANCE_PRODUCTS = {
    "mortgage_insurance": {
        "name": "🏠 Страхование ипотеки",
        "description": "Страхование конструктива, жизни и здоровья, титула проверенными страховыми компаниями при ипотеке от любого банка",
        "url": "https://mortgage-svoy.insapp.ru/?platformId=alfapartners_msv_insurance-mortgage_567050_3469319&webMasterID=alfapartners_msv_insurance-mortgage_567050_3469319&utm_source=alfapartners&utm_medium=msv&utm_term=insurance-mortgage&utm_campaign=567050"
    },
    "kasko": {
        "name": "🚗 Страховой полис каско",
        "description": "Страховой полис каско",
        "url": "https://kasko-svoy.insapp.ru/?platformId=alfapartners_msv_insurance-kasko_567050_3469310&webMasterID=alfapartners_msv_insurance-kasko_567050_3469310&utm_source=alfapartners&utm_medium=msv&utm_term=insurance-kasko&utm_campaign=567050"
    },
    "osago": {
        "name": "🛡️ Страховой полис ОСАГО",
        "description": "Полис ОСАГО страхует ответственность водителя перед другими участниками дорожного движения в случае, если тот станет виновником ДТП, находясь за рулем машины.\n\nМини-каско\nОформить возможно только в момент оформления ОСАГО от СК «АльфаСтрахование», перед совершением оплаты полиса.\nЭто полис защиты водителей от непредвиденных ситуациях на дорогах. Его преимущества:\n- стоимость ниже, чем у каско;\n- не требует осмотра автомобиля при приобретении;\n- простое оформление.",
        "url": "https://osago-svoy.insapp.ru/?platformId=alfapartners_msv_insurance-osago_567050_3469300&webMasterID=alfapartners_msv_insurance-osago_567050_3469300&utm_source=alfapartners&utm_medium=msv&utm_term=insurance-osago&utm_campaign=567050"
    }
}

LIFE_SERVICES = {
    "mobile": {
        "name": "📱 Мобильный оператор Альфа-Мобайл",
        "description": "Мобильный оператор Альфа-Мобайл",
        "url": "https://alfa.me/SIM_alfapartners_msv?prefilledDataID=alfapartnersmsv_567050"
    },
    "credit_helper_optimal": {
        "name": "🎯 Кредитный помощник. Тариф Оптимальный",
        "description": "Кредитный помощник. Тариф Оптимальный",
        "url": "https://альфа-помощник3.космовиза.рф/?chanel=svoy_v_alfe&tariff_id=3&partner_id=567050"
    },
    "credit_helper_basic": {
        "name": "📊 Кредитный помощник. Тариф Базовый Плюс",
        "description": "Кредитный помощник. Тариф Базовый Плюс",
        "url": "https://альфа-помощник2.космовиза.рф/?chanel=svoy_v_alfe&tariff_id=2&partner_id=567050"
    },
    "lawyer_service": {
        "name": "⚖️ ЕЮС. Свой комфорт «Плюс Юрист»",
        "description": "ЕЮС. Свой комфорт «Плюс Юрист»",
        "url": "https://elsgroup.ru/svoy_v_alfe_6?tariff=6&partner_id=567050"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
        keyboard = [
            [InlineKeyboardButton("💳 Кредитные и дебетовые карты", callback_data="cards_menu")],
            [InlineKeyboardButton("📈 Инвестиционные решения", callback_data="investment_menu")],
            [InlineKeyboardButton("🛡️ Страховые решения", callback_data="insurance_menu")],
            [InlineKeyboardButton("🔧 Сервисы для жизни", callback_data="services_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "👋 Привет! Я Алекс, твой финансовый помощник от Альфа-Банка!\n\n"
            "Я здесь, чтобы помочь тебе уверенно управлять своими финансами. Со мной ты можешь подобрать для себя выгодные продукты:\n\n"
            "• Кредитные и дебетовые карты — с кэшбэком и бонусами.\n"
            "• Инвестиционные и страховые решения — для роста и защиты капитала.\n"
            "• Сервисы для жизни — которые упростят ежедневные платежи и переводы.\n\n"
            "🚀 Стань участником программы лояльности «Свой Альфа»!\n"
            "Получай еще больше выгоды, бонусы и привилегии за то, что пользуешься любимыми продуктами. Зарегистрируйся по ссылке ниже, чтобы открыть доступ к эксклюзивным предложениям:\n"
            "https://svoy.alfabank.ru/ref/567050 или пиши в телеграм @Grinch2star\n\n"
            "Используй меню команд для навигации. Я всегда на связи и готов оперативно помочь с выбором и ответить на твои вопросы!"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        logger.info(f"Пользователь {update.effective_user.id} запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

async def show_cards_menu(query) -> None:
    """Показать меню карт"""
    keyboard = [
        [InlineKeyboardButton("💳 Кредитные", callback_data="credit_cards")],
        [InlineKeyboardButton("💎 Дебетовые", callback_data="debit_cards")],
        [InlineKeyboardButton("◀️ Назад в главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "💳 Выберите тип карты:"
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def show_product_menu(query, products, menu_title, back_callback) -> None:
    """Показать меню продуктов"""
    keyboard = []
    for product_key, product in products.items():
        keyboard.append([InlineKeyboardButton(product["name"], callback_data=f"product_{product_key}")])
    
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=back_callback)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=menu_title, reply_markup=reply_markup)

async def show_main_menu(query) -> None:
    """Показать главное меню"""
    keyboard = [
        [InlineKeyboardButton("💳 Кредитные и дебетовые карты", callback_data="cards_menu")],
        [InlineKeyboardButton("📈 Инвестиционные решения", callback_data="investment_menu")],
        [InlineKeyboardButton("🛡️ Страховые решения", callback_data="insurance_menu")],
        [InlineKeyboardButton("🔧 Сервисы для жизни", callback_data="services_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👋 Привет! Я Алекс, твой финансовый помощник от Альфа-Банка!\n\n"
        "Я здесь, чтобы помочь тебе уверенно управлять своими финансами. Со мной ты можешь подобрать для себя выгодные продукты:\n\n"
        "• Кредитные и дебетовые карты — с кэшбэком и бонусами.\n"
        "• Инвестиционные и страховые решения — для роста и защиты капитала.\n"
        "• Сервисы для жизни — которые упростят ежедневные платежи и переводы.\n\n"
        "🚀 Стань участником программы лояльности «Свой Альфа»!\n"
        "Получай еще больше выгоды, бонусы и привилегии за то, что пользуешься любимыми продуктами. Зарегистрируйся по ссылке ниже, чтобы открыть доступ к эксклюзивным предложениям:\n"
        "https://svoy.alfabank.ru/ref/567050 или пиши в телеграм @Grinch2star\n\n"
        "Используй меню команд для навигации. Я всегда на связи и готов оперативно помочь с выбором и ответить на твои вопросы!"
    )
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)

def get_all_products():
    """Получить все продукты"""
    all_products = {}
    all_products.update(CREDIT_PRODUCTS)
    all_products.update(DEBIT_PRODUCTS)
    all_products.update(INVESTMENT_PRODUCTS)
    all_products.update(INSURANCE_PRODUCTS)
    all_products.update(LIFE_SERVICES)
    return all_products

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех callback-ов от inline кнопок"""
    query = update.callback_query
    
    try:
        await query.answer()
        
        if query.data == "main_menu":
            await show_main_menu(query)
            
        elif query.data == "cards_menu":
            await show_cards_menu(query)
            
        elif query.data == "credit_cards":
            await show_product_menu(query, CREDIT_PRODUCTS, "💳 Кредитные продукты:", "cards_menu")
            
        elif query.data == "debit_cards":
            await show_product_menu(query, DEBIT_PRODUCTS, "💎 Дебетовые продукты:", "cards_menu")
            
        elif query.data == "investment_menu":
            await show_product_menu(query, INVESTMENT_PRODUCTS, "📈 Инвестиционные решения:", "main_menu")
            
        elif query.data == "insurance_menu":
            await show_product_menu(query, INSURANCE_PRODUCTS, "🛡️ Страховые решения:", "main_menu")
            
        elif query.data == "services_menu":
            await show_product_menu(query, LIFE_SERVICES, "🔧 Сервисы для жизни:", "main_menu")
            
        elif query.data.startswith("product_"):
            product_key = query.data.replace("product_", "")
            all_products = get_all_products()
            
            if product_key in all_products:
                product = all_products[product_key]
                text = f"*{product['name']}*\n\n{product['description']}"
                
                # Определяем, откуда пришел пользователь для кнопки "Назад"
                back_callback = "main_menu"
                if product_key in CREDIT_PRODUCTS:
                    back_callback = "credit_cards"
                elif product_key in DEBIT_PRODUCTS:
                    back_callback = "debit_cards"
                elif product_key in INVESTMENT_PRODUCTS:
                    back_callback = "investment_menu"
                elif product_key in INSURANCE_PRODUCTS:
                    back_callback = "insurance_menu"
                elif product_key in LIFE_SERVICES:
                    back_callback = "services_menu"
                
                keyboard = [
                    [InlineKeyboardButton("🔗 Перейти", url=product['url'])],
                    [InlineKeyboardButton("◀️ Назад", callback_data=back_callback)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text("❌ Продукт не найден")
                
        logger.info(f"Обработан callback: {query.data} от пользователя {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка в button_callback: {e}")
        try:
            await query.edit_message_text("❌ Произошла ошибка. Попробуйте еще раз.")
        except:
            pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Произошла ошибка: {context.error}")

def main() -> None:
    """Основная функция запуска бота"""
    try:
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_callback))
        app.add_error_handler(error_handler)
        
        logger.info("🚀 Алекс готов помогать с финансами!")
        print("🚀 Алекс готов помогать с финансами!")
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        print(f"❌ Критическая ошибка при запуске бота: {e}")

if __name__ == "__main__":

    main()
