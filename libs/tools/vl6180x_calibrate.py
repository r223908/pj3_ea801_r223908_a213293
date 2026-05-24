import machine
import utime
# IMPORTANTE: Você precisará subir um arquivo 'vl6180x.py' genérico de MicroPython na placa
import vl6180x 

"""
1 - Vin - VERMELHO (VM) <-- 3V3
2 - 2v8 - VERDE (VD)
3 - GND - PRETO (PT) <-- GND
4 - GPIO - AZUL (AZ)
5 - SHDN - ROXO (RX)
6 - SCL - CINZA (CZ) <-- GP9
7 - SDA - BRANCO (BR) <-- GP8
"""

# 1. Configura o I2C (Usando o GP8 e GP9 do cabo IDC como conversamos)
# O endereço I2C padrão do sensor é 0x29 e não pode ser alterado!
#i2c_tof = machine.I2C(1, sda=machine.Pin(2), scl=machine.Pin(3))

# 2. Inicializa o sensor
sensor = vl6180x.Sensor(vl6180x.i2c_tof)

# --- CONFIGURAÇÃO DA CALIBRAÇÃO ---
# Meça com uma régua e coloque a peça mecânica exatamente a esta distância:
DISTANCIA_REAL_MM = 0  

print("========================================")
print("   CALIBRAÇÃO DO SENSOR TOF VL6180X     ")
print("========================================")
print(f"1. Posicione a peça mecânica a exatos {DISTANCIA_REAL_MM} mm do sensor.")
print("2. Deixe suas mãos longe do sensor para não refletir a luz.")
print("Iniciando as leituras em 5 segundos...")
utime.sleep(5)

soma_leituras = 0
amostras = 30 # Vamos tirar uma média de 30 amostras para ter precisão matemática

print("\nColetando dados brutos...")
for i in range(amostras):
    # Lê a distância em milímetros
    leitura_atual = sensor.range() 
    soma_leituras = soma_leituras + leitura_atual # type: ignore
    
    print(f"Amostra {i+1}: {leitura_atual} mm")
    utime.sleep_ms(100)

# 3. Calcula o Offset
media_lida = soma_leituras / amostras
offset_calculado = DISTANCIA_REAL_MM - media_lida

print("\n========================================")
print("          RESULTADO DA CALIBRAÇÃO       ")
print("========================================")
print(f"Distância Real: {DISTANCIA_REAL_MM} mm")
print(f"Média Lida pelo Sensor: {media_lida:.2f} mm")
print(f"-> OFFSET A SER APLICADO: {offset_calculado:.2f} mm")
print("========================================")
print("Anote este valor de OFFSET!")