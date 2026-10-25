# <img src="assets/icon/icon.svg" alt="Ícone do Facial Unlock" height="32" align="top"> Facial Unlock

🇺🇸 [English](README.md) | 🇧🇷 **Português**

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

A tela inicial mostra se já existe um rosto cadastrado e permite:

- **Register face** — grava o seu rosto pela webcam
- **Add samples** — grava mais amostras (ex.: com fone, de óculos, outra luz)
- **Test recognition** — reconhece o seu rosto e, por enquanto, abre a calculadora

Para cadastrar, o app pede a senha do computador (Touch ID/senha no Mac, Windows Hello no Windows).

## 🔐 Segurança e privacidade

- Os dados do seu rosto ficam **só no seu computador**, nunca são enviados para a internet.
- A **senha continua funcionando** como alternativa — o reconhecimento facial é um atalho, não uma substituição.
- 📸 Contra fotos: depois de reconhecer o rosto, o app pede para **ficar parado e depois sorrir**. Uma foto não muda de expressão.

## Projeto

Teste para ver se vai funcionar :P
