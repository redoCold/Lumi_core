import serial
import matplotlib.pyplot as plt
import numpy as np
#--- CONFIG 
PORT = 'COM13'
BAUD = 115200
LIFE_SPAN = 5
ser = serial.Serial(PORT, BAUD, timeout=0.1)
plt.ion()
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
line, = ax.plot([], [], 'ro', markersize=2)
ax.set_ylim(0, 400) 
ax.set_theta_offset(np.pi / 2)
scan_data = np.zeros(360)
life_data = np.zeros(360)
def get_points():
    if ser.in_waiting >= 47:
        raw = ser.read(ser.in_waiting)
        chunks = raw.split(b'\x54\x2c')
        for chunk in chunks:
            if len(chunk) >= 44:
                start_angle = (chunk[3] << 8 | chunk[2]) / 100.0
                for i in range(12):
                    off = 4 + (i * 3)
                    dist = (chunk[off+1] << 8 | chunk[off]) / 10.0 # to CM
                    conf = chunk[off+2]
                    if 15 < dist < 400 and conf > 10:
                        angle = int((start_angle + (i * 1.0)) % 360)
                        scan_data[angle] = dist     # Set the distance
                        life_data[angle] = LIFE_SPAN # Reset the "Life" timer
#--- GRAPH
try:
    while True:
        life_data[life_data > 0] -= 1
        scan_data[life_data == 0] = 0
        get_points()
        radians = np.deg2rad(np.arange(360))
        plot_mask = np.where(life_data > 0, scan_data, np.nan)
        line.set_data(radians, plot_mask)
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        plt.pause(0.001)
except KeyboardInterrupt:
    ser.close()