# Copyright (C) 2024 officialputuid

import aiohttp
import asyncio
import base64
import datetime
import json
import random
import re
import ssl
import time
import uuid
import websockets

from loguru import logger
import pyfiglet
from websockets_proxy import Proxy, proxy_connect

logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format=(
        "<green>{time:DD/MM/YY HH:mm:ss}</green> | "
        "<level>{level:8} | {message}</level>"
    ),
    colorize=True
)

# main.py
def print_header():
    cn = pyfiglet.figlet_format("xGrassBot")
    print(cn)
    print("🌱 Season 2")
    print("🎨 by \033]8;;https://github.com/officialputuid\033\\officialputuid\033]8;;\033\\")
    print('🎁 \033]8;;https://paypal.me/IPJAP\033\\Paypal.me/IPJAP\033]8;;\033\\ — \033]8;;https://trakteer.id/officialputuid\033\\Trakteer.id/officialputuid\033]8;;\033\\')

# Initialize the header
print_header()

# Number of proxies to use /uid
ONETIME_PROXY = 100
DELAY_INTERVAL = 0.5
MAX_RETRIES = 3
FILE_UID = "uid.txt"
FILE_PROXY = "proxy.txt"
USERAGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.57",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.52",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.46",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.128",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.112",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.98",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.83",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.133",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.121",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91"
]
HTTP_STATUS_CODES = {
    200: "OK",
    201: "Created",
    202: "Accepted",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout"
}

# Read UID and Proxy count
def read_uid_and_proxy():
    with open(FILE_UID, 'r') as file:
        uid_count = sum(1 for line in file)

    with open(FILE_PROXY, 'r') as file:
        proxy_count = sum(1 for line in file)

    return uid_count, proxy_count

uid_count, proxy_count = read_uid_and_proxy()

print()
print(f"🔑 UID: {uid_count}. from {FILE_UID}.")
print(f"🌐 Loaded {proxy_count} proxies. from {FILE_PROXY}.")
print(f"🌐 Active proxy loaded per-task: {ONETIME_PROXY} proxies.")
print()

# Get User input for proxy failure handling
def get_user_input():
    user_input = ""
    while user_input not in ['yes', 'no']:
        user_input = input("🔵 Do you want to remove the proxy if there is a specific failure (yes/no)? ").strip().lower()
        if user_input not in ['yes', 'no']:
            print("🔴 Invalid input. Please enter 'yes' or 'no'.")
    return user_input == 'yes'

remove_on_all_errors = get_user_input()
print(f"🔵 You selected: {'Yes' if remove_on_all_errors else 'No'}, ENJOY!\n")

# Ask user for node type
def get_node_type():
    node_type = ""
    while node_type not in ['desktop', 'extension', 'grasslite']:
        print(f"🧩 Desktop Node (2.0x Reward), Extension (1.25x Reward), GrassLite (1.0x Reward)")
        node_type = input("🔵 Choose node type (desktop/extension/grasslite): ").strip().lower()
        if node_type not in ['desktop', 'extension', 'grasslite']:
            print("🔴 Invalid input. Please enter 'desktop' / 'extension' / 'grasslite'.")
    return node_type

node_type = get_node_type()
print(f"🔵 You selected: {node_type.capitalize()} node. ENJOY!\n")

def truncate_userid(user_id):
    return f"{user_id[:3]}--{user_id[-3:]}"

def truncate_proxy(proxy):
    pattern = r'([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})|(?:\d{1,3}\.){3}\d{1,3})'
    match = re.search(pattern, proxy)
    if match:
        return match.group(0)
    return 'Undefined'

def count_proxies(FILE_PROXY):
    try:
        with open(FILE_PROXY, 'r') as file:
            proxies = file.readlines()
        return len(proxies)
    except FileNotFoundError:
        logger.error(f"File {FILE_PROXY} not found!")
        return 0

async def connect_to_wss(protocol_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, protocol_proxy))
    random_user_agent = random.choice(USERAGENTS)
    logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | Generate Device ID: {device_id} | Proxy: {truncate_proxy(protocol_proxy)}")

    has_received_action = False
    is_authenticated = False

    total_proxies = count_proxies(FILE_PROXY)

    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": random_user_agent
            }

            if node_type == "extension":
                custom_headers["Origin"] = "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi"
            elif node_type == "grasslite":
                custom_headers["Origin"] = "chrome-extension://ilehaonighjijnmpnagapkhpcdbhclfg"

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            urilist = [
                "wss://proxy2.wynd.network:4444", 
                "wss://proxy2.wynd.network:4650"
            ]
            uri = random.choice(urilist)
            server_hostname = uri.split("://")[1].split(":")[0]
            proxy = Proxy.from_url(protocol_proxy)

            async with proxy_connect(
                uri,
                proxy=proxy,
                ssl=ssl_context,
                server_hostname=server_hostname,
                extra_headers=custom_headers
            ) as websocket:
                logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | Success connect to WS | uri: {uri} | Headers: {custom_headers} | Device ID: {device_id} | Proxy: {truncate_proxy(protocol_proxy)} | Remaining Proxy: {total_proxies}")

                async def send_ping():
                    while True:
                        if has_received_action:
                            send_message = json.dumps({
                                "id": str(uuid.uuid4()),
                                "version": "1.0.0",
                                "action": "PING",
                                "data": {}
                            })
                            logger.debug(f"UID: {truncate_userid(user_id)} | {node_type} | Send PING message | data: {send_message}")
                            await asyncio.sleep(DELAY_INTERVAL)
                            await websocket.send(send_message)
                            logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | Done sent PING | data: {send_message}")

                        rand_sleep = random.uniform(10, 30)
                        logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | Next PING in {rand_sleep:.2f} seconds, ENJOY!")
                        await asyncio.sleep(rand_sleep)

                await asyncio.sleep(DELAY_INTERVAL)
                send_ping_task = asyncio.create_task(send_ping())

                try:
                    while True:
                        if is_authenticated and not has_received_action:
                            logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | Authenticated | Wait for PING Gate to Open for {'HTTP_REQUEST' if node_type in ['extension', 'grasslite'] else 'OPEN_TUNNEL'}")

                        response = await websocket.recv()
                        message = json.loads(response)
                        logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | Received message | data: {message}")

                        if message.get("action") == "AUTH":
                            extension_ids = {
                                "extension": "lkbnfiajjmbhnfledhphioinpickokdi",
                                "grasslite": "ilehaonighjijnmpnagapkhpcdbhclfg"
                            }

                            auth_response = {
                                "id": message["id"],
                                "origin_action": "AUTH",
                                "result": {
                                    "browser_id": device_id,
                                    "user_id": user_id,
                                    "user_agent": random_user_agent,
                                    "timestamp": int(time.time()),
                                    "device_type": "extension" if node_type in ["extension", "grasslite"] else "desktop",
                                    "version": "4.26.2" if node_type == "extension" else "4.30.0"
                                }
                            }

                            if node_type in extension_ids:
                                auth_response["result"]["extension_id"] = extension_ids[node_type]

                            logger.debug(f"UID: {truncate_userid(user_id)} | {node_type} | Send AUTH | data: {auth_response}")
                            await asyncio.sleep(DELAY_INTERVAL)
                            await websocket.send(json.dumps(auth_response))
                            logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | Done sent AUTH | data: {auth_response}")
                            is_authenticated = True

                        elif message.get("action") in ["HTTP_REQUEST", "OPEN_TUNNEL"]:
                            has_received_action = True
                            request_data = message["data"]

                            headers = {
                                "User-Agent": custom_headers["User-Agent"],
                                "Content-Type": "application/json; charset=utf-8"
                            }

                            async with aiohttp.ClientSession() as session:
                                async with session.get(request_data["url"], headers=headers) as api_response:
                                    content = await api_response.text()
                                    encoded_body = base64.b64encode(content.encode()).decode()

                                    status_text = HTTP_STATUS_CODES.get(api_response.status, "")

                                    http_response = {
                                        "id": message["id"],
                                        "origin_action": message["action"],
                                        "result": {
                                            "url": request_data["url"],
                                            "status": api_response.status,
                                            "status_text": status_text,
                                            "headers": dict(api_response.headers),
                                            "body": encoded_body
                                        }
                                    }

                                    logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | Open PING Access | data: {http_response}")
                                    await asyncio.sleep(DELAY_INTERVAL)
                                    await websocket.send(json.dumps(http_response))
                                    logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | Done sent PING Access | data: {http_response}")

                        elif message.get("action") == "PONG":
                            pong_response = {"id": message["id"], "origin_action": "PONG"}
                            logger.debug(f"UID: {truncate_userid(user_id)} | {node_type} | Send PONG | data: {pong_response}")
                            await asyncio.sleep(DELAY_INTERVAL)
                            await websocket.send(json.dumps(pong_response))
                            logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | Done sent PONG | data: {pong_response}")

                except websockets.exceptions.ConnectionClosedError as e:
                    logger.error(f"UID: {truncate_userid(user_id)} | {node_type} | Connection closed error | Proxy: {truncate_proxy(protocol_proxy)} | Error: {str(e)} | Remaining Proxy: {total_proxies}")
                    await asyncio.sleep(DELAY_INTERVAL)
                finally:
                    await websocket.close()
                    logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | WebSocket connection closed | Proxy: {truncate_proxy(protocol_proxy)} | Remaining Proxy: {total_proxies}")
                    send_ping_task.cancel()
                    await asyncio.sleep(DELAY_INTERVAL)
                    break

        except Exception as e:
            logger.error(f"UID: {truncate_userid(user_id)} | {node_type} | Error with proxy {truncate_proxy(protocol_proxy)} ➜ {str(e)} | Remaining Proxy: {total_proxies}")
            error_conditions = [
                "403 Forbidden",
                "Host unreachable",
                "Empty host component",
                "Invalid scheme component",
                "[SSL: WRONG_VERSION_NUMBER]",
                "invalid length of packed IP address string",
                "Empty connect reply",
                "Device creation limit exceeded",
                "[Errno 111] Could not connect to proxy",
                "sent 1011 (internal error) keepalive ping timeout; no close frame received"
            ]
            skip_proxy = [
                "Proxy connection timed out: 60",
                "407 Proxy Authentication Required",
                "Invalid port component"
            ]

            if any(error_msg in str(e) for error_msg in skip_proxy):
                logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Skipping proxy due to error ➜ {truncate_proxy(protocol_proxy)} | Remaining Proxy: {total_proxies}")
                return "skip"

            if remove_on_all_errors:
                if any(error_msg in str(e) for error_msg in error_conditions):
                    logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Removing error proxy due to error ➜ {truncate_proxy(protocol_proxy)} | Remaining Proxy: {total_proxies}")
                    remove_proxy_from_list(protocol_proxy)
                    return None
            else:
                if "Device creation limit exceeded" in str(e):
                    logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Removing error proxy due to error ➜ {truncate_proxy(protocol_proxy)} | Remaining Proxy: {total_proxies}")
                    remove_proxy_from_list(protocol_proxy)
                    return None

            await asyncio.sleep(DELAY_INTERVAL)
            continue

async def main():
    with open(FILE_UID, 'r') as file:
        user_ids = file.read().splitlines()

    with open(FILE_PROXY, 'r') as file:
        all_proxies = file.read().splitlines()

    if len(all_proxies) < ONETIME_PROXY * len(user_ids):
        logger.error(f"The number of proxies is insufficient to provide {ONETIME_PROXY} proxies per User ID.")
        return

    random.shuffle(all_proxies)
    proxy_allocation = {
        user_id: all_proxies[i * ONETIME_PROXY: (i + 1) * ONETIME_PROXY]
        for i, user_id in enumerate(user_ids)
    }

    retry_count = {}

    for user_id, proxies in proxy_allocation.items():
        logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Total proxies to be used: {len(proxies)}")
        await asyncio.sleep(DELAY_INTERVAL)

    tasks = {}

    for user_id, proxies in proxy_allocation.items():
        for proxy in proxies:
            retry_count[(proxy, user_id)] = 0
            await asyncio.sleep(DELAY_INTERVAL)
            task = asyncio.create_task(connect_to_wss(proxy, user_id))
            tasks[task] = (proxy, user_id)

    while True:
        done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            try:
                result = task.result()

                failed_proxy, user_id = tasks[task]

                if result == "skip":
                    retry_count[(failed_proxy, user_id)] += 1

                    if retry_count[(failed_proxy, user_id)] > MAX_RETRIES:
                        logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Max retries (skipping proxy) reached for proxy: {truncate_proxy(failed_proxy)}.")
                        continue

                    logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Skipping proxy: {truncate_proxy(failed_proxy)}")

                    available_proxies = list(set(all_proxies) - set(proxy_allocation[user_id]))
                    if available_proxies:
                        new_proxy = random.choice(available_proxies)
                        proxy_allocation[user_id].append(new_proxy)

                        retry_count[(new_proxy, user_id)] = retry_count[(failed_proxy, user_id)]
                        await asyncio.sleep(DELAY_INTERVAL)
                        new_task = asyncio.create_task(connect_to_wss(new_proxy, user_id))
                        tasks[new_task] = (new_proxy, user_id)
                        logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | Replaced skipping proxy {truncate_proxy(failed_proxy)} with {truncate_proxy(new_proxy)}")
                    else:
                        logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | No available proxies left for replacement.")

                elif result is None:
                    retry_count[(failed_proxy, user_id)] += 1

                    if retry_count[(failed_proxy, user_id)] > MAX_RETRIES:
                        logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Max retries (error proxy) reached for proxy: {truncate_proxy(failed_proxy)}.")
                        proxy_allocation[user_id].remove(failed_proxy)
                        continue

                    logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | Removing and replacing failed proxy: {truncate_proxy(failed_proxy)}")
                    proxy_allocation[user_id].remove(failed_proxy)

                    available_proxies = list(set(all_proxies) - set(proxy_allocation[user_id]))
                    if available_proxies:
                        new_proxy = random.choice(available_proxies)
                        proxy_allocation[user_id].append(new_proxy)

                        retry_count[(new_proxy, user_id)] = retry_count[(failed_proxy, user_id)]
                        await asyncio.sleep(DELAY_INTERVAL)
                        new_task = asyncio.create_task(connect_to_wss(new_proxy, user_id))
                        tasks[new_task] = (new_proxy, user_id)
                        logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | Replaced failed proxy: {truncate_proxy(failed_proxy)} with: {truncate_proxy(new_proxy)}")
                    else:
                        logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | No available proxies left for replacement.")

            except Exception as e:
                logger.error(f"UID: {truncate_userid(user_id)} | {node_type} | Error handling task: {str(e)}")
            finally:
                tasks.pop(task)

        active_proxies = [proxy for _, proxy in tasks.values()]
        for user_id, proxies in proxy_allocation.items():
            for proxy in set(proxies) - set(active_proxies):
                new_task = asyncio.create_task(connect_to_wss(proxy, user_id))
                tasks[new_task] = (proxy, user_id)

def remove_proxy_from_list(proxy):
    with open(FILE_PROXY, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.strip() != proxy:
                file.write(line)
        file.truncate()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info(f"Program terminated by user. ENJOY!\n")
