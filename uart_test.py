import serial
import time

# Mở UART
ser = serial.Serial(
    '',   # đổi COM đúng máy bạn
    9600
)

time.sleep(2)

while True:

    data = input("Nhap ky tu: ")

    ser.write(data.encode())

    print("Da gui:", data)