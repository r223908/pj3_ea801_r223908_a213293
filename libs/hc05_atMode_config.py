"""
Como usar:
1. Segurar botão da placa HC-05 (ao ligar a BitDogLab, o módulo vai piscar os LEDs a cada 2 segundos).
2. Inserir o cabo USB na entrada da BitDogLab.
3. No VSCode, selecionar este .py na árvore usar a opção "Run current file on Pico"
4. Testar interface com o comando "AT" --> Deve aparecer um "OK" onde estava o "AT".
5. Configurar usuário da placa:
    a. AT+NAME=....     --> digitar o nome do módulo; e.g.: AT+NAME=EA801_CVT
    b. AT+PSWD=xxxx     --> senha de 4 digitos = xxxx
    c. AT+CMODE=1       --> para se conectar com qualquer dispositivo através da senha
6. Desligar a placa e realizar pareamento.


A. Para mais comandos, ver /docs/datasheets/HC-05_ATCommandSet.pdf
"""


import machine
import sys
import uselect
import utime

# Configura a UART0 nos pinos 0 (TX) e 1 (RX) - Conector J2
# O baud rate de 38400 é o padrão de fábrica para o modo AT do HC-05
uart = machine.UART(0, baudrate=38400, tx=machine.Pin(0), rx=machine.Pin(1))

print("==================================")
print("     Terminal AT para HC-05       ")
print("==================================")
print("Digite 'AT' e pressione Enter.")
print("A resposta deve ser 'OK'.")
print("==================================")

# Configura a entrada do teclado (terminal USB) para não bloquear o código
teclado = uselect.poll()
teclado.register(sys.stdin, uselect.POLLIN)

# Envia um "AT" inicial de teste (igual ao seu código C++)
uart.write('AT\r\n')

while True:
    # 1. Se chegou algo do HC-05, imprime no terminal do PC
    if uart.any():
        resposta = uart.read()
        if resposta is not None:        # sem isso vai aparecer um erro no decode abaixo
            try:
                print(resposta.decode('utf-8'), end='')
            except UnicodeError:
                print(resposta) # Imprime cru se houver lixo na serial
            
    # 2. Se digitar algo no terminal do PC, 05envia para o HC-
    if teclado.poll(0):
        comando = sys.stdin.readline().strip() # Lê o que foi digitado
        if comando:
            # O HC-05 exige que os comandos AT terminem com Carriage Return e Line Feed (\r\n)
            uart.write(comando + '\r\n')
            
    utime.sleep(0.01) # Pequena pausa para não sobrecarregar o processador