"""
    arquivo de importação de bibliotecas, configuração de interfaces e variáveis
"""

from machine import Pin, ADC, I2C, PWM
import neopixel, utime, machine, time
import ssd1306, vl6180x

# 1. Variáveis Globais e Cores
corVermelha = (20, 0, 0)
corAzul = (0, 0, 20)
corVerde = (0, 20, 0)
cor_travada = corVermelha  # Motor começa vermelho
ultimo_tempo_btn = 0
ultimo_tempo_pisca = utime.ticks_ms()
indice_frame = 0

# 2. Variáveis de Controle do Motor Virtual
CENTRO_JOYSTICK = 32768
ZONA_MORTA = 4000
MAX_LEDS_POR_SEGUNDO = 100  # Ajuste a velocidade máxima aqui

# 3. Configuração dos Botões (A, B e C)
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)
botao_c = Pin(10, Pin.IN, Pin.PULL_UP)

# 4. Configuração do Joystick
joystick_x = ADC(Pin(27))
joystick_y = ADC(Pin(26))
joystick_sw = Pin(22, Pin.IN, Pin.PULL_UP)

# 5. Configuração do Display OLED (SSD1306)
# Usando os pinos I2C0 da BitDogLab V7 (SDA=2, SCL=3)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
display.fill(0)
display.show()
ATT_DISPLAY_MS = 100

# 6. Configuração da Matriz de LEDs
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)
LED_MEIO = 12
# Buffer circular da animação do motor
FRAMES_MOTOR = [[14, 13], [15, 16], [16, 24], [16, 23], [17, 22],
                [18, 21], [18, 20], [18, 19], [10, 11], [8, 9],
                [0, 8], [1, 8], [2, 7], [3, 6], [4, 6], [5, 6] ]

# 7. Configuração dos controles de Motor (Ponte H) e PWM da placa
# IMPORTANTE: GPIO 0 e 1 são do Bluetooth. Vamos usar os pinos livres do conector IDC.

# Motor Principal (Eixo) - Assumindo ligação no lado Esquerdo do L293D (Pinos 1, 2 e 7)
Mprincipal_DIR1 = Pin(16, Pin.OUT)
Mprincipal_DIR2 = Pin(17, Pin.OUT)
Mprincipal_PWM  = PWM(Pin(18))       # GP28 vai no pino 1 (EN1,2) do L293D
Mprincipal_PWM.freq(1000)
Mprincipal_PWM.duty_u16(0)
TEMPO_RAMPA_MS = 1000

# Motor Câmbio (Atuador CVT) - EXATAMENTE COMO NO SEU ESQUEMÁTICO (Lado Direito)
Mcambio_DIR1 = Pin(19, Pin.OUT)      # GP18 (Fio Roxo) vai no IN3
Mcambio_DIR2 = Pin(20, Pin.OUT)      # GP20 (Fio Branco) vai no IN4
Mcambio_PWM  = PWM(Pin(28))          # GP19 (Fio Cinza) vai no EN3,4 (Enable/PWM)
Mcambio_PWM.freq(1000)
Mcambio_PWM.duty_u16(0)
TEMPO_PASSO_CVT_MS = 5000  # 2000 ms = 2 segundos

# 8. Configura o LED Azul da placa (GPIO 12) para feedback visual
led_azul = machine.Pin(12, machine.Pin.OUT)
led_azul.value(0) # Inicia desligado

# 9. Inicializa a UART0 para o Bluetooth (Pinos do Conector J2)
bluetooth = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))
status_bt = machine.Pin(4, machine.Pin.IN)      # Pino que vai ler o pino 'STATE' do módulo Bluetooth

# 10. Mapeamento das entradas bluetooth
outButtonDir = '0'
frontDir = 'F'
backDir = 'B'
rightDir = 'R'
leftDir = 'L'
triangleDir = 'T'
circleDir = 'C'
squareDir = 'S'
crossDir = 'X'
startDir = 'A'
pauseDir = 'P'

# 11. Inicializa o sensor
#i2c_tof = I2C(0, sda=Pin(8), scl=Pin(9)) #esta declaracao já está na biblioteca do sensor ToF
i2c_tof = vl6180x.i2c_tof
sensor_tof = vl6180x.Sensor(i2c_tof) # type: ignore
