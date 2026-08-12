
Futsal Tracker

Setup Rápido

Requisitos: Python 3.11, VSCode, Extensões Python, Git

Copiar: futsal.v1.py, vídeo e notas (ignorar pastas venv e runs)

Comandos:
python -m venv venv
venv\Scripts\activate
pip install ultralytics opencv-python scenedetect

**Roadmap**

*Deteção de pessoas com YOLOv8 (Feito)*

Criar loop OpenCV frame a frame

Limpar vídeo com scenedetect

Criar ROI interativo de 4 cliques e guardar em json

Melhorar deteção da bola

Fazer tracking e homografia

Extrair analytics (equipas, heatmaps, highlights)

Gerar relatório LLM para o treinador

**Decisões de Arquitetura**

Foco: impossivel ter a camâra sempre fixa, camâra a mover-se.

ROI: Usar sempre a base da caixa (pés do jogador) e não o centro

Git: Nunca enviar mp4, pt, venv ou runs

**Erros Comuns**

Erro ultralytics: Ativar sempre o venv antes

Scripts bloqueados: Executar Set-ExecutionPolicy RemoteSigned -Scope CurrentUser no PowerShell