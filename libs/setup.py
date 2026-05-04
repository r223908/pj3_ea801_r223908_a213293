import vl6180x, time, machine

i2c_tof = machine.I2C(1, sda=machine.Pin(2), scl=machine.Pin(3))

# 2. Inicializa o sensor
sensor_tof = vl6180x.Sensor(i2c_tof) # type: ignore