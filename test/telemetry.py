from dronekit import connect, VehicleMode
import time

# Connect to the Vehicle.
connection_string = '/dev/ttyS0'
print("Connecting to vehicle on: %s" % (connection_string,))
vehicle = connect(connection_string, wait_ready=True, baud=57600)


def location_callback(self, attr_name, value):
     print("Location (Global): ", value)

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
    vehicle.add_attribute_listener('location.global_frame', location_callback)
    print("running...\n")
    
    while True:
        time.sleep(1)

finally:
    vehicle.remove_message_listener('location.global_frame', location_callback)
    vehicle.close()
