from dronekit import connect, VehicleMode
import time, struct, pigpio
from pm25 import PM25

rx_pin = 20
reset_pin = 21
serial = '/dev/ttyS0'

print(f'Connecting to PM25 on pins {rx_pin}, {reset_pin}')
pm25 = PM25(rx_pin, reset_pin)

print("Connecting to vehicle on: %s" % (serial))
vehicle = connect(serial, wait_ready=True, baud=57600)

# def location_callback(self, attr_name, value):
#      print("Location (Global): ", value)

try:
    # Get some vehicle attributes (state)
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)

    # Add a callback `location_callback` for the `global_frame` attribute.
    # vehicle.add_attribute_listener('location.global_frame', location_callback)
    print("running...\n")
    
    while True:
        time.sleep(1)

        try:
            aqdata = pm25.read()
            location = vehicle.location.global_frame

            print(f'location: {location}')
            print(f'sensor: {aqdata}')
        except RuntimeError as e:
            print(f"Unable to read from sensor: {e}")
            continue


finally:
    pm25.stop()
    vehicle.remove_message_listener('location.global_frame', location_callback)
    vehicle.close()
    
