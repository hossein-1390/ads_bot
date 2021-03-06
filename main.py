import config
import code_creator
from telethon import utils
import msg
import datetime
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from pymongo import MongoClient
from telethon.sync import TelegramClient,events
from telethon import Button
api_id = 86576
api_hash = '385886b58b21b7f3762e1cde2d651925'
bot_token = config.read("telegram","bot_token")

bot = TelegramClient('bot', api_id, api_hash,proxy=('socks5','127.0.0.1',1080))
bot.start(bot_token=bot_token)


mongo_client = MongoClient('127.0.0.1:27017')
db = mongo_client.user
@bot.on(events.NewMessage())
async def h(event):
    print(event.message)
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    z = event.message.peer_id.user_id
    t = datetime.datetime.now()
    code = code_creator.code()
    try:
        db.users.insert_one({
            "_id" : z,
            "coin" : 0,
            "registration_date" : t,
            "code" : code,
        })
    except:
        # user = db.users.find_one({ '_id': z})
        # code = user.get('code')
        # print(code)
        pass
    keyboard = [
        [
            Button.inline(str(msg.read_msg('connect')),b'1'),
            Button.inline(str(msg.read_msg("create")), b"2"),
        ],
        [
            Button.inline(msg.read_msg("show"), b"3"),
            Button.inline(msg.read_msg("settings"), b"4")
        ],
        [
            Button.inline(msg.read_msg("buy coins"), b"5"),
            Button.inline(msg.read_msg("help"), b"6")
        ]
    ]


    await bot.send_message(z,msg.read_msg('Introduction') , buttons=keyboard)
    find = db.users.find_one({'_id': event.message.peer_id.user_id})
    admin_id = find.get('_id')
    db.connections.insert_one({
        'owner' : admin_id
    })

@bot.on(events.NewMessage(pattern="code:*"))
async def code(event):
    print(event.message)
    if type(event.message.peer_id) == PeerChannel:
        peer_id = event.message.peer_id.channel_id
    elif type(event.message.peer_id) == PeerChat:
        peer_id = event.message.peer_id.chat_id
    elif type(event.message.peer_id) == PeerUser:
        peer_id = event.message.peer_id.user_id
    else:
        peer_id = 0

    chat_from = event.chat if event.chat else (await event.get_chat())  # telegram MAY not send the chat enity
    chat_title = utils.get_display_name(chat_from)

    try:
        db.connections.insert_one({
            '_id' : event.message.peer_id.user_id,
            'title' : chat_title,
            'type' : peer_id,
        })
        print('ok')
    except:
        print('error')


@bot.on(events.CallbackQuery())
async def handler(event):
    find = db.users.find_one({'_id': event.original_update.user_id})
    code_2 = find.get('code')
    if event.data == b'1':
        z = event.original_update.user_id
        await bot.send_message(z, msg.read_msg('code'))
        await bot.send_message(z,code_2)
    else:
        pass


def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()