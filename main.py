import json
import asyncio
import random
import traceback

from telethon import TelegramClient
from telethon.errors import FloodWaitError, PeerFloodError
from telethon.tl.functions.users import GetFullUserRequest

sended_users = []
flood_errors = {}
max_errors = 50

users = list(set([us for us in open("users.txt", "r", encoding="utf-8").read().split("\n") if us != ""]))
message = open("message.txt", "r", encoding="utf-8").read()
errors = open("errors.txt", "w", encoding="utf-8")
with open("user.json", "r", encoding="utf-8") as j_file:
    user_file = json.load(j_file)
    api_name, api_id, api_hash = user_file["name"], user_file["api_id"], user_file["api_hash"]
    wait = user_file["wait"]


async def exit_(code):
    await save_data()


async def log_error(err_name):
    flood_errors[err_name] = flood_errors[err_name] + 1 if err_name in flood_errors else 1
    errors.write(err_name + "\n")


async def check_errors():
    for err, counter in flood_errors.items():
        if counter >= max_errors:
            await save_data()
            print(f"Broke because a lot of {err} errors")
            await exit_(0)


async def get_user(app: TelegramClient, username):
    return await app(GetFullUserRequest(username))


async def save_data():
    with open("sended_users.txt", "w", encoding="utf-8") as saving_file:
        saving_file.write("\n".join(sended_users))

        with open("users.txt", "w", encoding="utf-8") as deleting_send_users:
            for user in users:
                if user not in sended_users:
                    deleting_send_users.write(user + "\n")


async def send_for_user(app, username):
    user = await get_user(app, username)
    await app.send_message(user.to_dict()["full_user"]["id"], message)
    sended_users.append(username)


async def main():
    try:
        app = TelegramClient(api_name, api_id, api_hash)
        await app.start()

        for username in users:
            try:
                await send_for_user(app, username)
            except FloodWaitError:
                await save_data()
                print("Flood error, wait")
                if wait:
                    await asyncio.sleep(random.randint(10, 40))
                await app.disconnect()
                app = TelegramClient(api_name, api_id, api_hash)
                await app.start()
                print("FloodWaitError")
            except PeerFloodError:
                await save_data()
                if wait:
                    await asyncio.sleep(random.randint(10, 40))
                await app.disconnect()
                app = TelegramClient(api_name, api_id, api_hash)
                await app.start()
                print("PeerFloodError")
            except Exception as error:
                print(traceback.format_exc())
                print(error)
            except BaseException as based:
                print(traceback.format_exc())
                print(based)
                await save_data()
        await save_data()
        await exit_(0)
    except KeyboardInterrupt:
        await save_data()


if __name__ == '__main__':
    asyncio.run(main())
