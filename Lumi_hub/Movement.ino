#include <Dynamixel2Arduino.h>

#define DXL_SERIAL    Serial3
const int DXL_DIR_PIN = 84; 
const int DXL_POWER_ENABLE = 0x12; 

Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

void setup() {
  pinMode(DXL_POWER_ENABLE, OUTPUT);
  digitalWrite(DXL_POWER_ENABLE, HIGH);
  delay(1000); 

  Serial.begin(115200);

  dxl.begin(1000000); 
  dxl.setPortProtocolVersion(1.0); 

  // Ids
  uint8_t all_ids[] = {9, 10, 11, 13, 14};

  for(uint8_t id : all_ids) {
    dxl.torqueOff(id);
    if(id == 10 || id == 13) {
      dxl.setOperatingMode(id, OP_VELOCITY); // Wheels
    } else {
      dxl.setOperatingMode(id, OP_POSITION); // Arms Neck
    }
    dxl.torqueOn(id);
  }
  Serial.println("Lumi Hub: Online @ 1Mbps");
}
void loop() {
  while (Serial.available() > 0) { 
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() == 0) continue; 

    int firstColon = input.indexOf(':');
    int secondColon = input.lastIndexOf(':');

    if (firstColon != -1 && secondColon != -1) {
      char type = input.charAt(0);
      int id = input.substring(firstColon + 1, secondColon).toInt();
      int val = input.substring(secondColon + 1).toInt();

      if (type == 'M') {
        // --- THE MAGIC FIX FOR REVERSE ---
        int raw_speed = 0;
        if (val >= 0) {
          raw_speed = val; // Forward (0 to 1023)
        } else {
          // Reverse: Absolute value + 1024
          raw_speed = abs(val) + 1024; 
        }
        dxl.setGoalVelocity(id, raw_speed);
      } 
      else if (type == 'P') {
        dxl.setGoalPosition(id, val);
      }
    }
    
    if (input == "STOP") {
      dxl.setGoalVelocity(10, 0);
      dxl.setGoalVelocity(13, 0);
    }
  }
}