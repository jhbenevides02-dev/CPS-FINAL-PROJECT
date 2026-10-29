/*
  connection_test.ino: Part 4 of the CPS connection test (test sketch only).

  Bridge -> USB serial -> this Arduino (Nano Every)
  Expected: a line "1" turns the LED on and replies "ACK 1".
            No message for 1000 ms turns the LED off.
*/
#define ELAPSE_TIME 1000
int handClass = 0;
unsigned long lastMessageTime = 0;


void setup() {

  Serial.begin (115200);
  Serial.setTimeout(50);          // Prevent blocking with ELAPSE_TIME
  pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  handClass=readWekiClass();

  // turn on LED when message is 1
  if (handClass ==1){
    lastMessageTime = millis();
    digitalWrite(LED_BUILTIN,HIGH);
    Serial.println("ACK 1");

  }
  else 
  {
    if ((millis()-lastMessageTime) > ELAPSE_TIME){
      digitalWrite(LED_BUILTIN,LOW);
      //Serial.println("No Message");
    }
  }
  
}

int readWekiClass(){
  // Variables definition
  int hand_class = 0;             // Variable to return. 0 when there's no message
  String hand_class_string = "";  // String message from Python bridge
  
  if (Serial.available()>0){
    
    hand_class_string = Serial.readStringUntil('\n');
    hand_class = hand_class_string.toInt();
  
  }

  return hand_class;
}
