#ifndef SENSOR_H
#define SENSOR_H
#include <Arduino.h>

class Sensor {

  protected:
    int pin;
    int ledpin;
    float higher, lower, hysterese;
    boolean isInRange;
    virtual float meassure() = 0;
    boolean critical = true;

  public:
    String name;
    String unit;
    float value;
    Sensor() {
    }
    Sensor(String name, int pin) {
      this->name = name;
      this->pin = pin;
      this->ledpin = 13;
      this->isInRange = false;
      this->lower = 1000;
      this->higher = 0;
      this->hysterese = 0;
      this->critical = true;
    }

    void setBounds(float lower, float higher, float hysterese) {
      this->lower = lower;
      this->higher = higher;
      this->hysterese = hysterese;
    }

    void setNonCritical() {
      this->critical = false;
    }

    boolean isCritical() {
      return critical;
    }

    virtual void setAsFlow(float area) = 0; //fuck it

    virtual void init() = 0;

    String getString() {
      String out = "{'name':'";
      out += this->name;
      out += "', 'value':";
      char buff[8];
      dtostrf(this->value, 5, 2, buff);
      out += buff;
      out += ", 'unit':'";
      out += this->unit;
      out += "'}";
      return out;
    }

    boolean evaluate() {
      float value = meassure();
      this->value = value;
      if (isInRange) {
        if (value > (higher + hysterese) || value < (lower - hysterese)) {
          isInRange = false;
          digitalWrite(ledpin, HIGH);
        }
      } else {
        if (value > (lower + hysterese) && value < (higher - hysterese)) {
          isInRange = true;
          digitalWrite(ledpin, LOW);
        }

      }
      return isInRange;
    }
};

#endif


