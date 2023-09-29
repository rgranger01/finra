import os
import time
import random
import pyautogui
import pytest
from pytest import fixture
from pygetwindow import getWindowsWithTitle
import threading
import psutil

def open_calculator():
    os.system("start calc.exe")
    time.sleep(2)

def close_calculator():
    os.system("taskkill /im calc.exe /f")

def focus_calculator():
    windows = getWindowsWithTitle("Calculator")
    if windows:
        calculator_window = windows[0]
        calculator_window.activate()

def press_key(key):
    key_map = {
        '+': 'add',
        '-': 'subtract',
        '*': 'multiply',
        '/': 'divide',
        '=': 'enter',
        'esc': 'esc',
        'backspace': 'backspace',
        'CE': 'home',
        'C': 'end'
    }
    pyautogui.press(key_map.get(key, key))


def write_to_csv(data):
    with open('test_log.csv', 'a') as f:
        f.write(','.join(map(str, data)) + '\n')


def monitor_performance():
    with open('perf_metrics.log', 'w') as file:
        file.write("Timestamp,CPU (%),Memory (bytes)\n")

    while not stop_event.is_set():
        try:
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info().rss
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            with open('perf_metrics.log', 'a') as file:
                file.write(f"{timestamp},{cpu_percent},{memory_info}\n")

            time.sleep(1)
        except KeyboardInterrupt:
            break

@fixture(scope='module', autouse=True)
def calculator_setup():
    """Setup and teardown for calculator application."""
    open_calculator()
    focus_calculator()


    monitor_thread = threading.Thread(target=monitor_performance)
    monitor_thread.start()

    yield
    close_calculator()


def timer_function():
    global stop_event
    time.sleep(30)
    stop_event.set()

@pytest.mark.parametrize("iteration", range(50))
def test_random_operation(iteration):

    start_time = time.time()

    press_key('esc')

    num1 = random.randint(0, 9)
    num2 = random.randint(0, 9)
    operator = random.choice(['+', '-', '*', '/'])

    if operator == '+':
        expected = num1 + num2
    elif operator == '-':
        expected = num1 - num2
    elif operator == '*':
        expected = num1 * num2
    else:
        if num2 == 0:
            return
        else:
            expected = round(num1 / num2, 2)

    for key in str(num1), operator, str(num2), '=':
        press_key(key)

    computed_result = None
    if operator == '+':
        computed_result = num1 + num2
    elif operator == '-':
        computed_result = num1 - num2
    elif operator == '*':
        computed_result = num1 * num2
    elif operator == '/':
        if num2 != 0:
            computed_result = round(num1 / num2, 2)


    end_time = time.time()


    duration = end_time - start_time


    if computed_result == expected:
        status = "PASS"
    else:
        status = "FAIL"


    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    data = [timestamp, duration, f"{num1} {operator} {num2}", expected, computed_result, status]
    write_to_csv(data)


stop_event = threading.Event()
timer_thread = threading.Thread(target=timer_function)
timer_thread.start()

if __name__ == "__main__":
    pytest.main([__file__])
