from PyQt5.QtCore import QThread, pyqtSignal
from collections import deque
import numpy as np
from COM import recibir, procesar_aceleracion, guardar_csv
from DSP import calibrar_aceleracion, calcular_pitch_roll, calcular_psd, promedio_movil
# Buffers circulares 
acelX_list, acelY_list, acelZ_list = deque(maxlen=100), deque(maxlen=100), deque(maxlen=100)
acelX_centrada_list, acelY_centrada_list, acelZ_centrada_list = deque(maxlen=100), deque(maxlen=100), deque(maxlen=100)
acelX_filtrada_list, acelY_filtrada_list, acelZ_filtrada_list = deque(maxlen=100), deque(maxlen=100), deque(maxlen=100)
pitch_list, roll_list = deque(maxlen=100), deque(maxlen=100)
vrms_list = deque(maxlen=100)

tiempo_list = deque(maxlen=100)
tiempo = 0

fs = 100  # Frecuencia de muestreo (Hz)
ts = 1 / fs

class WorkerThread(QThread):
    data = pyqtSignal(dict) # Señal para enviar los datos procesados

    def run(self):
        global tiempo
        while True:
            VectorRS = recibir(10)
            
            if VectorRS and VectorRS[0] == 0xFE:  # Verifico el formato de la respuesta
                    # Procesar datos
                    acelX_raw = procesar_aceleracion(VectorRS[4], VectorRS[5])
                    acelY_raw = procesar_aceleracion(VectorRS[6], VectorRS[7])
                    acelZ_raw = procesar_aceleracion(VectorRS[8], VectorRS[9])

                    # Guardo datos sin calibrar en el CSV
                    guardar_csv(acelX_raw, acelY_raw, acelZ_raw)

                    # Aplicar calibración
                    acelX_cal, acelY_cal, acelZ_cal = calibrar_aceleracion(acelX_raw, acelY_raw, acelZ_raw)

                    acelX_list.append(acelX_cal)
                    acelY_list.append(acelY_cal)
                    acelZ_list.append(acelZ_cal)

                    offsetX = np.mean(acelX_list)  # Calcula la media de la lista acumulada
                    offsetY = np.mean(acelY_list)
                    offsetZ = np.mean(acelZ_list)

                    # Restar el offset para centrar en 0
                    acelX_centrada_list.append(acelX_cal - offsetX)
                    acelY_centrada_list.append(acelY_cal - offsetY)
                    acelZ_centrada_list.append(acelZ_cal - offsetZ)

                    # Actualizar tiempo
                    tiempo += ts
                    tiempo_list.append(tiempo)
                    
                    # Calcular pitch y roll
                    pitch, roll = calcular_pitch_roll(acelX_cal, acelY_cal, acelZ_cal)
                    pitch_list.append(pitch)
                    roll_list.append(roll)

                    #filtro antes de integrar
                    acelX_filtrada_list = promedio_movil(acelX_centrada_list, 100)
                    acelY_filtrada_list = promedio_movil(acelY_centrada_list, 100)
                    acelZ_filtrada_list = promedio_movil(acelZ_centrada_list, 100)

                    # Integración para obtener velocidad (m/s)
                    velocidadX = np.cumsum(ts * np.array(acelX_filtrada_list))
                    velocidadY = np.cumsum(ts * np.array(acelY_filtrada_list))
                    velocidadZ = np.cumsum(ts * np.array(acelZ_filtrada_list))

                    # Calcular velocidad resultante
                    velocidad_resultante = np.sqrt(velocidadX**2 + velocidadY**2 + velocidadZ**2)
                    velocidad_mm_s = velocidad_resultante * 1000   # Velocidad en mm/s
                    
                    # Calcular RMS de la velocidad
                    vrms = np.sqrt(np.mean(velocidad_mm_s**2)) 
                    vrms_list.append(vrms)

                    # Calcular PSD
                    tx, psdx = calcular_psd(acelX_centrada_list, fs)
                    ty, psdy = calcular_psd(acelY_centrada_list, fs)
                    tz, psdz = calcular_psd(acelZ_centrada_list, fs)
                    
                    # Emitir los datos procesados
                    self.data.emit({
                        "acelX_list": acelX_centrada_list,
                        "acelY_list": acelY_centrada_list,
                        "acelZ_list": acelZ_centrada_list,
                        "tiempo_list": tiempo_list,
                        "pitch_list": pitch_list,
                        "roll_list": roll_list,
                        "psd": (tx, psdx, ty, psdy, tz, psdz),
                        "vrms_list": vrms_list,
                    })
