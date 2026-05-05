### EA801 - PROJETO 3

### Câmbio CVT (v2) com BitDogLab V7

**Autores:** 
- Raul Galdino Tancredo (RA: 223908 / [@r223908](https://github.com/r223908))
- Arthur Lucas Da Silva Nogueira (RA: 213293 / [@arthurnog](https://github.com/arthurnog)))

**Professor:** Eric Rohmer

* **Proposta de Projeto**: [Proposta em G-Docs](https://docs.google.com/document/d/12xUf4pp4VCcdJPwbZHKw6q6G0AQpYL8BC8JdEnKDbEA/edit?usp=sharing) (acesso "Comentador" para UNICAMP)
* **Relatório de projeto (in-work)**: [Relatório em G-Docs](https://docs.google.com/document/d/11B9UFEimS15q4Ivua8mCu4cjH7NtBMuLyvma5xU35qU/edit?usp=sharing) (acesso "Comentador" para UNICAMP)
* **Demonstração do projeto no YouTube (in-work)**: [Vídeo](tbd)

---
## ⚙️ DESCRIÇÃO DO SISTEMA (v2)
O sistema desenvolvido consiste na implementação de uma bancada de testes para um **Câmbio de Transmissão Continuamente Variável (CVT)** simulado, controlado remotamente via interface sem fio. O projeto utiliza a plataforma BitDogLab V7 como unidade central de processamento, integrando comunicação serial, controle de potência e telemetria. O controle é dividido em dois eixos de atuação:
1. Eixo motor: Um motor de corrente contínua (DC), simulando a rotação do motor primário, controlado via PWM mas com a rotação travada em 100%.
2. Atuador do câmbio: Um segundo motor acoplado a um sistema de fuso (atuador linear), responsável por alterar a posição física da correia do câmbio CVT.

A interface homem-máquina (IHM) é realizada de forma remota através de um módulo Bluetooth (conectado à interface UART da placa) com a integração de um aplicativo no celular. O display OLED da placa é utilizado para exibir a telemetria em tempo real.

A realimentação da posição do atuador do CVT é realizada por meio de um sensor de distância óptico Time of Flight (ToF) VL6180X. Cabe ressaltar que o atual protótipo apresenta diversas otimizações mecânicas e elétricas em relação ao projeto original desenvolvido na etapa anterior da disciplina (PJ2).

<figure align="center">
    <figcaption><i>Figura 1: Diagrama de blocos do projeto.</i></figcaption>
    <img src="/docs/2_images/blockDiag_pj3_v0.png" width="70%" style="border: 2px solid black; border-radius: 8px;" alt="Diagrama de blocos do projeto">
    </br>
</figure>

<figure align="center">
    <figcaption>
        <i>Figura 2: Projeto em CAD 3D (nova versão - preliminar).</i>
    </figcaption>
    <table align="center">
    <tr>
    <td align="center">
        <img src="/docs/2_images/cvt_cad-1_pj3_v0.png" width="90%" style="border: 2px solid black; border-radius: 8px;" alt="Equipamento montado"><br>
    </td>
    <td align="center">
        <img src="/docs/2_images/cvt_cad-2_pj3_v0.png" width="100%" style="border: 2px solid black; border-radius: 8px;" alt="Outra Imagem"><br>
    </td>
    </tr>
</table>
    <figcaption>
        PDF 3D (abrir com Foxit ou Adobe): <a href="https://github.com/r223908/pj3_ea801_r223908_a213293/blob/main/docs/6_CAD-files/ea801_pj3_cvt_pdf3D.PDF">/docs/6_CAD-files/ea801_pj3_cvt_pdf3D</a></i>
    </figcaption>
</figure>


---
## ❗REQUISITOS (in-work)
- 1x BitDogLab V7.
- 1x Ponte H L293D (CI) para ambos os motores.
- 1x Sensor ToF VL6180X
- Placa de fenolite para a shield da BitDogLab
- Jumpers M-M e M-F.
- 3x pilhas 18650: 2x para os motores e 1x para a placa
- Cabo micro USB (usar apenas para passar a programação, com as pilhas desconectadas).
- Módulo Bluetooth HC-05.
- Anel o-ring ou elástico para o câmbio.
- Elementos de fixação
    - 1x Parafuso ISO 4017 M6x15 (Contra-eixo do cone principal)
    - 1x Parafuso ISO 4017 M6x60 (fuso do CVT)
    - 2x Porca ISO 4032 M6 (Espaçador no fuso do CVT e guia da polia)
    - 1x Arruela ISO 7093 Ø6 (Espaçador no fuso do CVT)
    - 4x Parafuso auto atarrachante 9/64"x1" (ou 1/8"x1" - Ø x Comprimento)
- Peças impressas em 3D
- Ambiente de desenvolvimento configurado para MicroPython.

---
## 🔧CONFIGURAÇÕES
- BitDogLab V7: Transferir os arquivos **main.py**, **setup.py**, **vl6180x.py** e **ssd1306.py** para a placa via USB.
- Ligação das pontes H e motores conforme **/docs/images/schematic_pj3.png**
- Módulo Bluetooth HC05 configurado com AT Mode usando **hc05_atMode_config.py**
- Sensor VL6180X calibrado conforme **/libs/tools/vl6180x_calibrate**

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
│   ├── 1_folhas-de-dados/          → Folhas de dados dos equipamentos utilizados
│   ├── 2_images/                   → Imagens para relatórios e referências
│   ├── 3_mermaid-files/            → arquivos para gerar os diagramas de bloco e gantt
│   ├── 4_kicad-pj3/                → Projeto KiCad para a plaquinha shield
│   ├── 5_video/                    → Vídeo do equipamento em operação
│   ├── 6_CAD-files/                → Arquivos .stl e PDF_3D da montagem
│   └── (...)                       → Proposta e relatório
├── libs/
│   ├── tools/                      → Códigos para configuração dos equipamentos                           
│   └── (...)                       → Bibliotecas
├── src/                            
│   └── main.py                     → Código-fonte
├── .micropico                      → Arquivo necessário para a extensão Pi PICO no VSCODE
├── LICENSE                         → Licença de uso do código
└── README.md                       → Resumo e estrutura do projeto
```
