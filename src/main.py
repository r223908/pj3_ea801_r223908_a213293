from setup import *

# ==========================================
# FUNÇÕES DE HARDWARE (MOTORES E TELA)
# ==========================================

# Lida com as informações do display OLED
def printOled(velocidade, direcao, posicao_cvt, bt_conectado):
    texto_sentido = "Horario" if direcao == 1 else "Anti-Hor."  
    texto_sentido = "Parado" if velocidade == 0 else texto_sentido
    texto_bt = "ON" if bt_conectado == 1 else "OFF"
    display.fill(0)
    display.text("Cambio CVT", 20, 0)
    display.text("-" * 16, 0, 10)
    display.text(f"Motor: {texto_sentido}", 0, 25)
    display.text(f"Pos. CVT: {posicao_cvt}%", 0, 40)
    display.text(f"Bluetooth: {texto_bt}", 0, 55)
    display.show()

#controle do motor principal, lidando com a velocidade (mantida em 100%) e sentido de giro
def controlar_motor_principal(velocidade_percentual, direcao, fazer_rampa=False):
    # verificação se recebeu o comando para inverter o sentido do motor ou parar
    # nos dois casos tem rampa de variação de velocidade para não ter um solavanco nos componentes mecânicos
    if fazer_rampa and velocidade_percentual > 0:
        passos = 10 
        tempo_por_passo = (TEMPO_RAMPA_MS / 2000) / passos 
        passo_pwm = max(1, velocidade_percentual // passos)
        for v in range(velocidade_percentual, -1, -passo_pwm):
            Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
            utime.sleep(tempo_por_passo)
        Mprincipal_DIR1.value(0)
        Mprincipal_DIR2.value(0)
        Mprincipal_PWM.duty_u16(0)
        utime.sleep(0.05) 
        if direcao == 1:                # a mudança de direção pode ser feita na inversão dos fios de alimentação do motor 
            Mprincipal_DIR1.value(1)
            Mprincipal_DIR2.value(0)
        else:
            Mprincipal_DIR1.value(0)
            Mprincipal_DIR2.value(1)
        for v in range(0, velocidade_percentual + 1, passo_pwm):
            Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
            utime.sleep(tempo_por_passo)
        Mprincipal_PWM.duty_u16(int((velocidade_percentual / 100) * 65535))
    else:           # controle normal, apenas ocorre se recebe algum comando via Bluetooth
        if velocidade_percentual > 0:
            if direcao == 1:
                Mprincipal_DIR1.value(1)
                Mprincipal_DIR2.value(0)
            else:
                Mprincipal_DIR1.value(0)
                Mprincipal_DIR2.value(1)
        else:
            Mprincipal_DIR1.value(0)
            Mprincipal_DIR2.value(0)
        Mprincipal_PWM.duty_u16(int((velocidade_percentual / 100) * 65535))

# movimentação do câmbio, dependendo do sentido que ele precisar girar
# velocidade também sempre em 100%
def iniciar_movimento_cvt(direcao):     
    if direcao == 1:            
        Mcambio_DIR1.value(1)
        Mcambio_DIR2.value(0)
    elif direcao == -1:
        Mcambio_DIR1.value(0)
        Mcambio_DIR2.value(1)
    else:
        return 
    Mcambio_PWM.duty_u16(65535) 

# ==========================================
# Função de Interrupção dos Botões
# ==========================================
def trata_interrupcao_botao(pino):
    global cor_travada, ultimo_tempo_btn
    tempo_atual = utime.ticks_ms()
    if utime.ticks_diff(tempo_atual, ultimo_tempo_btn) > 200:
        if pino == botao_a:
            cor_travada = corVermelha
        elif pino == botao_b:
            cor_travada = corAzul
        elif pino == botao_c:
            cor_travada = corVerde
        ultimo_tempo_btn = tempo_atual

botao_a.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_b.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_c.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)

# ==========================================
# INICIALIZAÇÃO E LOOP PRINCIPAL
# ==========================================
ultimo_tempo_pisca = utime.ticks_ms()
ultimo_tempo_oled = utime.ticks_ms()

# inicializacao dos motores
velocidade_atual = 0
direcao_motor = 1 
posicao_cvt = 0  

# VARIÁVEIS PARA O CVT ASSÍNCRONO
cvt_em_movimento = False
ultimo_tempo_cvt = 0

# desliga a matriz de LEDs
for i in range(NUM_LEDS):
    np[i] = (0, 0, 0)
np.write()

print("Aguardando comandos Bluetooth...")

while True:
    tempo_atual = utime.ticks_ms()

    # 1. ATUALIZAÇÃO DO DISPLAY OLED
    if utime.ticks_diff(tempo_atual, ultimo_tempo_oled) >= ATT_DISPLAY_MS:
        estado_conexao = status_bt.value()
        if estado_conexao == 0 and velocidade_atual > 0:
            passos = 10                                             
            tempo_por_passo = (TEMPO_RAMPA_MS / 2000) / passos
            passo_pwm = max(1, velocidade_atual // passos)
            for v in range(velocidade_atual, -1, -passo_pwm):
                Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
                utime.sleep(tempo_por_passo)
            velocidade_atual = 0                                    
            controlar_motor_principal(0, direcao_motor)
        printOled(velocidade_atual, direcao_motor, posicao_cvt, estado_conexao)
        ultimo_tempo_oled = tempo_atual

    # 2. LEITURA DE COMANDOS BLUETOOTH
    if bluetooth.any():
        try:
            dados_brutos = bluetooth.read()
            if dados_brutos is not None:
                comando = dados_brutos.decode('utf-8').strip().upper()

                if comando:
                    led_azul.value(1) 
                    
                    if comando == startDir:         # ligar motor principal
                        velocidade_atual = 100
                        controlar_motor_principal(velocidade_atual, direcao_motor)
                        
                    elif comando == frontDir:       # sentido horário
                        deve_fazer_rampa = (direcao_motor == -1 and velocidade_atual > 0)
                        direcao_motor = 1
                        controlar_motor_principal(velocidade_atual, direcao_motor, deve_fazer_rampa)
                        
                    elif comando == backDir:        # sentido anti-horário
                        deve_fazer_rampa = (direcao_motor == 1 and velocidade_atual > 0)
                        direcao_motor = -1
                        controlar_motor_principal(velocidade_atual, direcao_motor, deve_fazer_rampa)
                        
                    elif comando == triangleDir:    # sobe marcha; motor CVT
                        # Adicionada a regra: "not cvt_em_movimento" para evitar acúmulo de comandos
                        if posicao_cvt < 100 and not cvt_em_movimento: 
                            iniciar_movimento_cvt(1)
                            cvt_em_movimento = True
                            ultimo_tempo_cvt = tempo_atual # Marca a hora que ligou
                            posicao_cvt = min(100, posicao_cvt + 10)                      
                            
                    elif comando == crossDir:       # desce marcha; motor CVT
                        if posicao_cvt > 0 and not cvt_em_movimento: 
                            iniciar_movimento_cvt(-1)
                            cvt_em_movimento = True
                            ultimo_tempo_cvt = tempo_atual # Marca a hora que ligou
                            posicao_cvt = max(0, posicao_cvt - 10)
                        
                    elif comando == pauseDir:       # para o motor principal
                        velocidade_atual = 0
                        controlar_motor_principal(0, direcao_motor)
                        # Parada de emergência para o Câmbio também!
                        Mcambio_DIR1.value(0)
                        Mcambio_DIR2.value(0)
                        Mcambio_PWM.duty_u16(0)
                        cvt_em_movimento = False
                    
                    led_azul.value(0)
        except UnicodeError:
            pass 

    # 3. VERIFICADOR ASSÍNCRONO DO MOTOR CVT
    # Fica verificando se o tempo do motor do câmbio já deu
    if cvt_em_movimento:
        if utime.ticks_diff(tempo_atual, ultimo_tempo_cvt) >= TEMPO_PASSO_CVT_MS:
            # O tempo do passo (ex: 2s) acabou! Desliga o motor do CVT.
            Mcambio_DIR1.value(0)
            Mcambio_DIR2.value(0)
            Mcambio_PWM.duty_u16(0)
            cvt_em_movimento = False

    # 4. ANIMAÇÃO DA MATRIZ DE LEDS PARA REPLICAR O SENTIDO DE GIRO DO MOTOR PRINCIPAL
    np.fill((0, 0, 0))
    if posicao_cvt == 0 or velocidade_atual == 0:
        np[LED_MEIO] = cor_travada 
    else:
        leds_por_segundo = (posicao_cvt / 100) * MAX_LEDS_POR_SEGUNDO
        leds_por_segundo = .1 if leds_por_segundo < 0.1 else leds_por_segundo
        intervalo_ms = int(1000 / leds_por_segundo)
        
        if utime.ticks_diff(tempo_atual, ultimo_tempo_pisca) >= intervalo_ms:    
            if direcao_motor == 1:
                indice_frame = (indice_frame + 1) % len(FRAMES_MOTOR)
            else:
                indice_frame = (indice_frame - 1) % len(FRAMES_MOTOR)
                
            ultimo_tempo_pisca = tempo_atual
            
        for led in FRAMES_MOTOR[indice_frame]:
            np[led] = cor_travada
    np.write()
    
    utime.sleep(0.01)