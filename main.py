import json
import asyncio

from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

sended_users = []
users = list(set([us for us in open("users.txt", "r", encoding="utf-8").read().split("\n") if us != ""]))
message = open("message.txt", "r", encoding="utf-8").read()
with open("user.json", "r", encoding="utf-8") as j_file:
    user_file = json.load(j_file)
    api_name, api_id, api_hash = user_file["name"], user_file["api_id"], user_file["api_hash"]


async def get_user(app: TelegramClient, username):
    return await app(GetFullUserRequest(username))


async def save_data():
    with open("sended_users.txt", "w", encoding="utf-8") as saving_file:
        saving_file.write("\n".join(sended_users))

        with open("users.txt", "w", encoding="utf-8") as deleting_send_users:
            for user in users:
                if user not in sended_users:
                    deleting_send_users.write(user + "\n")


async def main():
    try:
        async with TelegramClient(api_name, api_id, api_hash) as app:
            for username in users:
                user = await get_user(app, username)
                await app.send_message(user.to_dict()["full_user"]["id"], message)
                sended_users.append(username)
    except Exception as error:
        print(error.__class__.__name__)
        await save_data()
    await save_data()


if __name__ == '__main__':
    asyncio.run(main())
