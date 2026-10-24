<img src="assets/icon/icon.svg" alt="Ícone do Facial Unlock" width="128">

# 🔓 Facial Unlock

Desbloqueia o computador usando a webcam comum para o login.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-suportado-black?logo=apple)
![Windows](https://img.shields.io/badge/Windows-suportado-0078D6?logo=windows)

## 🚀 Como rodar

**macOS**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python facial.py
```

**Windows**

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python facial.py
```

Na primeira vez o app grava o seu rosto; depois, só reconhece. Por enquanto, ao reconhecer o seu rosto ele abre a calculadora (teste).

- `facial.py --cadastrar` — grava mais amostras (ex.: com fone, de óculos, outra luz)
- `facial.py --novo` — apaga o rosto salvo e grava do zero
- `q` — fecha a janela

## 🔐 Segurança e privacidade

- Os dados do seu rosto ficam **só no seu computador**, nunca são enviados para a internet.
- A **senha continua funcionando** como alternativa — o reconhecimento facial é um atalho, não uma substituição.
- ⚠️ Webcams comuns podem ser enganadas por fotos; o anti‑spoofing é etapa obrigatória antes de usar no dia a dia.

## Projeto

Teste para ver se vai funcionar :P