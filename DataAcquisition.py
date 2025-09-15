from PySide6.QtCore import QThread, Signal
from collections import deque
import numpy as np
from COM import recibir, procesar_aceleracion, guardar_csv
from DSP import calibrar_aceleracion, calcular_pitch_roll, calcular_psd
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
    data = Signal(dict) # Señal para enviar los datos procesados

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
                    
                    fmin = 2.0
                    fmax = min(1000.0, fs/2.0)   # no pasar de Nyquist
                    
                    # Actualizar tiempo
                    tiempo += ts
                    tiempo_list.append(tiempo)
                    
                    # Calcular pitch y roll
                    pitch, roll = calcular_pitch_roll(acelX_cal, acelY_cal, acelZ_cal)
                    pitch_list.append(pitch)
                    roll_list.append(roll)

                    # Obtener PSD de aceleraciones
                    fx, psdx = calcular_psd(acelX_list, fs)
                    fy, psdy = calcular_psd(acelY_list, fs)
                    fz, psdz = calcular_psd(acelZ_list, fs)
                    
                    # convertir PSD de aceleración -> PSD de velocidad
                    # evitar división por cero en f=0
                    psd_vx = np.zeros_like(psdx)
                    psd_vy = np.zeros_like(psdy)
                    psd_vz = np.zeros_like(psdz)

                    nonzero = fx > 0
                    psd_vx[nonzero] = psdx[nonzero] / (2.0 * np.pi * fx[nonzero])**2
                    psd_vy[nonzero] = psdy[nonzero] / (2.0 * np.pi * fx[nonzero])**2
                    psd_vz[nonzero] = psdz[nonzero] / (2.0 * np.pi * fx[nonzero])**2

                    # seleccionar banda ISO
                    mask = (fx >= fmin) & (fx <= fmax)
                    if not np.any(mask):
                        # protecciones en caso de ventanas cortas o fs bajo
                        vrms_list.append(0.0)
                    else:
                        # integrar PSD (uso trapz para no depender de df uniforme)
                        vrms_x = np.sqrt(np.trapz(psd_vx[mask], fx[mask]))   # VRMS en m/s
                        vrms_y = np.sqrt(np.trapz(psd_vy[mask], fx[mask]))
                        vrms_z = np.sqrt(np.trapz(psd_vz[mask], fx[mask]))

                        # convertir a mm/s
                        vrms_x_mm = vrms_x * 1000.0
                        vrms_y_mm = vrms_y * 1000.0
                        vrms_z_mm = vrms_z * 1000.0

                        # Resultado combinado:
                        vrms_resultante_mm = np.sqrt(vrms_x_mm**2 + vrms_y_mm**2 + vrms_z_mm**2)

                        vrms_list.append(vrms_resultante_mm)
            
                    # Emitir los datos procesados
                    self.data.emit({
                        "acelX_list": acelX_list,
                        "acelY_list": acelY_list,
                        "acelZ_list": acelZ_list,
                        "tiempo_list": tiempo_list,
                        "pitch_list": pitch_list,
                        "roll_list": roll_list,
                        "psd": (fx, psdx, fy, psdy, fz, psdz),
                        "vrms_list": vrms_list,
                    })
