#include "Sensor.h"
#include <Arduino.h>

#ifndef FLOWSENSOR_H
#define FLOWSENSOR_H

unsigned long time;
uint32_t timePoints[2];

void ISR_FlowSensor() {
  timePoints[0] = timePoints[1];
  timePoints[1] = millis();
}

class FlowSensor : public Sensor {
  private:
    float area;
  public:
    FlowSensor(String name, int pin) :
      Sensor(name, pin) {
      this->unit = "l/min";
      time = millis();
      digitalWrite(3, HIGH);
      attachInterrupt(1, ISR_FlowSensor, RISING);
      sei();
    }

    void init() {
    }

    float meassure() {
      value = 1.0 / (float)(timePoints[1] - timePoints[0]) * 1000.0;
      if (timePoints[0] == 0)
        value = 0;
      timePoints[0] = 0;
      timePoints[1] = 0;
      return value;
    }

    void setAsFlow(float area) {
    } //TODO rework
};

#endif

