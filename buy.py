# *****************************
# bot. View all objects and notification settings
# *****************************

from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import config
from db import db, Users, Objects, AccessKeys, app, Images
from aiogram.types import ParseMode
from aiogram.utils.markdown import link
import logging
import aiogram.utils.markdown as md
import datetime
from yandex import get_data
from bot import render_all_objects, UserData, Notification, get_user_

OBJECTS = {}
FILTER = {}
USER = {}
UPDATE = {}
SWITCH = {}
NOTIFICATION = {}

logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=config.TOKEN_BUY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



# CHECK AUTH USER

# main keyboard
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(config.OBJECT_TEXT['main']['feed_btn'], config.OBJECT_TEXT['main']['notification_btn'])


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


@dp.message_handler(Text(equals=config.OBJECT_TEXT['main']['back_btn'], ignore_case=True), state='*')
async def back_handler(message: types.Message,  state: FSMContext):
    """BACK HANDLER"""

    await bot.send_message(message.chat.id, config.OBJECT_TEXT['main']['back_ok'], reply_markup=main_keyboard)

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()


@dp.message_handler(Text(equals=config.OBJECT_TEXT['main']['feed_btn']))
async def function_feed(message: types.Message):
    """FUNCTION FEED"""

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(config.OBJECT_TEXT['main']['back_btn'])

    await bot.send_message(message.chat.id, config.OBJECT_TEXT['feed']['feed'], reply_markup=keyboard)

    # filter switch
    filter_keyboard = types.InlineKeyboardMarkup(
        resize_keyboard=True, selective=True)

    filter_keyboard.add(*[
        types.InlineKeyboardButton(
            f'✅ Да', callback_data=f'filter_switch_yes'),
        types.InlineKeyboardButton(
            f'❌ Нет', callback_data=f'filter_switch_no')
    ])

    await bot.send_message(message.chat.id, config.OBJECT_TEXT['feed']['switch_filter'], reply_markup=filter_keyboard)

    OBJECTS[message.chat.id] = {}

# ------------------ FILTER AND NOTIFICATION FILTER----------------------

def get_result_objects(id):
    
    filter_region = FILTER[id]['region']
    filter_city = FILTER[id]['city']
    filter_area = FILTER[id]['area']
    filter_price = FILTER[id]['price']
    filter_rooms = FILTER[id]['rooms']
    filter_advertising = FILTER[id]['advertising']
    print(filter_advertising)

    res_objects = []

    # true true true true
    if filter_area != 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising != 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, rooms=filter_rooms, city=filter_city, advertising=filter_advertising).all()
    # ----

    # true false false false
    elif filter_area != 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area).all()

    # false true false false
    elif filter_area == 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, rooms=filter_rooms).all()

    # false false true false
    elif filter_area == 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, city=filter_city).all()
    
    # false false false true
    elif filter_area == 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising != 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, advertising=filter_advertising).all()

    # ----
    
    # true true false false
    elif filter_area != 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, rooms=filter_rooms).all()

    # false false true true
    elif filter_area == 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising != 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, city=filter_city, advertising=filter_advertising).all()

    # true false false true
    elif filter_area != 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising != 'Не выбрано':
        print(12)
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, advertising='Да').all()
    
    # true false true false
    elif filter_area != 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, city=filter_city).all()
    
    # false true false true
    elif filter_area == 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising != 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, rooms=filter_rooms, advertising=filter_advertising).all()
        
    
    # false true true false
    elif filter_area == 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, rooms=filter_rooms, city=filter_city).all()
            
     # ----
    
    # true true true false
    elif filter_area != 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, rooms=filter_rooms, city=filter_city).all()

    # false true true true
    elif filter_area == 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising != 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, rooms=filter_rooms, city=filter_city, advertising=filter_advertising).all()

    # true false true true
    elif filter_area == 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city != 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, city=filter_city, advertising=filter_advertising).all()
    
    #  true true false true
    elif filter_area != 'Не выбрано' and filter_rooms != 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising != 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(
                region=filter_region, area=filter_area, rooms=filter_rooms, advertising=filter_advertising).all()

    # ----
    
    # false false false false
    elif filter_area == 'Не выбрано' and filter_rooms == 'Не выбрано' and filter_city == 'Не выбрано' and filter_advertising == 'Не выбрано':
        with app.app_context():
            objects = Objects.query.filter_by(region=filter_region).all()

    if filter_price != 'Не выбрано':
        for i in objects:
            if int(filter_price['max']) >= int(i.price) >= int(filter_price['min']):
                res_objects.append(i)
    else:
        res_objects = objects
        
    print(res_objects)

    return res_objects




@dp.callback_query_handler(Text(startswith="img_"))
async def callback_extend_img(call: types.CallbackQuery):
    """CALLBACK EXTEND img"""
    print(call.data)
    id = call.data.split('_')[-1]
    print(id)
    
    with app.app_context():
        images = Images.query.filter_by(object=id).all()

        if len(images) != 0:
            if len(images) > 1:
                media = types.MediaGroup()

                for i in images:
                    print(i.image_path)
                    media.attach_photo(types.InputFile(i.image_path))

                await bot.send_media_group(call.message.chat.id, media=media)

            else:
                photo = types.InputFile(images[0].image_path)
                await bot.send_photo(call.message.chat.id, photo)
        else:
            await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['objects']['images_not'])

    




async def render_item(id, item):
    """RENDER FILTER ITEM"""
    if 'current_item' in FILTER[id]:
        try:
            await FILTER[id]['current_item'].delete()
        except Exception as e:
            print(e)

    keyboard_items = types.InlineKeyboardMarkup(
        resize_keyboard=True, selective=True, row_width=1)

    # get all objects
    with app.app_context():
        objects = Objects.query.all()
        
    all_city = set([i.city for i in objects if i.city != None])
    all_areas_filter_by_city = set(
        [i.area for i in objects if i.city == FILTER[id]['city']])
    all_objects_rooms_filter_by_city = set(
        [i.rooms for i in objects if i.city == FILTER[id]['city']])

    all_region = set([i.region for i in objects])

    buttons = []

    # all refion
    if item == 'region':
        for i in all_region:
            buttons.append(types.InlineKeyboardButton(
                f'{i}', callback_data=f'filter_region_{i}'))

        keyboard_items.add(*buttons)

        msg = await bot.send_message(id, config.OBJECT_TEXT['feed']['region_btn'], reply_markup=keyboard_items)

    # all cities
    if item == 'city':
        for i in all_city:
            print(i)
            buttons.append(types.InlineKeyboardButton(
                f'{i}', callback_data=f'filter_city_{i}'))

        keyboard_items.add(*buttons)

        msg = await bot.send_message(id, config.OBJECT_TEXT['feed']['city_btn'], reply_markup=keyboard_items)

    # all areas by current city
    elif item == 'area':

        for i in all_areas_filter_by_city:
            buttons.append(types.InlineKeyboardButton(
                f'{i}', callback_data=f'filter_area_{i}'))

        keyboard_items.add(*buttons)

        msg = await bot.send_message(id, config.OBJECT_TEXT['feed']['area_btn'], reply_markup=keyboard_items)
        
    # all advertising by current city
    elif item == 'advertising':

        buttons = [types.InlineKeyboardButton(f'Да', callback_data=f'filter_advertising_Да'), 
                           types.InlineKeyboardButton(f'Нет', callback_data=f'filter_advertising_Нет')]

        keyboard_items.add(*buttons)

        msg = await bot.send_message(id, config.OBJECT_TEXT['feed']['advertising_btn'], reply_markup=keyboard_items)

    elif item == 'rooms':

        for i in all_objects_rooms_filter_by_city:
            buttons.append(types.InlineKeyboardButton(
                f'{i}', callback_data=f'filter_rooms_{i}'))

        keyboard_items.add(*buttons)

        msg = await bot.send_message(id, config.OBJECT_TEXT['feed']['rooms_btn'], reply_markup=keyboard_items)

    elif item == 'price':

        msg = await bot.send_message(id, config.OBJECT_TEXT['feed']['enter_current_price'])

        await UserData.current_price.set()

        # data to delete
        FILTER[id]['trash'] = [msg]

    FILTER[id]['current_item'] = msg

@dp.message_handler(lambda message: '-' not in message.text, state=UserData.current_price)
async def process_current_filter_price_invalid(message: types.Message):

    item = await message.reply(config.OBJECT_TEXT['feed']['exc_current_price'])

    # add in trash
    FILTER[message.chat.id]['trash'].append(item)
    FILTER[message.chat.id]['trash'].append(message)

    return item


@dp.message_handler(lambda message: '-' in message.text, state=UserData.current_price)
async def process_current_filter_price(message: types.Message, state: FSMContext):
    """CURRENT FILTER PRICE PROCESS"""

    # add in trash
    FILTER[message.chat.id]['trash'].append(message)

    async with state.proxy() as data:
        try:
            data['current_price'] = message.text.strip().replace(' ', '')
            FILTER[message.chat.id]['price'] = {'text': message.text.strip().replace(' ', ''),
                                        'min': data['current_price'].split('-')[0],
                                        'max': data['current_price'].split('-')[1]}
        except Exception as e:
            print(e)

    try:
        # clear trash
        for i in FILTER[message.chat.id]['trash']:
            await i.delete()
    except Exception as e:
        print(e)

    try:
        # delete current filter menu
        await FILTER[message.chat.id]['filter_menu'].delete()
    except Exception as e:
        print(e)

    filter_menu = await bot.send_message(message.chat.id, config.OBJECT_TEXT['feed']['filter'], reply_markup=render_filter_button(message.chat.id))
    FILTER[message.chat.id]['filter_menu'] = filter_menu

    # finish state
    await state.finish()


async def set_item_filter_notification(id, item):
    """ENTER VALUE FOR NOTIFICATION FILTER"""
    msg = await bot.send_message(id, config.OBJECT_TEXT['notification']['enter_value'])
    
    NOTIFICATION[id]['current_filter_item'] = item
    NOTIFICATION[id]['current_filter_msg'] = msg
    await Notification.data.set()
    

@dp.message_handler(lambda message: len(message.text) > 0, state=Notification.data)
async def process_value_notification(message: types.Message, state: FSMContext):
    """VALUE FOR NOTIFICATION PROCESS"""

    async with state.proxy() as data:
        item = NOTIFICATION[message.chat.id]['current_filter_item']
        
        if item == 'city':
            valid_data = get_data(f'{FILTER[message.chat.id]["region"]}, {message.text}', 'region_city')
            FILTER[message.chat.id][item] = valid_data['city']
        else:
            FILTER[message.chat.id][item] = message.text
            
        NOTIFICATION[message.chat.id]['user_msg'] = message

    # finish state
    await state.finish()
    
    # delete trash
    await NOTIFICATION[message.chat.id]['user_msg'].delete()
    await NOTIFICATION[message.chat.id]['current_filter_msg'].delete()
    
    try:
        # delete old filter menu
        await FILTER[message.chat.id]['filter_menu'].delete()
    except Exception as e:
        print(e)
        
    filter_menu = await bot.send_message(message.chat.id, config.OBJECT_TEXT['feed']['filter'], reply_markup=render_filter_button(message.chat.id))
    
    FILTER[message.chat.id]['filter_menu'] = filter_menu    
    

@dp.callback_query_handler(Text(startswith="filter_"))
async def callback_filter(call: types.CallbackQuery):
    """CALLBACK FILTER"""

    action = call.data.split('_')[-1]
    func_action = call.data.split('_')[-2]

    try:
        await OBJECTS[call.message.chat.id]['current_object'].delete()
    except Exception as e:
        pass

    try:
        for i in FILTER[call.message.chat.id]['objects']:
            await i.delete()
    except Exception as e:
            print(e)
            
    contact_keybord = types.InlineKeyboardMarkup(
    resize_keyboard=True, selective=True)

    # switch yes/no
    if func_action == 'switch':
        if action == 'yes':
            # toggle filter application
            SWITCH[call.message.chat.id] = {'current': 'objects'}
            
            filter_menu = await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['feed']['filter'], reply_markup=render_filter_button(call.message.chat.id))
            FILTER[call.message.chat.id]['filter_menu'] = filter_menu
            
        elif action == 'no':
            # get objects without filter
            with app.app_context():
                user = Users.query.filter_by(id=call.message.chat.id).first()
                object = Objects.query.filter_by(region=user.region).all()
                
                for i in render_all_objects(object):
                    await bot.send_message(call.message.chat.id, i[0], parse_mode=ParseMode.MARKDOWN, reply_markup=i[2])

    # filter items
    elif func_action == 'item':
    
        if action == 'region':
            
            await render_item(call.message.chat.id, 'region')
            
        elif action == 'city':
            
            # FEED MODE
            if SWITCH[call.message.chat.id]['current'] == 'objects':
                await render_item(call.message.chat.id, 'city')
            else:
                await set_item_filter_notification(call.message.chat.id, 'city')
            
            
        elif action == 'area':
            
            # FEED MODE
            if SWITCH[call.message.chat.id]['current'] == 'objects':
                await render_item(call.message.chat.id, 'area')
            else:
                await set_item_filter_notification(call.message.chat.id, 'area')
            
        elif action == 'rooms':
            
            # FEED MODE
            if SWITCH[call.message.chat.id]['current'] == 'objects':
                await render_item(call.message.chat.id, 'rooms')
            else:
                await set_item_filter_notification(call.message.chat.id, 'rooms')
                
        elif action == 'advertising':
            
            # FEED MODE
            if SWITCH[call.message.chat.id]['current'] == 'objects':
                await render_item(call.message.chat.id, 'advertising')
            else:
                await set_item_filter_notification(call.message.chat.id, 'advertising')
                
        elif action == 'price':
            await render_item(call.message.chat.id, 'price')
            
        elif action == 'ok':
           
            res_objects = get_result_objects(call.message.chat.id)
            if len(res_objects) > 0:
                # render objects 
                # objects_btn = await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['feed']['objects_with_filter'], reply_markup=render_all_feed(res_objects))
                FILTER[call.message.chat.id]['objects'] = []
                for i in render_all_objects(res_objects):
                    msg = await bot.send_message(call.message.chat.id, i[0], parse_mode=ParseMode.MARKDOWN, reply_markup=i[2])
                    
                    FILTER[call.message.chat.id]['objects'].append(msg)
            else:
                objects_btn = await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['feed']['no_objects'])
                FILTER[call.message.chat.id]['objects_btn'] = objects_btn
                
        # clear filter
        elif action == 'clear':
            FILTER[call.message.chat.id]['region'] = 'Не выбрано'
            FILTER[call.message.chat.id]['area'] = 'Не выбрано'
            FILTER[call.message.chat.id]['rooms'] = 'Не выбрано' 
            FILTER[call.message.chat.id]['price'] = 'Не выбрано'
            FILTER[call.message.chat.id]['advertising'] = 'Не выбрано'
            FILTER[call.message.chat.id]['city'] = 'Не выбрано' 
            
            try:
                # delete old filter menu
                await FILTER[call.message.chat.id]['filter_menu'].delete()
            except Exception as e:
                print(e)
            
            try:
                for i in FILTER[call.message.chat.id]['objects']:
                    await i.delete()
            except Exception as e:
                print(e)
            
            try:
                # delete buttons
                await FILTER[call.message.chat.id]['current_item'].delete()
            except Exception as e:
                print(e)
                
            
                
            filter_menu = await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['feed']['filter'], reply_markup=render_filter_button(call.message.chat.id))
            
            FILTER[call.message.chat.id]['filter_menu'] = filter_menu
            
    # notification filter OK
    elif func_action == 'notification':
        with app.app_context():
            user = Users.query.filter_by(id=call.message.chat.id).first()
        
        try:
            await FILTER[call.message.chat.id]['filter_menu'].delete()
        except Exception as e:
            print(e)
        
        try:
            del FILTER[call.message.chat.id]['filter_menu']
        except Exception as e:
            print(e)
        
        try:
            for i in FILTER[call.message.chat.id]['objects']:
                await i.delete()
                del FILTER[call.message.chat.id]['objects']
        except Exception as e:
            print(e)
        
        try:
            del FILTER[call.message.chat.id]['objects']
        except Exception as e:
            print(e)
        
        try:
            # delete buttons
            await FILTER[call.message.chat.id]['current_item'].delete()
        except Exception as e:
            print(e)
        
        try:
            del FILTER[call.message.chat.id]['current_item']
        except Exception as e:
            print(e)
        
        try:
            await FILTER[call.message.chat.id]['trash'].delete()
        except Exception as e:
            print(e)
        
        try:
            del FILTER[call.message.chat.id]['trash']
        except Exception as e:
            print(e)
        
        
        print(FILTER[call.message.chat.id])
        with app.app_context():
            user.notification = {'status': True, 'filter': FILTER[call.message.chat.id]}
            db.session.commit()
        
        await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['notification']['filter_ok'])
            
    else:
        # if the city is changes, area and rooms is cleared
        
        if func_action == 'city':
            FILTER[call.message.chat.id]['area'] = 'Не выбрано' 
            FILTER[call.message.chat.id]['rooms'] = 'Не выбрано' 
            FILTER[call.message.chat.id]['price'] = 'Не выбрано'
            FILTER[call.message.chat.id]['advertising'] = 'Не выбрано'
        elif func_action == 'region':
            FILTER[call.message.chat.id]['area'] = 'Не выбрано' 
            FILTER[call.message.chat.id]['rooms'] = 'Не выбрано' 
            FILTER[call.message.chat.id]['price'] = 'Не выбрано'
            FILTER[call.message.chat.id]['city'] = 'Не выбрано'
            FILTER[call.message.chat.id]['advertising'] = 'Не выбрано'
            
            
        FILTER[call.message.chat.id][func_action] = action
        
        try:
            for i in FILTER[call.message.chat.id]['objects']:
                await i.delete()
        except Exception as e:
                print(e)
        
        try:
            # delete buttons
            await FILTER[call.message.chat.id]['current_item'].delete()
        except Exception as e:
            print(e)
            
        try:
            # delete old filter menu
            await FILTER[call.message.chat.id]['filter_menu'].delete()
        except Exception as e:
            print(e)
            
        filter_menu = await bot.send_message(call.message.chat.id, config.OBJECT_TEXT['feed']['filter'], reply_markup=render_filter_button(call.message.chat.id))
        
        FILTER[call.message.chat.id]['filter_menu'] = filter_menu


# ------------------ NOTIFICATION --------------------

@dp.message_handler(Text(equals=config.OBJECT_TEXT['main']['notification_btn']))
async def function_notifications(message: types.Message):
    """FUNCTION NOTIFICATIONS"""

    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(config.OBJECT_TEXT['notification']['yes'], config.OBJECT_TEXT['notification']['no'])
    keyboard.add(config.OBJECT_TEXT['notification']['filter'], config.OBJECT_TEXT['notification']['all'])
    keyboard.add(config.OBJECT_TEXT['main']['back_btn'])
    
    # printing current notification status
    with app.app_context():
        user_settings = Users.query.filter_by(id=message.chat.id).first()
    status = user_settings.notification['status']
    
    if status == False:
        status = '🔕'
    elif status == True:
        status = '🔔'
    await bot.send_message(message.chat.id, f"{config.OBJECT_TEXT['notification']['settings']} ({status})", reply_markup=keyboard)
    
@dp.message_handler(Text(equals=config.OBJECT_TEXT['notification']['yes'], ignore_case=True), state='*')
async def notification_yes_handler(message: types.Message,  state: FSMContext):
    """NOTIFICATON YES HANDLER"""

    with app.app_context():
        user_settings = Users.query.filter_by(id=message.chat.id).first()
        user_settings.notification = {'status': True, 'filter': None}
        db.session.commit()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['notification']['yes'], reply_markup=main_keyboard)

@dp.message_handler(Text(equals=config.OBJECT_TEXT['notification']['no'], ignore_case=True), state='*')
async def notification_no_handler(message: types.Message,  state: FSMContext):
    """NOTIFICATON NO HANDLER"""

    with app.app_context():
        user_settings = Users.query.filter_by(id=message.chat.id).first()
        user_settings.notification = {'status': False, 'filter': None}
        db.session.commit()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['notification']['no'], reply_markup=main_keyboard)

@dp.message_handler(Text(equals=config.OBJECT_TEXT['notification']['all'], ignore_case=True), state='*')
async def notification_all_handler(message: types.Message,  state: FSMContext):
    """NOTIFICATON ALL HANDLER"""

    with app.app_context():
        user_settings = Users.query.filter_by(id=message.chat.id).first()
        user_settings.notification = {'status': True, 'filter': None}
        db.session.commit()
    await bot.send_message(message.chat.id, config.OBJECT_TEXT['notification']['all'], reply_markup=main_keyboard)


@dp.message_handler(Text(equals=config.OBJECT_TEXT['notification']['filter'], ignore_case=True), state='*')
async def notification_filter_handler(message: types.Message,  state: FSMContext):
    """NOTIFICATON FILTER HANDLER"""
    
    # toggle filter application
    SWITCH[message.chat.id] = {'current': 'notification'}
    # user_settings = Users.query.filter_by(id=message.chat.id).first()
    
    # user init in NOTIFICATION DICT
    NOTIFICATION[message.chat.id] = {}
    
    
    msg = await bot.send_message(message.chat.id, config.OBJECT_TEXT['notification']['filter'], reply_markup=render_filter_button(message.chat.id))
    FILTER[message.chat.id]['filter_menu'] = msg


def render_filter_button(id):
    """FEED. RENDER FILTER BUTTONS"""
    filter_items_keyboard = types.InlineKeyboardMarkup(
        resize_keyboard=True, selective=True, row_width=1)

    if id in FILTER:
        with app.app_context():
            user = Users.query.filter_by(id=id).first()

        if 'region' in FILTER[id]:
            current_region = FILTER[id]['region']
        else:
            # user city
            current_region = user.region

        if 'city' in FILTER[id]:
            current_city = FILTER[id]['city']
        else:
            # user city
            current_city = 'Не выбрано'

        if 'area' in FILTER[id]:
            current_area = FILTER[id]['area']
        else:
            current_area = 'Не выбрано'

        if 'rooms' in FILTER[id]:
            current_rooms = FILTER[id]['rooms']
        else:
            current_rooms = 'Не выбрано'

        if 'price' in FILTER[id]:

            try:
                current_price = FILTER[id]['price']['text']
            except Exception as e:
                current_price = 'Не выбрано'
        else:
            current_price = 'Не выбрано'
            
        if 'advertising' in FILTER[id]:
            current_advertising = FILTER[id]['advertising']
        else:
            current_advertising = 'Не выбрано'

        if 'count' in FILTER[id]:
            current_count = len(get_result_objects(id))
        else:
            with app.app_context():
                current_count = len(
                    Objects.query.filter_by(region=current_region).all())
    else:

        # default user city and region

        with app.app_context():
            user = Users.query.filter_by(id=id).first()
            
        current_region = user.region
        current_city = 'Не выбрано'
        current_area = 'Не выбрано'
        current_rooms = 'Не выбрано'
        current_price = 'Не выбрано'
        current_advertising = 'Не выбрано'
        with app.app_context():
            current_count = len(Objects.query.filter_by(city=current_city).all())

        FILTER[id] = {'city': current_city, 'area': current_area,
                      'rooms': current_rooms, 'price': current_price,
                      'count': current_count, 'region': current_region, 'advertising': current_advertising}

    buttons = [
        types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['region_btn']}: {current_region}", callback_data='filter_item_region'),
        types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['city_btn']}: {current_city}", callback_data='filter_item_city'),
        types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['area_btn']}: {current_area}", callback_data='filter_item_area'),
        types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['rooms_btn']}: {current_rooms}", callback_data='filter_item_rooms'),
        types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['price']}: {current_price}", callback_data='filter_item_price'),
        types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['advertising_btn']}: {current_advertising}", callback_data='filter_item_advertising')
    ]
    
    filter_items_keyboard.add(*buttons)
    if SWITCH[id]['current'] == 'objects':
        filter_items_keyboard.row(types.InlineKeyboardButton(
            f"{config.OBJECT_TEXT['feed']['feed_ok_filter']} ({current_count})", callback_data='filter_item_ok'), 
                                  types.InlineKeyboardButton(f"{config.OBJECT_TEXT['feed']['clear']}", callback_data='filter_item_clear'))
        
    else:
        filter_items_keyboard.row(types.InlineKeyboardButton(f"{config.OBJECT_TEXT['notification']['filter_btn_ok']}", callback_data='filter_notification_ok'))
    
    
    return filter_items_keyboard


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)