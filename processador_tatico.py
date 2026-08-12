import cv2
import json
import numpy as np

polygon_points_display = []
WINDOW_NAME = "Mascara Anti-Ruido - Selecione os 4 limites uteis"

def mouse_callback(event, x, y, flags, param):
    global polygon_points_display
    if event == cv2.EVENT_LBUTTONDOWN:
         if len(polygon_points_display) < 4:
             polygon_points_display.append((x, y))

def main():
    json_in = "tracking_data.json"
    json_out = "clean_data.json"
    video_path = "futsal.mp4"

    # Ler array cru da memoria Yolo
    print("[INFO] A ler ficheiro original JSON (Extração Turbinada)...")
    try:
        with open(json_in, 'r') as f:
             db_tracking = json.load(f)
    except Exception as e:
         print("[ERRO] JSON corrompido ou cancelado mal. Começa a limar com que gravou.")
         return

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret: 
         return

    # Escala do monitor p/ facilitar trabalho do rato vs a realidade física
    orig_h, orig_w = frame.shape[:2]
    
    # Nós queremos que te caiba num ecrã para ver bem (Resize p/ 1280x720 UI)
    scale_x = orig_w / 1280.0
    scale_y = orig_h / 720.0
    frame_ui = cv2.resize(frame, (1280, 720))

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    print("\n--- INSTRUÇÕES ---")
    print("O teu objetivo é só excluir as zonas que vão entupir dados. \nIgnora veres os cantos!")
    print("-> 1º e 2º Cliques (Esq+Drt cima, delimitando público das escadas etc)")
    print("-> 3º e 4º Cliques (Dir+Esq baixo, fechando o plano útil no lado mais junto ao tripé)")
    print("Clica ENTER no fim dos 4. Fecha esta janela para sair sem processar nada.\n")

    while True:
        display = frame_ui.copy()
        
        # UI Desenho interativo
        for i, pt in enumerate(polygon_points_display):
            cv2.circle(display, pt, 6, (0, 0, 255), -1)
            # Para ajudar o arquiteto a ver logo as pernas mal limadas
            if i > 0:
                 cv2.line(display, polygon_points_display[i-1], pt, (255,0,0), 2)
                 
        if len(polygon_points_display) == 4:
            cv2.line(display, polygon_points_display[-1], polygon_points_display[0], (0, 255, 0), 2)
            cv2.putText(display, "[4 CLIQUES DEECTADOS: Aperte ENTER para Excluir Dados]", (40, 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0,255,255), 2)

        cv2.imshow(WINDOW_NAME, display)
        
        k = cv2.waitKey(20) & 0xFF
        if k == 13 and len(polygon_points_display) == 4: 
             break
        elif k == 27 or k == ord('q'): # ESC Cancela operação toda
             print("A sair...")
             cv2.destroyAllWindows()
             return

    cv2.destroyAllWindows()

    # Mágica de matemática. Nós convertemos os quatro pequenos pixels que tu carregaste no HD para pixeis brutos (scale original 1080p, ou ate o 4K do video):
    poly_pontos_originais = [
         (int(x * scale_x), int(y * scale_y)) 
         for (x, y) in polygon_points_display
    ]
    pts_polygon_matematico = np.array(poly_pontos_originais, np.int32).reshape((-1, 1, 2))

    # EXECUTA A FILTRAGEM OFFLINE NO ARRAY .JSON CRU.
    print("[PROCESSO] Exterminando tudo fora desse Polígono...")
    registos_processados = 0
    eliminacoes = 0
    clean_db = {}
    
    for frame_id, trackers in db_tracking.items():
        clean_db[frame_id] = []
        for track_node in trackers:
             registos_processados += 1
             # Verifica: Esta a ler coords Originais cruzando c o PtsPoly tb originais convertidos ali p/ cima. Limpo e exacto:
             is_valid = cv2.pointPolygonTest(pts_polygon_matematico, (track_node["x"], track_node["y"]), False)
             
             if is_valid >= 0:
                  clean_db[frame_id].append(track_node)
             else:
                  eliminacoes += 1
    
    with open(json_out, 'w') as f:
         json.dump(clean_db, f, indent=4)

    print(f"\n=====================================")
    print(f"[ESTATISTICA V1] Pontos processados YOLO (Tóxicos+Úteis): {registos_processados}")
    print(f"[EXTERMINIO BANCADAS] Leituras apagadas permanentemente:   {eliminacoes}")
    print(f"[FINAL GRAVADO] Registos Tacticos válidos guardados ({json_out}):  {registos_processados - eliminacoes}")
    print("=====================================")

if __name__ == "__main__":
    main()