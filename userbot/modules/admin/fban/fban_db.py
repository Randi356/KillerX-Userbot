from userbot import MONGO


async def get_fban():
    return MONGO.fban.find()


async def add_chat_fban(chat_id):
    if await is_fban(chat_id) is True:
        return False
    else:
        MONGO.fban.insert_one({'chat_id': chat_id})


async def remove_chat_fban(chat_id):
    if await is_fban(chat_id) is False:
        return False
    else:
        MONGO.fban.delete_one({'chat_id': chat_id})
        return True


async def is_fban(chat_id):
    if not MONGO.fban.find_one({"chat_id": chat_id}):
        print("FAILED on fed")
        return False
    else:
        return True
