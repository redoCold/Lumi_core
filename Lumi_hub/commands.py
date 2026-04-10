import serial

class LumiHub:
    def __init__(self, port='COM12'):
        self.LEFT_WHEEL = 10
        self.RIGHT_WHEEL = 13
        self.LEFT_ARM = 9
        self.RIGHT_ARM = 11
        self.NECK = 14
        self.ser = None

        try:
            self.ser = serial.Serial(port, 115200, timeout=0.1)
            print(f"Lumi Hub Connected to {port}")
        except Exception as e:
            print(f"Connection Error: {e}")

    def _send(self, msg):
        if self.ser and self.ser.is_open:
            self.ser.write(msg.encode())

    # --- LOCOMOTION ---
    def drive(self, left, right):
            self._send(f"M:{self.LEFT_WHEEL}:{left}\n")
            self._send(f"M:{self.RIGHT_WHEEL}:{right}\n")
    def sync_drive(self, speed):
            self.drive(speed, -speed)
    # --- ARMS ---
    def arm_cross(self):
        """Moves arms into an X shape (Z key)"""
        self._send(f"P:{self.LEFT_ARM}:700\n")
        self._send(f"P:{self.RIGHT_ARM}:300\n")
    def arm_opposite(self):
        """Moves arms wide apart (X key)"""
        self._send(f"P:{self.LEFT_ARM}:300\n")
        self._send(f"P:{self.RIGHT_ARM}:700\n")
    def sync_arms(self, position):
        """Standard mirrored arm movement"""
        self._send(f"P:11:{position}\n")
        self._send(f"P:9:{1023 - position}\n")
    # --- HEAD ---
    def look(self, position):
        self._send(f"P:{self.NECK}:{position}\n")
    # --- STOP ---
    def stop(self):
        self.drive(0, 0)
        self._send("STOP\n")