import serial
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIG
PORT = 'COM13'
BAUD = 115200
LIFE_SPAN = 5 
GRID_SIZE = 200 
CELL_SIZE = 1  # ZOOMED IN: 1cm per pixel (better for a cardboard box)
ser = serial.Serial(PORT, BAUD, timeout=0.1)

# --- DATA STORAGE
scan_data = np.zeros(360)
life_data = np.zeros(360)
map_memory = np.zeros((GRID_SIZE, GRID_SIZE)) 

# Mark the Robot's start position in the center (Gray dot)
map_memory[GRID_SIZE//2, GRID_SIZE//2] = 50

# --- PLOT SETUP
plt.ion()
fig = plt.figure(figsize=(12, 6))

ax1 = fig.add_subplot(121, projection='polar')
line, = ax1.plot([], [], 'ro', markersize=2)
ax1.set_ylim(0, 400)
ax1.set_title("Live Polar Scan")

ax2 = fig.add_subplot(122)
# Using 'hot' or 'binary' can make the box walls pop out more
map_img = ax2.imshow(map_memory, cmap='binary', origin='lower', vmin=0, vmax=100)
ax2.set_title("AI Grid Map (Memory)")

def get_points():
    if ser.in_waiting >= 47:
        raw = ser.read(ser.in_waiting)
        chunks = raw.split(b'\x54\x2c')
        for chunk in chunks:
            if len(chunk) >= 44:
                start_angle = (chunk[3] << 8 | chunk[2]) / 100.0
                for i in range(12):
                    off = 4 + (i * 3)
                    dist = (chunk[off+1] << 8 | chunk[off]) / 10.0
                    conf = chunk[off+2]
                    
                    # LD08 Filter: Cardboard might be close, so 10cm to 400cm
                    if 10 < dist < 400 and conf > 10:
                        angle = int((start_angle + (i * 1.0)) % 360)
                        scan_data[angle] = dist
                        life_data[angle] = LIFE_SPAN
                        update_grid_map(angle, dist)

def update_grid_map(angle, dist):
    center = GRID_SIZE // 2
    # Offset by 90 to align the Polar plot with the Grid plot
    rad = np.deg2rad(angle + 90) 
    
    x_cm = dist * np.cos(rad)
    y_cm = dist * np.sin(rad)
    
    grid_x = int(center + (x_cm / CELL_SIZE))
    grid_y = int(center + (y_cm / CELL_SIZE))
    
    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
        map_memory[grid_y, grid_x] = 100 # Draw Black Wall

# --- MAIN LOOP
try:
    print("Lumi is mapping the box... Watch the right-hand screen!")
    while True:
        life_data[life_data > 0] -= 1
        scan_data[life_data == 0] = 0
        
        get_points()
        
        # Update Polar
        radians = np.deg2rad(np.arange(360))
        plot_mask = np.where(life_data > 0, scan_data, np.nan)
        line.set_data(radians, plot_mask)
        
        # Update Grid - Force a data refresh
        map_img.set_data(map_memory)
        
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        plt.pause(0.01)

except KeyboardInterrupt:
    print("Stopping...")
    ser.close()
    np.save('lumi_box_map.npy', map_memory)
    print("Box map saved!")