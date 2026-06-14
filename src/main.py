from setup import *

# VARIÁVEIS PARA O CVT ASSÍNCRONO BASEADO EM DISTÂNCIA
cvt_em_movimento = False
direcao_cvt = 0        # 1 avança (diminui mm), -1 recua (aumenta mm)
alvo_tof_mm = 0.0      # Distância que queremos atingir
janela_leituras = []   # Buffer para a Média Móvel
TAMANHO_JANELA = 30     # Média das últimas 15 leituras
PASSO_MM = 4.0         # Quantos mm o câmbio anda por vez
MAX_DIST_MM = 24.0     # Fundo do câmbio (0%)
MIN_DIST_MM = 1.0      # Batente do câmbio (100%)


# ==========================================
# FUNÇÕES DE HARDWARE (MOTORES, TELA E SENSOR)
# ==========================================

# MÉTODO DE LEITURA E SINCRONIZAÇÃO DO SENSOR TOF
def sincronizar_posicao_cvt():
    global posicao_cvt
    print("Sincronizando posição atual do sensor ToF...")
    leituras_locais = []
    
    # Coleta 10 amostras rápidas para ignorar ruídos de leitura única
    for _ in range(10):
        leitura = sensor_tof.range()
        if leitura > 0: # type: ignore
            leituras_locais.append(leitura)
        utime.sleep(0.01)

    if len(leituras_locais) > 0:
        distancia_calculada = sum(leituras_locais) / len(leituras_locais)
    else:
        distancia_calculada = MAX_DIST_MM # Segurança

    # Trava dentro dos limites físicos do projeto
    distancia_calculada = max(MIN_DIST_MM, min(MAX_DIST_MM, distancia_calculada))

    # Atualiza a variável global de porcentagem
    porcentagem_calculada = ((MAX_DIST_MM - distancia_calculada) / (MAX_DIST_MM - MIN_DIST_MM)) * 100
    posicao_cvt = max(0, min(100, int(porcentagem_calculada)))
    
    print(f"Posição Sincronizada: {distancia_calculada:.1f} mm ({posicao_cvt}%)")
    return distancia_calculada

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

# Controle do motor principal
def controlar_motor_principal(velocidade_percentual, direcao, fazer_rampa=False):
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
        if direcao == 1:
            Mprincipal_DIR1.value(1)
            Mprincipal_DIR2.value(0)
        else:
            Mprincipal_DIR1.value(0)
            Mprincipal_DIR2.value(1)
        for v in range(0, velocidade_percentual + 1, passo_pwm):
            Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
            utime.sleep(tempo_por_passo)
        Mprincipal_PWM.duty_u16(int((velocidade_percentual / 100) * 65535))
    else:
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

# Movimentação do câmbio, velocidade sempre em 100%
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

# VARIÁVEIS DE CONTROLE DOS BOTÕES FÍSICOS
flag_homing = False
flag_cancelar = False

# ==========================================
# Função de Interrupção dos Botões
# ==========================================
def trata_interrupcao_botao(pino):
    global cor_travada, ultimo_tempo_btn, flag_homing, flag_cancelar
    tempo_atual = utime.ticks_ms()
    
    if utime.ticks_diff(tempo_atual, ultimo_tempo_btn) > 200:
        if pino == botao_a:
            cor_travada = corVermelha
            flag_homing = True      # Solicita o Homing (Voltar a 0%)
        elif pino == botao_b:
            cor_travada = corAzul
        elif pino == botao_c:
            cor_travada = corVerde
            flag_cancelar = True    # Solicita a Parada Total (E-Stop)
            
        ultimo_tempo_btn = tempo_atual

botao_a.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_b.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_c.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)

# ==========================================
# INICIALIZAÇÃO E LOOP PRINCIPAL
# ==========================================
ultimo_tempo_pisca = utime.ticks_ms()
ultimo_tempo_oled = utime.ticks_ms()

velocidade_atual = 0
direcao_motor = 1   

# --- CHAMADA DO MÉTODO ANTES DO WHILE (POSIÇÃO INICIAL) ---
distancia_inicial = sincronizar_posicao_cvt()
# ----------------------------------------------------------

cvt_em_movimento = False
ultimo_tempo_cvt = 0

for i in range(NUM_LEDS):
    np[i] = (0, 0, 0)
np.write()

print("Aguardando comandos Bluetooth...")

while True:
    tempo_atual = utime.ticks_ms()

    # ===================================================
    # AÇÃO DE EMERGÊNCIA / CANCELAR (BOTÃO C)
    # ===================================================
    if flag_cancelar:
        flag_cancelar = False
        velocidade_atual = 0
        controlar_motor_principal(0, direcao_motor)
        
        Mcambio_DIR1.value(0)
        Mcambio_DIR2.value(0)
        Mcambio_PWM.duty_u16(0)
        cvt_em_movimento = False
        
        print("BOTAO C: Parada de Emergencia Acionada!")

    # ===================================================
    # AÇÃO DE HOMING / RETORNO À BASE (BOTÃO A)
    # ===================================================
    if flag_homing:
        flag_homing = False
        if not cvt_em_movimento:
            alvo_tof_mm = MAX_DIST_MM
            direcao_cvt = -1
            
            # --- CHAMADA DO MÉTODO DURANTE O FUNCIONAMENTO ---
            # Zera o passado e pega a posição exata de agora de forma estável
            leitura_estavel = sincronizar_posicao_cvt()
            
            # Inicializa a janela com o valor atualizado e limpo
            janela_leituras = [leitura_estavel] * TAMANHO_JANELA
            
            # Dá a partida física no motor para o retorno
            iniciar_movimento_cvt(direcao_cvt)
            cvt_em_movimento = True
            print(f"BOTAO A: Homing iniciado a partir de {leitura_estavel:.1f} mm...")

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
                    
                    if comando == startDir:
                        velocidade_atual = 100
                        controlar_motor_principal(velocidade_atual, direcao_motor)
                        
                    elif comando == frontDir:
                        deve_fazer_rampa = (direcao_motor == -1 and velocidade_atual > 0)
                        direcao_motor = 1
                        controlar_motor_principal(velocidade_atual, direcao_motor, deve_fazer_rampa)
                        
                    elif comando == backDir:
                        deve_fazer_rampa = (direcao_motor == 1 and velocidade_atual > 0)
                        direcao_motor = -1
                        controlar_motor_principal(velocidade_atual, direcao_motor, deve_fazer_rampa)
                        
                    elif comando == triangleDir:    # Sobe marcha (Avança / Diminui mm)
                        if not cvt_em_movimento:
                            leitura_atual = sensor_tof.range()
                            if leitura_atual > MIN_DIST_MM: # type: ignore
                                alvo_tof_mm = max(MIN_DIST_MM, leitura_atual - PASSO_MM) # type: ignore
                                direcao_cvt = 1
                                iniciar_movimento_cvt(direcao_cvt)
                                cvt_em_movimento = True
                                janela_leituras = [leitura_atual] * TAMANHO_JANELA 

                    elif comando == crossDir:       # Desce marcha (Recua / Aumenta mm)
                        if not cvt_em_movimento: 
                            leitura_atual = sensor_tof.range()
                            if leitura_atual < MAX_DIST_MM: # type: ignore
                                alvo_tof_mm = min(MAX_DIST_MM, leitura_atual + PASSO_MM) # type: ignore
                                direcao_cvt = -1
                                iniciar_movimento_cvt(direcao_cvt)
                                cvt_em_movimento = True
                                janela_leituras = [leitura_atual] * TAMANHO_JANELA
                        
                    elif comando == pauseDir:
                        velocidade_atual = 0
                        controlar_motor_principal(0, direcao_motor)
                        Mcambio_DIR1.value(0)
                        Mcambio_DIR2.value(0)
                        Mcambio_PWM.duty_u16(0)
                        cvt_em_movimento = False
                    
                    led_azul.value(0)
        except UnicodeError:
            pass 

    # 3. VERIFICADOR ASSÍNCRONO DO MOTOR CVT (MÉDIA MÓVEL COM TRAVA PARA 0MM)
    if cvt_em_movimento:
        nova_leitura = sensor_tof.range()
        chegou_no_alvo = False
        
        # --- FILTRO INTELIGENTE E ANTITRAVAMENTO ---
        if nova_leitura == 0:
            if direcao_cvt == 1 and len(janela_leituras) > 0 and janela_leituras[-1] <= (MIN_DIST_MM + 3.0):
                chegou_no_alvo = True
                nova_leitura = MIN_DIST_MM
                print("Seguranca: Sensor detectou colisao/fim de curso em 0mm!")
            else:
                nova_leitura = janela_leituras[-1] if len(janela_leituras) > 0 else MAX_DIST_MM
        elif nova_leitura > 50:  # type: ignore
            nova_leitura = janela_leituras[-1] if len(janela_leituras) > 0 else MAX_DIST_MM
            
        janela_leituras.pop(0)
        janela_leituras.append(nova_leitura) # type: ignore
        
        media_atual = sum(janela_leituras) / TAMANHO_JANELA # type: ignore
        
        porcentagem = ((MAX_DIST_MM - media_atual) / (MAX_DIST_MM - MIN_DIST_MM)) * 100
        posicao_cvt = max(0, min(100, int(porcentagem)))
        
        # 1. Validação de Alvo
        if direcao_cvt == 1 and media_atual <= alvo_tof_mm:
            chegou_no_alvo = True
        elif direcao_cvt == -1 and media_atual >= (alvo_tof_mm - 0.5):
            chegou_no_alvo = True

        # 2. Trava de Segurança dos Batentes Físicos (Baseado na Média)
        if media_atual <= MIN_DIST_MM and direcao_cvt == 1:
            chegou_no_alvo = True
            print("Seguranca: Batente Minimo atingido pela media!")
        elif media_atual >= MAX_DIST_MM and direcao_cvt == -1:
            chegou_no_alvo = True
            print("Seguranca: Batente Maximo atingido pela media!")

        # 3. Execução Correta da Parada
        if chegou_no_alvo:
            Mcambio_DIR1.value(0)
            Mcambio_DIR2.value(0)
            Mcambio_PWM.duty_u16(0)
            cvt_em_movimento = False
            
            if direcao_cvt == -1 and media_atual >= (MAX_DIST_MM - 1.0):
                posicao_cvt = 0
            print(f"Cambio Parado. Posicao Final: {posicao_cvt}% ({media_atual:.1f} mm)")
    
    utime.sleep(0.01)