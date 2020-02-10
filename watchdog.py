import datetime
import time
# import os
# import colorama
import subprocess
from termcolor import colored

while True:
    last_line = None
    time_now = datetime.datetime.now()

    for line in open("time.log", "r"):
        last_line = line

    print('')
    print(colored(time_now.strftime('Sys last time: ' + "%H:%M:%S"), 'yellow', attrs=['bold']))
    # print(time_now.strftime('Sys last time: ' + "%H:%M:%S"))
    print('log last time: ' + last_line)
    tm_log = last_line[3:5]
    tm_now = time_now.strftime("%M")
    print('time log: ' + tm_log)
    print('time now: ' + tm_now)
    check = int(tm_now) - int(tm_log)
    print('difference: ' + str(check))
    print('')

    if check >= 2 or check < 0:
        print(colored('!!! РАСХОЖДЕНИЕ ПО ВРЕМЕНИ !!!', 'red', attrs=['bold']))
        print(colored('--- ВЕРОЯТНО ЗАВИСАНИЕ ПРОЦЕССА ---', 'cyan', attrs=['bold']))
        program = "C:\Python\project\mybin\script_start.bat"
        subprocess.Popen(program)
        # subprocess.call([r'C:\Python\project\mybin\script_start.bat'])

    # os.system ("taskkill /f /im  Binbot.exe")
    # print('--- ПРОЦЕСС ОСТАНОВЛЕН ---')
    # #os.system(r'C:/Users/trogwar/Desktop/dist_0.1.3.2/bot.exe')
    # #print('ПРОЦЕСС ЗАПУЩЕН')
    else:
        print(colored('--- ПРОЦЕСС АКТИВЕН ---', 'green', attrs=['bold']))
    time.sleep(10)
