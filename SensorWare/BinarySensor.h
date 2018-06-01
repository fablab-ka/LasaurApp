#include "Sensor.h"
#include <Arduino.h>

#ifndef BINARYSENSOR_H
#define BINARYSENSOR_H

class BinarySensor :  public Sensor {
  public:
    BinarySensor(String name, int pin) :
      Sensor(name, pin) {
      this->unit = "";
    }

    void init() {
      pinMode(pin, INPUT);
      digitalWrite(pin, HIGH);
    }

    float meassure() {
      return digitalRead(pin);
    }

    void setAsFlow(float area) {
    } //TODO rework
};

#endif

