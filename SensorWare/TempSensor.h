#include "Sensor.h"
#include <Arduino.h>

#ifndef TEMPSENSOR_H
#define TEMPSENSOR_H

#define STEINHART_A 0.001125308852122
#define STEINHART_B 0.000234711863267
#define STEINHART_C 0.000000085663516

class TempSensor :  public Sensor {
  public:
    int values[10];
    TempSensor(String name, int pin) :
      Sensor(name, pin) {
        this->unit = "C";
    }

    void init() {
    }

    float meassure() {
      int meass = 0;
      for(int i = 0; i < 16; i++)
        meass += analogRead(pin);
      meass /= 16;
      float value =  (float)meass * 5.0 / 1024.0; //U [V]
      value = (5.0 * 10.0e3) / value - 10.0e3; //R [ohm]
      value = 1.0 / (STEINHART_A + STEINHART_B * log(value) + STEINHART_C * log(value) * log(value) * log(value));
      value -= 273.15;
      return value;
    }

    void setAsFlow(float area) {
    } //TODO rework
};

#endif

