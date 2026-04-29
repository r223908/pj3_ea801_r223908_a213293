"""
1. Arquivo de uso geral para mapear o que chega de informação na UART com o módulo bluetooth.
2. Utilizado para reconhecer os comandos e configurar o setup.py deste projeto.
3. O que a placa receber será exibido no Terminal do VSCode.
"""

import machine
import utime

# Inicializa a UART0 para o Bluetooth (Pinos do Conector J2)
# Baud rate 9600 é o padrão para comunicação (modo transparente)
bluetooth = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# Configura o LED Azul da placa (GPIO 12) para feedback visual
# O BIH diz que é cátodo comum, então '1' liga e '0' desliga
led_azul = machine.Pin(12, machine.Pin.OUT)
led_azul.value(0) # Inicia desligado

print("=======================================")
print("   Monitor Bluetooth - Projeto CVT     ")
print("=======================================")
print("Aguardando conexão e comandos do celular...")

while True:
    # Verifica se há dados no buffer do Bluetooth
    if bluetooth.any():
        # Lê os dados brutos recebidos
        dados_brutos = bluetooth.read()
        
        try:
            # Tenta decodificar de bytes para texto (String)
            # O .strip() remove espaços em branco e quebras de linha (\r, \n) das pontas
            comando = dados_brutos.decode('utf-8').strip() # type: ignore
            
            # Só imprime se realmente tiver algo após o strip
            if comando:
                print(f"Comando recebido em Texto: '{comando}'")
                
                # Envia um "eco" de volta para o celular (aparece na tela do app)
                bluetooth.write(f"Placa recebeu: {comando}\n")
                
                # Pisca o LED Azul rapidamente
                led_azul.value(1)
                utime.sleep(0.1)
                led_azul.value(0)
                
        except UnicodeError:
            # Se o aplicativo do celular mandar dados hexadecimais puros 
            # (comum em apps de controle tipo "joystick"), a decodificação de texto falha.
            # Nesse caso, imprimimos os bytes puros para você poder mapear.
            print(f"Dados recebidos em Bytes (Hex): {dados_brutos}")

    # Pausa curta para não travar a CPU no loop infinito
    utime.sleep(0.05)