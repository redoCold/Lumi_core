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

  // Ids: 10, 13 (Wheels) | 9, 11, 14 (Arms/Neck)
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
  // НЭГДСЭН СЕРИАЛ УНШИГЧ (Single Serial Reader)
  while (Serial.available() > 0) { 
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() == 0) continue; 

    // 1. Өндөр түвшний Навигацийн тушаалууд (Jetson Nano AI-аас ирэх)
    if (input.startsWith("NAV_TO:")) {
      String location = input.substring(7);
      
      if (location == "SECTION_A") {
        move_robot(150, 0); // Инженерчлэлийн хэсэг
      } 
      else if (location == "SECTION_B") {
        move_robot(150, 45); // Мэдээллийн технологийн хэсэг
      }
    }
    // 2. Бүх моторыг зогсоох
    else if (input == "STOP" || input == "STOP_ALL") {
      stop_motors();
    }
    // 3. Нам түвшний шууд тушаалууд (M:id:val эсвэл P:id:val)
    else {
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
            raw_speed = abs(val) + 1024; // Reverse
          }
          dxl.setGoalVelocity(id, raw_speed);
        } 
        else if (type == 'P') {
          dxl.setGoalPosition(id, val);
        }
      }
    }
  }
  
  // PID болон бусад тасралтгүй тооцооллууд энд хийгдэнэ
  // update_pid_control(); 
  delay(10);
}

// --- ТУСЛАХ ФУНКЦҮҮД (Helper Functions) ---

void stop_motors() {
  dxl.setGoalVelocity(10, 0);
  dxl.setGoalVelocity(13, 0);
}

void move_robot(int velocity, int angle) {
  // Энд та өнцөг болон хурдыг дугуй тус бүрийн хурд руу хөрвүүлэх 
  // Кинематик тооцооллоо хийнэ. Түр хугацаанд шууд урагшаа явахаар тохируулав.
  dxl.setGoalVelocity(10, velocity);
  dxl.setGoalVelocity(13, velocity); // Хэрэв нэг дугуй эсрэг харсан бол чиглэлийг өөрчлөх хэрэгтэй
}