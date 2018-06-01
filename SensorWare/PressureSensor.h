#include "Sensor.h"
#include <Arduino.h>

#ifndef PRESSURESENSOR_H
#define PRESSURESENSOR_H

class PressureSensor : public Sensor {
  private:
    boolean isFlow;
    float area;
    float zero;
    float lastValues[10];
  public:
    PressureSensor(String name, int pin, float zero) :
      Sensor(name, pin) {
      isFlow = false;
      pinMode(pin, INPUT);
      digitalWrite(pin, LOW);
      this->zero = zero;
      this->unit = "Pa";
    }
    void setAsFlow(float area) {
      isFlow = true;
      this->area = area;
      this->unit = "m3/h";
    }

    void setAsDifferential() {
      isFlow = false;
      this->unit = "Pa";
    }

    void init() {
      float nzero = 0;
      for (int i = 0; i < 1000; i++)
        nzero += analogRead(pin);
      nzero /= 1000.0;
      nzero *= 5.0 / 1024.0;
      zero = nzero;
    }

    float meassure() {
      float value = 0;
      for (int i = 0; i < 1000; i++)
        value += analogRead(pin);
      value /= 1000.0;
      value *= 5.0 / 1024.0;
      value -= zero;
      value *= 1000;

      if (isFlow)
        value = sqrt(abs(value) * 2.0 / 1.2041) * area * 3600.0;

      return abs(value);
    }
};

#endif

