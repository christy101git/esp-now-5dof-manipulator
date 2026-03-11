#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <WiFi.h>
#include <esp_now.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// --- PCA9685 Channel Mapping ---
#define CH_BASE360   0  
#define CH_SHOULDER  1  
#define CH_ELBOW     2  
#define CH_WRIST_P   3  
#define CH_WRIST_R   4  
#define CH_GRIPPER   5  

// --- 1. BASE 360 CALIBRATION ---
#define BASE360_STOP   280 
#define BASE360_LEFT   330 
#define BASE360_RIGHT  210 

// --- 2. STANDARD PULSE LIMITS ---
#define PULSE_MIN  150 // ~0 degrees
#define PULSE_MAX  600 // ~180 degrees

// --- 3. SHOULDER CALIBRATION (Restored Safe Limits) ---
#define SHOULDER_MIN_TICK 260
#define SHOULDER_MAX_TICK  450

// --- 4. GRIPPER CALIBRATION ---
#define GRIPPER_CLOSE_TICK 200 
#define GRIPPER_OPEN_TICK  450 

bool isPowered = false;      
bool gloveOverride = false;  
bool lastGloveState = false; 
uint8_t lastPreset = 0;

// Must match the ESP8266 Glove struct exactly!
typedef struct struct_message {
    uint8_t gloveActive;  
    int16_t pitch;        
    int16_t roll;         
    uint8_t preset;       
} struct_message;

struct_message gloveData;

// Helper: Standard 0-180 angle to PCA9685 pulse (Used by Elbow, Wrist, etc.)
int angleToPulse(int ang) {
  ang = constrain(ang, 0, 180);
  return map(ang, 0, 180, PULSE_MIN, PULSE_MAX);
}

// Helper: Dedicated to the Shoulder to enforce safe physical gear limits!
int shoulderAngleToPulse(int ang) {
  ang = constrain(ang, 9, 170); // Python dashboard slider limits
  return map(ang, 9, 170, SHOULDER_MIN_TICK, SHOULDER_MAX_TICK);
}

// --- ESP-NOW CALLBACK (UPDATED FOR ESP32 V3 CORE) ---
void OnDataRecv(const esp_now_recv_info * info, const uint8_t *incomingData, int len) {
  memcpy(&gloveData, incomingData, sizeof(gloveData));
  
  // 1. Detect if the Glove Switch was just flipped ON or OFF
  if (gloveData.gloveActive == 1) {
    if (!lastGloveState) {
      Serial.println("GLOVE:ON"); // Tells Python to Lock the UI!
      lastGloveState = true;
    }
    gloveOverride = true;
    
    // 2. Detect Presets and trigger Python!
    if (gloveData.preset == 1 && lastPreset != 1) {
      Serial.println("GLOVE:PLUCK"); 
      lastPreset = 1;
    } 
    else if (gloveData.preset == 2 && lastPreset != 2) {
      Serial.println("GLOVE:UNPLUCK"); 
      lastPreset = 2;
    }
    else if (gloveData.preset == 0) {
      lastPreset = 0; // Reset when hand is flat
      
      // 3. Manual Glove Tracking (when not running a preset)
      int shoulderAng = map(gloveData.pitch, -45, 45, 170, 9); 
      // Safely route tracking data through the dedicated Shoulder helper
      pwm.setPWM(CH_SHOULDER, 0, shoulderAngleToPulse(shoulderAng));

      int wristRollAng = map(gloveData.roll, -45, 45, 0, 180);
      pwm.setPWM(CH_WRIST_R, 0, angleToPulse(wristRollAng));
      
      // Keep Elbow safely stable at a resting 25 degrees during hand tracking
      pwm.setPWM(CH_ELBOW, 0, angleToPulse(25));
    }
    
  } else {
    // Switch is OFF
    if (lastGloveState) {
      Serial.println("GLOVE:OFF"); // Tells Python to Unlock the UI!
      lastGloveState = false;
    }
    gloveOverride = false;
    lastPreset = 0;
  }
}

void setup() {
  Serial.begin(115200);
  
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(50);
  
  // Set device as a Wi-Fi Station for ESP-NOW
  WiFi.mode(WIFI_STA);
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  
  // Register the updated callback function
  esp_now_register_recv_cb(OnDataRecv);

  // Turn off all servos on boot safely
  for(int i=0; i<16; i++) pwm.setPWM(i, 0, 0);
  pwm.setPWM(CH_BASE360, 0, BASE360_STOP);
  
  Serial.println("SYSTEM READY: 6-AXIS HYBRID (ESP-NOW + PYTHON)");
}

void loop() {
  // --- PYTHON DASHBOARD LOGIC (Via USB Cable) ---
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "P:ON") {
      isPowered = true;
    } else if (cmd == "P:OFF") {
      isPowered = false;
      for(int i=0; i<16; i++) pwm.setPWM(i, 0, 0); 
    } 
    
    // Only obey Python sliders if the Glove Switch is OFF
    else if (isPowered && !gloveOverride) {
      if (cmd == "B:L") pwm.setPWM(CH_BASE360, 0, BASE360_LEFT);
      else if (cmd == "B:R") pwm.setPWM(CH_BASE360, 0, BASE360_RIGHT);
      else if (cmd == "B:S") {
        pwm.setPWM(CH_BASE360, 0, BASE360_STOP); 
        delay(150); 
        pwm.setPWM(CH_BASE360, 0, 0); 
      } 
      // FIXED: Route Shoulder commands exclusively to the safe limits
      else if (cmd.startsWith("A1:")) pwm.setPWM(CH_SHOULDER, 0, shoulderAngleToPulse(cmd.substring(3).toInt()));
      
      else if (cmd.startsWith("A2:")) pwm.setPWM(CH_ELBOW,    0, angleToPulse(cmd.substring(3).toInt()));
      else if (cmd.startsWith("A3:")) pwm.setPWM(CH_WRIST_P,  0, angleToPulse(cmd.substring(3).toInt()));
      else if (cmd.startsWith("A4:")) pwm.setPWM(CH_WRIST_R,  0, angleToPulse(cmd.substring(3).toInt()));
      
      // PERFECTED GRIPPER SLIDER LOGIC
      else if (cmd.startsWith("G:")) {
        int ang = constrain(cmd.substring(2).toInt(), 0, 90);
        pwm.setPWM(CH_GRIPPER, 0, map(ang, 0, 90, GRIPPER_CLOSE_TICK, GRIPPER_OPEN_TICK));
      }
    }
  }
}
