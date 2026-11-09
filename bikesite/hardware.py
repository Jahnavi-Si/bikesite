"""Pretend hardware for the station (a "mock").

The website only talks to the `station` object at the bottom of this file.
Later, replace the insides of these methods with real Raspberry Pi code
(GPIO pins for the relay and lock motor driver, a sensor for battery level)
and the website code does not need to change.
"""
import time

CHARGE_RATE = 1.0  # battery percent gained per second (fast, so demos are quick)


class Station:
    def __init__(self):
        self.reset()

    def reset(self):
        self.user_id = None
        self.serial = None
        self.connected = False
        self.charging = False
        self.bike_locked = False
        self.charger_locked = False
        self.battery = 40.0  # fake starting battery level
        self.full_notice = False
        self._t = time.time()

    def _tick(self):
        """Update the fake battery based on how much time has passed."""
        now = time.time()
        if self.charging:
            self.battery = min(100.0, self.battery + (now - self._t) * CHARGE_RATE)
            if self.battery >= 100.0:
                self.charging = False  # stop when full
                self.full_notice = True
        self._t = now

    def connect(self, user_id, serial):
        self.reset()
        self.user_id, self.serial, self.connected = user_id, serial, True

    def disconnect(self):
        self.reset()

    def do(self, name):
        """Run one button action. Returns a message to show the user."""
        self._tick()
        if name == "start":
            if self.battery >= 100:
                return "Battery is already full."
            self.charging, self.full_notice = True, False
            return "Charging started."
        if name == "stop":
            self.charging = False
            return "Charging stopped."
        if name == "lock_bike":
            self.bike_locked = True
            return "Bike locked."
        if name == "unlock_bike":
            self.bike_locked = False
            return "Bike unlocked."
        if name == "lock_charger":
            self.charger_locked = True
            return "Charger locked."
        if name == "unlock_charger":
            msg = "Charger unlocked."
            if self.charging:
                self.charging = False
                msg = "Charging stopped and charger unlocked."
            self.charger_locked = False
            return msg
        return "Unknown action."

    def status(self):
        self._tick()
        secs = round((100 - self.battery) / CHARGE_RATE) if self.charging else None
        return {
            "serial": self.serial,
            "battery": round(self.battery),
            "charging": self.charging,
            "bike_locked": self.bike_locked,
            "charger_locked": self.charger_locked,
            "full": self.full_notice,
            "seconds_left": secs,
        }


station = Station()
