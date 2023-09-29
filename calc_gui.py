import PySimpleGUI as sg
import subprocess
import matplotlib.pyplot as plt
import io
from PIL import Image

def run_tests():

    command = ["pytest", "calc.py"]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def read_logs():
    with open("test_log.csv", "r") as file:
        return file.readlines()


def draw_pie_chart(passed, failed):
    labels = ['Passed', 'Failed']
    sizes = [passed, failed]
    colors = ['green', 'red']
    plt.figure(figsize=(5, 3))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Test Results')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


def read_memory_data():
    memory_data = []
    with open('perf_metrics.log', 'r') as file:
        next(file)
        for line in file:
            _, _, memory_bytes = line.strip().split(',')
            memory_data.append(int(memory_bytes))
    return memory_data


def calculate_pass_fail(logs):
    passed = sum(1 for log in logs if 'PASS' in log)
    failed = sum(1 for log in logs if 'FAIL' in log)
    return passed, failed

# GUI layout
layout = [
    [sg.Text("Execute Calculator Test Suite")],
    [sg.Output(size=(60, 10), key='-OUTPUT-TESTS-')],
    [sg.Text("Logs")],
    [sg.Multiline(size=(60, 10), key='-OUTPUT-LOGS-', disabled=True)],
    [sg.Image(key='-PIE-CHART-')],
    [sg.Image(key='-IMAGE-')],
    [sg.Image(key='-LINE-CHART-')],
    [sg.Button("Run Tests"), sg.Button("Exit")]
]

window = sg.Window("Calculator Test Runner", layout)

while True:
    try:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break
        elif event == "Run Tests":

            output = run_tests()
            window['-OUTPUT-TESTS-'].print(output)


            logs = read_logs()
            window['-OUTPUT-LOGS-'].update("".join(logs))


            passed, failed = calculate_pass_fail(logs)


            if passed + failed > 0:
                pie_image = draw_pie_chart(passed, failed)
                window['-PIE-CHART-'].update(data=pie_image.getvalue())
            else:
                print("No valid test results found.")
                window['-PIE-CHART-'].update(filename='')


            memory_data = read_memory_data()
            plt.figure(figsize=(10, 6))
            plt.plot(memory_data, label='Memory (bytes)', marker='o', linestyle='-')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Memory (bytes)')
            plt.title('Memory Usage Over Time')
            plt.grid(True)
            plt.legend()
            plt.savefig('memory_chart.png')


            line_image = Image.open('memory_chart.png')
            line_byte_array = io.BytesIO()
            line_image.save(line_byte_array, format='PNG')
            window['-LINE-CHART-'].update(data=line_byte_array.getvalue())

    except Exception as e:
        print(f"An error occurred: {e}")

window.close()
