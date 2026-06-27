"""
GitHub: https://github.com/Ledbelly2142/VL6180X/blob/master/vl6180x.py
Author: Ledbelly2142 (https://github.com/Ledbelly2142)
"""

import ustruct
import struct
import time
from machine import I2C, Pin

i2c_tof = I2C(0, sda=Pin(8), scl=Pin(9))
offsetVal = 35

class Sensor:
    def __init__(self, i2c, address=0x29):
        self.i2c_tof = i2c
        self._address = address
        self.default_settings()
        self.init()

    def myWrite16(self, register, regValue):
        """ write a byte to specified 16 bit register """
        return self.i2c_tof.writeto_mem(self._address, register, bytearray([regValue]), addrsize=16)

    def myRead16(self, register):
        """read 1 bit from 16 byte register"""
        value = int.from_bytes(self.i2c_tof.readfrom_mem(self._address, register, 1, addrsize=16),'big')
        return value & 0xFFFF

    def init(self):
        if self.myRead16(0x0016) != 1:
            raise RuntimeError("Failure reset")

        # Recommended setup from the datasheet
        self.myWrite16(0x0207, 0x01)
        self.myWrite16(0x0208, 0x01)
        self.myWrite16(0x0096, 0x00)
        self.myWrite16(0x0097, 0xfd)
        self.myWrite16(0x00e3, 0x00)
        self.myWrite16(0x00e4, 0x04)
        self.myWrite16(0x00e5, 0x02)
        self.myWrite16(0x00e6, 0x01)
        self.myWrite16(0x00e7, 0x03)
        self.myWrite16(0x00f5, 0x02)
        self.myWrite16(0x00d9, 0x05)
        self.myWrite16(0x00db, 0xce)
        self.myWrite16(0x00dc, 0x03)
        self.myWrite16(0x00dd, 0xf8)
        self.myWrite16(0x009f, 0x00)
        self.myWrite16(0x00a3, 0x3c)
        self.myWrite16(0x00b7, 0x00)
        self.myWrite16(0x00bb, 0x3c)
        self.myWrite16(0x00b2, 0x09)
        self.myWrite16(0x00ca, 0x09)
        self.myWrite16(0x0198, 0x01)
        self.myWrite16(0x01b0, 0x17)
        self.myWrite16(0x01ad, 0x00)
        self.myWrite16(0x00ff, 0x05)
        self.myWrite16(0x0100, 0x05)
        self.myWrite16(0x0199, 0x05)
        self.myWrite16(0x01a6, 0x1b)
        self.myWrite16(0x01ac, 0x3e)
        self.myWrite16(0x01a7, 0x1f)
        self.myWrite16(0x0030, 0x00)

    def default_settings(self):
        self.myWrite16(0x0011, 0x10)
        self.myWrite16(0x010A, 0x30)
        self.myWrite16(0x003f, 0x46)
        self.myWrite16(0x0031, 0xFF)
        self.myWrite16(0x0040, 0x63)
        self.myWrite16(0x002E, 0x01)
        self.myWrite16(0x0024, 100)
        self.myWrite16(0x001B, 0x09)
        self.myWrite16(0x003E, 0x0A)
        self.myWrite16(0x0014, 0x24)
        self.myWrite16(0x002D, 0x10)
        self.myWrite16(0x0022, 0x28)
        self.myWrite16(0x001C, 0x3F)
        self.myWrite16(0x0120, 0x01)

    def identify(self):
        return {
            'model': self.myRead16(0x0000),
            'revision': (self.myRead16(0x0001), self.myRead16(0x0002)),
            'module_revision': (self.myRead16(0x0003), self.myRead16(0x0004)),
            'date': self.myRead16(0x006),
            'time': self.myRead16(0x008),
        }

    def address(self, address=None):
        if address is None:
            return self._address
        if not 8 <= address <= 127:
            raise ValueError("Wrong address")
        self.myWrite16(0x0212, address)
        self._address = address

    def range(self):
        """Previne falhas elétricas do hardware (I2C OSError) e retorna None de forma segura"""
        try:
            self.myWrite16(0x0018, 0x01)  # Sysrange start
            
            # Timeout simples para evitar travamento em loops infinitos caso o I2C congele
            timeout = 50
            try:
                while (self.myRead16(0x004F) & 0x04) == 0:
                    time.sleep(0.005)
                    timeout -= 1
                    if timeout <= 0:
                        print("Aviso: Timeout de leitura do sensor ToF.")
                        return None
            except:
                print(f"erro de leitura do ToF")
                
            status = self.myRead16(0x004D) >> 4
            distancia_crua = self.myRead16(0x0062) 
            self.myWrite16(0x0015, 0x07)  # Clear Interrupt
            
            if status != 0:
                print(f"Erro interno do ToF! Código: {status}")
                return None 
                
            distancia_real = distancia_crua
            if distancia_real < 0:
                distancia_real = 0
                
            return (0 if ((distancia_real - offsetVal) < 0) else (distancia_real - offsetVal))
            
        except OSError:
            # Captura o erro EIO [Errno 5] físico sem derrubar o programa principal
            print("Alerta: Falha física instantânea de comunicação I2C com o ToF.")
            return None