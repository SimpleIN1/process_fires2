import os
import shutil
import signal
import time
import random

fr0m = 'monitor_dir'
to = 'monitor_dir_1'


def handle_signal(signal, frame) -> None:
    global file_dict
    print('Handler start')
    for file in os.listdir(to):
        os.remove(f'{to}/{file}')
    print('Handler stop. Files have been deleted')
    exit()


def run():
    for file in os.listdir(fr0m):
        # print(file)
        time.sleep(random.randint(1,3))
        print('Copy ' + file)
        shutil.copy(f'{fr0m}/{file}', f'{to}/{file}')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_signal)
    run()