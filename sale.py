# *****************************
# Bot for sale objects 
# *****************************

from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import config
from db import db, Users, Objects, AccessKeys, app
from aiogram.types import ParseMode
from aiogram.utils.markdown import link
import logging
import aiogram.utils.markdown as md
import datetime
from yandex import get_data
from bot import objectsForm, price_processing, main_keyboard, get_user_
from buy import bot as buy_bot

logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN_SALE)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(Text(equals=config.OBJECT_TEXT['main']['cancel_btn'], ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """CANCEL HANDLER"""
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['main']['cancel_ok'], reply_markup=main_keyboard)

# main keyboard
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(config.OBJECT_TEXT['main']['sale_btn'])


@dp.message_handler(lambda message: get_user_(message.chat.id) != None
                    and message.text not in [config.OBJECT_TEXT['main'][i] for i in config.OBJECT_TEXT['main']] and 
                    message.text not in [config.OBJECT_TEXT['notification'][i] for i in config.OBJECT_TEXT['notification']])
async def process_auth(message: types.Message):
    """USER AUTH"""

    await message.answer(config.OBJECT_TEXT['user']['login'], reply_markup=main_keyboard)


@dp.message_handler(lambda message: get_user_(message.chat.id) == None
                    and message.text not in [config.OBJECT_TEXT['main'][i] for i in config.OBJECT_TEXT['main']] and 
                    message.text not in [config.OBJECT_TEXT['notification'][i] for i in config.OBJECT_TEXT['notification']])
async def process_not_auth(message: types.Message):
    """USER NOT AUTH"""
    markup = types.ReplyKeyboardRemove()

    await bot.send_message(
        message.chat.id, config.OBJECT_TEXT['user']['not_login'],
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN,
    )



@dp.message_handler(Text(equals=config.OBJECT_TEXT['main']['sale_btn']))
async def function_sale(message: types.Message):
    """FUNCTION SALE (SALE STATE)"""

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(config.OBJECT_TEXT['main']['cancel_btn'])

    # start objects region state
    await objectsForm.region.set()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['start_add'], reply_markup=keyboard)
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_region'])


@dp.message_handler(lambda message: len(message.text) < 0, state=objectsForm.region)
async def process_region_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_region'])


@dp.message_handler(lambda message: len(message.text) > 0, state=objectsForm.region)
async def process_objects_region(message: types.Message, state: FSMContext):
    """OBJECTS REGION STATE"""

    async with state.proxy() as data:

        data['region'] = message.text

    # start objects city state
    await objectsForm.next()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_city'])


@dp.message_handler(lambda message: len(message.text) < 0, state=objectsForm.city)
async def process_city_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_city'])


@dp.message_handler(lambda message: len(message.text) > 0, state=objectsForm.city)
async def process_objects_city(message: types.Message, state: FSMContext):
    """OBJECTS CITY STATE"""

    async with state.proxy() as data:

        region_city = get_data(
            f"{data['region']}, {message.text}", 'region_city')
        data['city'] = region_city['city']
        data['region'] = region_city['region']

    # start objects address state
    await objectsForm.next()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_area'])


@dp.message_handler(lambda message: len(message.text) < 0, state=objectsForm.area)
async def process_area_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_area'])


@dp.message_handler(lambda message: len(message.text) > 0, state=objectsForm.area)
async def process_objects_area(message: types.Message, state: FSMContext):
    """OBJECTS AREA STATE"""

    async with state.proxy() as data:

        data['area'] = message.text

    # start objects area state
    await objectsForm.next()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_address'])


@dp.message_handler(lambda message: len(message.text) < 0, state=objectsForm.address)
async def process_address_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_address'])


property_type_keyboard = types.InlineKeyboardMarkup(
    resize_keyboard=True, selective=True)
property_type_btn_1 = types.InlineKeyboardButton('Вторичка', callback_data='property_type_btn_1')
property_type_btn_2 = types.InlineKeyboardButton('Новострой', callback_data='property_type_btn_2')
property_type_btn_3 = types.InlineKeyboardButton('Дом', callback_data='property_type_btn_3')
property_type_btn_4 = types.InlineKeyboardButton('Земля', callback_data='property_type_btn_4')
property_type_keyboard.add(property_type_btn_1, property_type_btn_2)
property_type_keyboard.add(property_type_btn_3, property_type_btn_4)



@dp.message_handler(lambda message: len(message.text) > 0, state=objectsForm.address)
async def process_objects_address(message: types.Message, state: FSMContext):
    """OBJECTS ADDRESS STATE"""

    async with state.proxy() as data:

        all_address_data = get_data(
            f"{data['region']}, {data['city']}, {data['area']} {message.text}", 'all_data')

        if all_address_data['street'] != None:
            if all_address_data['house'] != None:
                data['address'] = all_address_data['street'] + \
                    ', ' + all_address_data['house']
                data['street'] = all_address_data['street']
            else:
                try:
                    data['address'] = all_address_data['street'] + \
                        ', ' + message.text.split(' ')[-1]
                    data['street'] = all_address_data['street']
                except Exception as e:
                    data['address'] = all_address_data['street']
                    data['street'] = all_address_data['street']
        else:
            data['address'] = message.text
            data['street'] = message.text

        if all_address_data['area'] != None:
            data['area'] = all_address_data['area']

        if all_address_data['city'] != None:
            data['city'] = all_address_data['city']

        if all_address_data['region'] != None:
            data['region'] = all_address_data['region']

    # start objects street state
    await objectsForm.next()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_property_type'], reply_markup=property_type_keyboard)



@dp.callback_query_handler(Text(startswith="property_type_btn_"), state=objectsForm.property_type)
async def callbacks_property_type(call: types.CallbackQuery, state: FSMContext):
    """CALLBACK PROPERTY TYPE"""
    action = call.data.split('_')[-1]

    if action == "1":
        p_type = 'Вторичка'
    elif action == "2":
        p_type = 'Новострой'
    elif action == "3":
        p_type = 'Дом'
    elif action == "4":
        p_type = 'Земля'

    async with state.proxy() as data:
        data['property_type'] = p_type

    # start objects ownership type type state
    await objectsForm.next()

    await call.answer()

    await bot.send_message(call.message.chat.id, p_type)
    
    if action != '4':
        await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['objects']['enter_rooms'])
    else:
        await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['objects']['enter_no_rooms'])


@dp.message_handler(lambda message: not message.text.isdigit(), state=objectsForm.rooms)
async def process_rooms_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_rooms'])


@dp.message_handler(lambda message: message.text.isdigit(), state=objectsForm.rooms)
async def process_objects_rooms(message: types.Message, state: FSMContext):
    """OBJECTS ROOMS STATE"""

    
    async with state.proxy() as data:
        type_ = data['property_type']
        if type_ != 'Земля':
            data['rooms'] = message.text
        else:
            data['rooms'] = 0

    # start objects stage state
    await objectsForm.next()
    
    if type_ != 'Земля':
        await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_stage'])
    else:
        await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_no_stage'])


@dp.message_handler(lambda message: not message.text.isdigit(), state=objectsForm.stage)
async def process_stage_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_stage'])


@dp.message_handler(lambda message: message.text.isdigit(), state=objectsForm.stage)
async def process_objects_stage(message: types.Message, state: FSMContext):
    """OBJECTS STAGE STATE"""

    async with state.proxy() as data:
        if data['property_type'] != 'Земля':
            data['stage'] = message.text
        else:
            data['stage'] = 0

    # start objects description state
    await objectsForm.next()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_description'])


@dp.message_handler(state=objectsForm.description)
async def process_objects_description(message: types.Message, state: FSMContext):
    """OBJECTS DESCRIPTION STATE"""

    async with state.proxy() as data:
        data['description'] = message.text

    # start objects price state
    await objectsForm.next()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_price'])


@dp.message_handler(lambda message: not message.text.isdigit(), state=objectsForm.price)
async def process_price_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_price'])


@dp.message_handler(lambda message: message.text.isdigit(), state=objectsForm.price)
async def process_objects_price(message: types.Message, state: FSMContext):
    """OBJECTS PRICE STATE"""

    async with state.proxy() as data:
        data['price'] = message.text

    # start objects quadrature state
    await objectsForm.next()
    
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_quadrature'])


@dp.message_handler(lambda message: not message.text.replace(',', '.').replace('.', '').isdigit(), state=objectsForm.quadrature)
async def process_quadrature_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_quadrature'])


@dp.message_handler(lambda message: message.text.replace(',', '.').replace('.', '').isdigit(), state=objectsForm.quadrature)
async def process_objects_quadrature(message: types.Message, state: FSMContext):
    """OBJECTS QUADRATURE STATE"""

    async with state.proxy() as data:
        type_ = data['property_type']
        data['quadrature'] = message.text

    # start objects property type state
    await objectsForm.next()
    
    if type_ != 'Земля':
        await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_number_of_storeys'])
    else:
        await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['no_enter_number_of_storeys'])

    
@dp.message_handler(lambda message: not message.text.isdigit(), state=objectsForm.number_of_storeys)
async def process_number_of_storeys_invalid(message: types.Message):
    return await message.reply(config.OBJECT_TEXT['objects']['exc_price'])

@dp.message_handler(lambda message: message.text.isdigit(), state=objectsForm.number_of_storeys)
async def process_number_of_storeys(message: types.Message, state: FSMContext):
    """CALLBACK number_of_storeys"""

    async with state.proxy() as data:
        type_ = data['property_type']
        print(123)
        if type_ != 'Земля':
            data['number_of_storeys'] = message.text
        else:
            data['number_of_storeys'] = 0
        

    # start objects phone state
    await objectsForm.next()
    
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['objects']['enter_phone'])

@dp.message_handler(state=objectsForm.phone)
async def process_objects_phone(message: types.Message, state: FSMContext):
    """OBJECTS PHONE STATE AND SAVE STATE DATA IN DB OBJECTS"""

    async with state.proxy() as data:
        data['phone'] = message.text

        with app.app_context():
            # save Objects data in db
            object = Objects(
                user=str(message.chat.id),
                region=data['region'],
                city=data['city'],
                area=data['area'],
                address=data['address'],
                street=data['street'],
                rooms=data['rooms'],
                stage=data['stage'],
                description=data['description'],
                price=data['price'],
                quadrature=data['quadrature'],
                property_type=data['property_type'],
                number_of_storeys=data['number_of_storeys'],
                phone=data['phone'])

            db.session.add(object)
            db.session.commit()
        
        object_info = md.text(
                md.text('Регион: ', md.bold(data['region'])),
                md.text('Город: ', md.bold(data['city'])),
                md.text('Район: ', md.bold(data['area'])),
                md.text('Адрес: ', md.bold(data['address'])),
                # md.text('Улица: ', md.bold(data['street'])),
                md.text('Кол-во комнат: ', md.bold(data['rooms'])),
                md.text('Этаж: ', md.bold(data['stage'])),
                md.text('Описание: ', md.bold(data['description'])),
                md.text('Цена: ', price_processing(data['price']) + ' ₽'),
                md.text('Площадь: ', data['quadrature'] + ' м²'),
                md.text('Тип недвижимости: ', md.bold(data['property_type'])),
                md.text('Этажность: ', md.bold(
                    data['number_of_storeys'])),
                md.text('Телефон: ', (f"[{data['phone']}](tel:{data['phone']})")),
                sep='\n',)

        await bot.send_message(message.chat.id, md.text(config.OBJECT_TEXT['objects']['finish_add']))
        # send object data
        await bot.send_message(
            message.chat.id,
            object_info,
            reply_markup=main_keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )

    # finish state
    await state.finish()
    
    await notification_maling(message.chat.id, object_info, object)
    
def maling_filter(notification, obj):
    # user notification filter settings
    filter = notification['filter']
    user_area = filter['area']
    user_city = filter['city']
    user_price = filter['price']
    user_rooms = filter['rooms']
    user_region = filter['region']
    
    status = False
    
    if user_region == obj.region and user_city == "Не выбрано" and user_rooms == "Не выбрано" and user_area == "Не выбрано":
        status =  True
    elif user_region == obj.region and user_city == obj.city and user_rooms == "Не выбрано" and user_area == "Не выбрано":
        status = True
    elif user_region == obj.region and user_city == obj.city and user_rooms == "Не выбрано" and user_area == "Не выбрано":
        status = True
    elif user_region == obj.region and user_city == obj.city and user_rooms == obj.rooms and user_area == "Не выбрано":
        status = True
    elif user_region == obj.region and user_city == obj.city and user_rooms == obj.rooms and user_area == obj.area:
        status = True
    else:
        status = False
    
    if status is True:
        if user_price != "Не выбрано":
            if int(user_price['max']) >= int(obj.price) >= int(user_price['min']):
                status = True
            else:
                status = False

    return status
    
    
async def notification_maling(id, object_info, object):
    """MALING NOTIFICATION"""
    with app.app_context():
        users = Users.query.all()
    
    for user in users:
        notification_user = user.notification
        
        # send info about new object
        if int(user.id) != int(id):
            if notification_user['status'] == True:
                if notification_user['filter'] != None:
                    if maling_filter(notification_user, object) == True:
                        await buy_bot.send_message(user.id, f"{config.OBJECT_TEXT['notification']['new_object']}\n\n{object_info}", parse_mode=ParseMode.MARKDOWN)
                else:
                    await buy_bot.send_message(user.id, f"{config.OBJECT_TEXT['notification']['new_object']}\n\n{object_info}", parse_mode=ParseMode.MARKDOWN)
                    
                    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)