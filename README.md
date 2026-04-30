### EA801 - PROJETO 3

### Câmbio CVT (versão 2) com BitDogLab V7

**Autores:** 
- Raul Galdino Tancredo (RA: 223908 / [@r223908](https://github.com/r223908))
- Arthur Lucas Da Silva Nogueira (RA: 213293 / [@arthurnog](https://github.com/arthurnog)))

**Professor:** Eric Rohmer

* **Proposta de Projeto**: [Proposta em G-Docs](tbd) (acesso "Comentador" para UNICAMP)
* **Relatório de projeto**: [Relatório em G-Docs](tbd) (acesso "Comentador" para UNICAMP)
* **Demonstração do projeto no YouTube**: [Vídeo](tbd)

---
## ⚙️ DESCRIÇÃO DO SISTEMA (v2)
O sistema desenvolvido consiste na implementação de uma bancada de testes para um **Câmbio de Transmissão Continuamente Variável (CVT)** simulado, controlado remotamente via interface sem fio. O projeto utiliza a plataforma BitDogLab V7 como unidade central de processamento, integrando comunicação serial, controle de potência e telemetria.

O controle é dividido em dois eixos de atuação:
1. Eixo motor: Um motor de corrente contínua (DC), simulando a rotação do motor primário, controlado via PWM mas com a rotação travada em 100%.
2. Atuador do câmbio: Um segundo motor acoplado a um sistema de fuso (atuador linear), responsável por alterar a posição física da correia do câmbio CVT.

A interface homem-máquina (IHM) é realizada de forma remota através de um módulo Bluetooth (conectado à interface UART da placa) com a integração de um aplicativo no celular. O display OLED da placa é utilizado para exibir a telemetria em tempo real.



<figure align="center">
    <figcaption><i>Figura 1: Diagrama de blocos do projeto.</i></figcaption>
    <img src="/docs/images/blockDiag_v1.png" width="100%" style="border: 2px solid black; border-radius: 8px;" alt="Diagrama de blocos do projeto">
    </br>
</figure>

<figure align="center">
    <figcaption><i>Figura 2: Projeto em CAD 3D.</i></figcaption>
    <img src="/docs/images/cvt_cad_v1.png" width="45%" style="border: 2px solid black; border-radius: 8px;" alt="Equipamento montado">
</figure>

<figure align="center">
    <figcaption><i>Figura 3: Equipamento montado e testado.</i></figcaption>
    <img src="/docs/images/montagem/IMG-20260426-WA0001.jpeg" width="80%" style="border: 2px solid black; border-radius: 8px;" alt="Equipamento montado">
</figure>


---
## ❗REQUISITOS (in-work)
- 1x BitDogLab V7.
- 2x Ponte H L293D (CI) para ambos os motores.
- 1x Protoboard 400 pinos ou fazer toda a ligação na placa de fenolite com solda.
- Jumpers M-M e M-F.
- 1x Adaptador de 4 pilhas AA (6 Vcc para os motores e alimentação da placa).
- 4x pilhas AA (1,5 Vcc).
- Cabo micro USB (usar apenas para passar a programação, com as pilhas desconectadas).
- Módulo Bluetooth HC05.
- Anel o-ring ou elástico.
- Parafusos para montagem (alguns precisam ser colados na base)
    - 2x Parafuso ISO 4017 M4x20 (Eixos do cone de saída)
    - 1x Parafuso ISO 4017 M6x15 (Contra-eixo do cone principal)
    - 1x Parafuso ISO 4017 M6x60 (fuso do CVT)
    - 2x Porca ISO 4032 M6 (Espaçador no fuso do CVT e guia da polia)
    - 1x Arruela ISO 7093 Ø6 (Espaçador no fuso do CVT)
    - 4x Parafuso autoatarrachante 9/64"x1" (ou 1/8"x1" - Ø x Comprimento)
- Peças impressas em 3D
- Ambiente de desenvolvimento configurado para MicroPython.

---
## 🔧CONFIGURAÇÕES
- BitDogLab V7: Transferir os arquivos **main.py**, **setup.py** e **ssd1306.py** para a placa via USB.
- Ligação das pontes H e motores conforme **/docs/images/schematic_pj3.png**
- Módulo Bluetooth HC05 configurado com AT Mode usando **hc05_atMode_config.py**

---
## 📚 REFERÊNCIAS
1. Repositório BitDogLab V7: [Repositório no GitHub](https://gitlab.unicamp.br/fabiano/bitdoglab-v7)
2. Banco de Informação de Hardware: [BitDogLabV7_BIH](https://docs.google.com/document/d/13-68OqiU7ISE8U2KPRUXT2ISeBl3WPhXjGDFH52eWlU/edit?tab=t.0)
3. LEGO Continuous Variable Transmission (CVT) V3 [Link YouTube](https://www.youtube.com/watch?v=sa60egMprYc)
4. LEGO Simple CVT (Continuously Variable Transmission) [Link YouTube](https://www.youtube.com/watch?v=1y5fQr0dDVg)

---
## 📄LICENÇA
* Ver o arquivo `LICENSE`.

---
## 📂 ESTRUTURA DO PROJETO
``` text
├── .vscode/                        → Configurações para o ambiente de trabalho no VSCode
├── docs/                           → Documentação do projeto
│   ├── 1_datasheets/               → Folhas de dados dos equipamentos utilizados
│   ├── 2_images/                   → Imagens para relatórios e referências
│   ├── 3_mermaid-files/            → arquivos para gerar os diagramas de bloco e gantt
│   ├── 4_kicad-pj3/                → Projeto KiCad para a plaquinha shield
│   ├── 5_video/                    → Vídeo original
│   ├── 6_CAD-files/                → Arquivos .stl e PDF_3D da montagem
│   └── (...)                       → Proposta e relatório
├── libs/                           
│   └── (...)                       → Bibliotecas e arquivos de configuração
├── src/                            
│   └── main.py                     → Código-fonte
├── .micropico                      → Arquivo necessário para a extensão Pi PICO no VSCODE
├── LICENSE                         → Licença de uso do código
└── README.md                       → Resumo e estrutura do projeto
```
