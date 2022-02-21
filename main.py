from dronekit import connect, VehicleMode
import time, json
from pm25 import PM25
from datetime import datetime

rx_pin = 20
reset_pin = 21
serial = '/dev/ttyS0'
output = '/home/pi/sensors.log'

print(f'Connecting to PM25 on pins {rx_pin}, {reset_pin}')
pm25 = PM25(rx_pin, reset_pin)

print("Connecting to vehicle on: %s" % (serial))
vehicle = connect(serial, wait_ready=True, baud=57600)

# def location_callback(self, attr_name, value):
#      print("Location (Global): ", value)

def startup():
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)
    # vehicle.add_attribute_listener('location.global_frame', location_callback)
    print("running...\n")

    
def log_sensors():
    location = vehicle.location.global_frame
    x = dict()
    x['time'] = datetime.utcnow().isoformat()
    x['lat'] = location.lat
    x['lon'] = location.lon
    x['alt'] = location.alt
    x['data'] = pm25.read()

    with open(output, 'a') as f:
        json.dump(x, f)
        f.write("\n")

    print(f"{x['lat']},{x['lon']},{x['alt']} PM10: {x['data']['pm10-std']} PM25: {x['data']['pm25-std']} PM100: {x['data']['pm100-std']}")


try:
    startup()
    
    while True:
        time.sleep(1)

        try:
            if vehicle.armed:
                log_sensors()
                
        except RuntimeError as e:
            print(f"Unable to read from sensor: {e}")
            continue


finally:
    pm25.stop()
    # vehicle.remove_message_listener('location.global_frame', location_callback)
    vehicle.close()
