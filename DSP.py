import numpy as np
from scipy.signal import correlate
import math

def calibrar_aceleracion(ax, ay, az):
    # Matrices y vectores de calibración
    alfa_yx, alfa_zx, alfa_zy = -0.016570, 0.009592, 0.013368
    Sx, Sy, Sz = 1.003519, 0.973724, 0.948608
    bx, by, bz = -0.263367, -0.017486, 0.619016

    # Definir matrices
    T = np.array([[1,       0,       0],
                  [alfa_yx, 1,       0],
                  [alfa_zx, alfa_zy, 1]])

    K = np.diag([Sx, Sy, Sz])
    b = np.array([bx, by, bz])

    # Vector de aceleración original
    a = np.array([ax, ay, az])

    # Aplicar calibración
    A_cal = T @ K @ (a - b)

    return A_cal[0], A_cal[1], A_cal[2]  # ax_cal, ay_cal, az_cal


def calcular_pitch_roll(acelX, acelY, acelZ):
    """Calcula pitch y roll en base a las aceleraciones."""
    pitch = math.atan2(acelX, math.sqrt(acelY**2 + acelZ**2)) * 180 / math.pi
    roll = math.atan2(acelY, math.sqrt(acelX**2 + acelZ**2)) * 180 / math.pi
    return pitch, roll

def calcular_psd(Acc, f):
    """
    Calcula la autocorrelación de la señal y luego la Densidad Espectral de Potencia (PSD).

    Parámetros:
    Acc : numpy array
        Señal de entrada.
    f : float
        Frecuencia de muestreo de la señal.

    Retorna:
    t : numpy array
        Rango de frecuencias centrado.
    PSD : numpy array
        Densidad espectral de potencia.
    """
    # Calcular la autocorrelación normalizada
    Rx = correlate(Acc, Acc, mode='full')  # Autocorrelación
    Rx = Rx / np.max(np.abs(Rx))           # Normalizar
    N = len(Rx)                            # Número de puntos en la autocorrelación

    # Transformada de Fourier para obtener la PSD
    PSD = np.fft.fftshift(np.abs(np.fft.fft(Rx)) / N)  # FFT y normalización
    t = np.linspace(-f / 2, f / 2, len(PSD))           # Rango de frecuencias centrado

    return t, PSD



def determinar_estado(tipo_maquina, vrms):
    """
    Determina el estado de la máquina según el tipo y el valor Vrms.
    
    Args:
        tipo_maquina (str): Tipo de máquina (Grupo I, Grupo II, etc.).
        vrms (float): Valor RMS de vibración.

    Returns:
        str: Estado de la máquina ("OK", "Advertencia", "Alarma", "Error").
    """
    # Límites de vibración según ISO 10816
    limites = {
        "Grupo I: Máquinas de 15-75 kW": [0.71, 1.8, 4.5],  # [OK, Advertencia, Alarma]
        "Grupo II: Máquinas >75 kW": [1.12, 2.8, 7.1],
        "Grupo III: Máquinas acopladas": [1.8, 4.5, 11.2],
        "Grupo IV: Motores >300 kW": [2.8, 7.1, 18]
    }

    # Verifica si el tipo de máquina tiene límites definidos
    if tipo_maquina not in limites:
        return "Error"  # Tipo de máquina desconocido

    # Obtiene los límites para el tipo de máquina
    ok_limit, warning_limit, alarm_limit = limites[tipo_maquina]

    # Determina el estado según los límites
    if vrms <= ok_limit:
        return "OK"
    elif vrms <= warning_limit:
        return "Advertencia"
    elif vrms <= alarm_limit:
        return "Alarma"
    else:
        return "Error"

