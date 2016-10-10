from sendData import SendData
import evdev
import argparse
from threading import Thread
from processor import get_directions, translate_grades

class Controller(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setup()

    def get_gamepad(self):
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
            if "Gamepad" in device.name:
                self.gamepad = evdev.InputDevice(device.fn)
                return

    def build_package(self, data):
        r2, l2, axis_x, axis_y = data
        package = {"l2": l2, "r2": r2, "axis_x": axis_x, "axis_y": axis_y}
        return package

    def setup(self):
        self.direccion = True
        self.get_gamepad()

        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--triggers",action="store_true", help="enable use of triggers")
        parser.add_argument("-x", "--usex", action="store_true", help = "use axis x, for testing")
        parser.add_argument("-y", "--usey", action="store_true", help = "use axis y, for testing")
        self.args = parser.parse_args()

        self.data_package = self.build_package((0,0,0,0))

        self.sender = Sender()
        self.sender.start()
        #Could be possible to implement later an argument to define which model is going to be used (Julian
        #or Cesar's team)

        print "Thread Controller running with gamepad %s\n" % self.gamepad

    def run(self):
        #self.data.sendDirection(1,1)
        for event in self.gamepad.read_loop():
            #R2
            if(event.code == 5):
                if self.args.triggers:
                    self.data_package["r2"] = int(event.value)
                    self.sender.send(self.data_package)
                """
                if(not self.direccion):
                    self.data.sendDirection(1,1)
                  self.direccion = True
                """
            #L2
            elif(event.code == 2):
                if self.args.triggers:
                    self.data_package["l2"] = int(event.value)
                    self.sender.send(self.data_package)
                """if(self.direccion):
                    self.data.sendDirection(0,0)
                    self.direccion= False
                """
            #D-Pad X
            elif(event.code == 16):
                self.x_value = event.value

            #D-Pad Y
            elif(event.code == 17):
                self.y_value = -event.value

            #Left Stick X
            elif(event.code == 0 and event.type == 3 and self.args.usex):
                self.data_package["axis_x"] = translate_grades(event.value, 'x')
                self.sender.send(self.data_package)

            #Left Stick Y
            elif(event.code == 1 and event.type == 3 and self.args.usey):
                self.data_package["axis_y"] = translate_grades(event.value, 'y')
                self.sender.send(self.data_package)

            else:
                continue

            #self.data.sendSpeed(l2_value,r2_value)
            #self.data.sendDirection(x_value,y_value)

class Sender(Thread):
    def __init__(self):
        Thread.__init__(self)

        ip, port = "localhost", 8888
        self.data = SendData("http://" + ip + ":" + str(port))

    def run(self):
        print "Thread Sender running...\n"

    def send(self, data):
        print data
        #print "X direction: %s, Y direction: %s" % (x_angle, y_angle)
        #print "Left motor: %s, Right motor: %s" % (l2_value, r2_value)

        #sendSpeed(motorL,motorR)
        #self.data.sendSpeed(100,100)
        #sendDirection(motorL,motorR)
        #self.data.sendDirection(200,200)
        #sendCameraAngle(x,y)
        #self.data.sendCameraAngle(80,30)

if __name__ == '__main__':
    controller_thread = Controller()
    controller_thread.start()