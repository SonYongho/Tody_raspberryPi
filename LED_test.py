from gpiozero import LED    # 라이브러리가 클린업 작업을 알아서 해준다.
from time import sleep

red = LED(21)
green = LED(19)

while True:
    red.on()
    green.on()
    sleep(1)
    red.off()
    green.off()
    sleep(1)