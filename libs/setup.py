import vl6180x, time, machine

i2c_tof = vl6180x.i2c_tof

# 2. Inicializa o sensor
sensor_tof = vl6180x.Sensor(i2c_tof) # type: ignore