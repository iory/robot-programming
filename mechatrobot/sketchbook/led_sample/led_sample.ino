void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // digital pinのモードを設定
}

void loop() {

  digitalWrite(LED_BUILTIN, HIGH); // digital pinをHIGH/LOWに切り替え
  delay(1000);           // sleep [msec]
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);

}
