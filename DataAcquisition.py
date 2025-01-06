from PyQt5.QtCore import QThread, pyqtSignal
from collections import deque
import numpy as np
from COM import recibir, procesar_aceleracion, guardar_csv
from DSP import calibrar_aceleracion, calcular_pitch_roll, calcular_psd

# Buffers circulares 
acelX_list, acelY_list, acelZ_list = deque(maxlen=100), deque(maxlen=100), deque(maxlen=100)
pitch_list, roll_list = deque(maxlen=100), deque(maxlen=100)
v_rms_list = deque(maxlen=100)
velocidad = 0

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
                    
                    #acelX_cal -= np.mean(acelX_cal) #resto la media para corregir el offset
                    #acelY_cal -= np.mean(acelY_cal)
                    #acelZ_cal -= np.mean(acelZ_cal)

                    # Guardar datos calibrados en las listas
                    acelX_list.append(acelX_cal)
                    acelY_list.append(acelY_cal)
                    acelZ_list.append(acelZ_cal)

                    # Actualizar tiempo
                    tiempo += ts
                    tiempo_list.append(tiempo)

                    # Calcular pitch y roll
                    pitch, roll = calcular_pitch_roll(acelX_cal, acelY_cal, acelZ_cal)
                    pitch_list.append(pitch)
                    roll_list.append(roll)

                    # Calcular PSD
                    t, psd = calcular_psd(acelX_list, fs)

                    # Integración para obtener velocidad (m/s)
                    velocidad = np.cumsum(ts * np.array(acelX_list))
                    velocidad_mm_s = velocidad * 1000   # Velocidad en mm/s
                    v_rms = np.sqrt(np.mean(velocidad_mm_s**2)) #RMS de la velocidad 
                    v_rms_list.append(v_rms)

                    # Emitir los datos procesados
                    self.data.emit({
                        "acelX_list": acelX_list,
                        "acelY_list": acelY_list,
                        "acelZ_list": acelZ_list,
                        "tiempo_list": tiempo_list,
                        "pitch_list": pitch_list,
                        "roll_list": roll_list,
                        "psd": (t, psd),
                        "velocidad_list": velocidad_mm_s,
                        "v_rms_list": v_rms_list,
                    })
