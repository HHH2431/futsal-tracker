import cv2
import json
import os
from ultralytics import YOLO

def main():
    video_path = "futsal.mp4"
    output_path = "futsal_output.mp4"
    json_path = "tracking_data.json"
    
    print("[INFO] A arrancar pipeline rápida de Tracking e Extração de Dados...")
    # Model configuration (na 1660 SUPER aguenta yolov8n sem pestanejar)
    model = YOLO("yolov8n.pt") 
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERRO] Falha ao abrir: {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    # ==========================================
    # ARQUITETURA: BASE DE DADOS (Dicionário de Tracking)
    # Formato: { "frame_0": [ {"id": 1, "team": null, "cls": "jogador", "x": 100, "y": 200}, ... ] }
    # ==========================================
    tracking_db = {}
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Preparar registo do frame
        current_frame_key = f"frame_{frame_count}"
        tracking_db[current_frame_key] = []

        # YOLO com tracker. Conf=0.45 levanta o limiar para eliminar falsos positivos de pés errados.
        results = model.track(frame, persist=True, tracker="bytetrack.yaml", classes=[0, 32], conf=0.45, verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy()
            clss = results[0].boxes.cls.cpu().numpy()
            
            for box, track_id, cls in zip(boxes, track_ids, clss):
                x1, y1, x2, y2 = map(int, box)
                
                # CÁLCULO CORE (Eixo Pivot dos pés)
                feet_x = int((x1 + x2) / 2)
                feet_y = y2
                
                class_name = "jogador" if cls == 0 else "bola"
                color = (255, 0, 0) if cls == 0 else (0, 165, 255)
                label = f"ID: {int(track_id)}" if cls == 0 else "BOLA"

                # Guardar em "Database"
                tracking_db[current_frame_key].append({
                    "id": int(track_id),
                    "class": class_name,
                    "x": feet_x,
                    "y": feet_y
                })

                # Visual Debugging (Desenho apenas no VideoWriter final, para validação visual)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
                cv2.putText(frame, label, (x1, max(y1 - 5, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                # Ponto crístico! É este ponto vermelho que iremos converter por homografia depois.
                cv2.circle(frame, (feet_x, feet_y), 4, (0, 0, 255), -1) 

        cv2.imshow("Tracking Viewer - Press Q to Quit", cv2.resize(frame, (1280, 720))) 
        out.write(frame)
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # CLEANUP & SALVAGUARDA DE DADOS
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    # Dump the tracking memory into a json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(tracking_db, f, indent=4)
        
    print(f"\n[SUCESSO] Tracking Finalizado. Vídeo gravado em '{output_path}'.")
    print(f"[ARQUITETURA] Base de Dados gerada com sucesso em: '{json_path}'. Tamanho de frames salvos: {frame_count}")

if __name__ == "__main__":
    main()