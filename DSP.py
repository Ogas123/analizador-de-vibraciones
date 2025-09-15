import numpy as np
from scipy.signal import welch
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


def calcular_psd(acel, fs, nperseg=None):
    """
    Calcula la PSD de la señal de aceleración usando Welch.

    acel : array-like (list, deque, np.array) en m/s^2
    fs   : frecuencia de muestreo [Hz]
    nperseg : tamaño de segmento para Welch
    """
    # Convertir a numpy array por si recibo deque o lista
    acel = np.asarray(acel, dtype=float)
    
    if acel.size == 0:
        return np.array([]), np.array([])

    freqs, psd_a = welch(
        acel,
        fs=fs,
        nperseg=min(nperseg or 256, len(acel)),  # nperseg <= tamaño de la señal
        window='hann',
        scaling='density'
    )
    return freqs, psd_a


def determinar_estado(tipo_maquina, vrms):
    """
    Determina el estado de un grupo electrógeno según ISO 8528-9:2017,
    usando directamente el texto seleccionado en el combobox.
    
    Args:
        tipo_maquina (str): Texto del combobox (ej: "≤ 40 kW").
        vrms (float): Valor RMS de vibración (mm/s).
    
    Returns:
        str: Estado de la máquina.
    """
    # Diccionario con los límites Vrms (Generator, columna value 1 / value 2)
    limites = {
        "≤ 40 kW": (50, 60),
        "40 – 100 kW": (25, 30),
        "100 – 200 kW": (25, 30),
        "200 – 1000 kW": (20, 24),
        "> 1000 kW": (15, 20),
    }
    
    if tipo_maquina not in limites:
        return "Error: tipo no reconocido"
    
    lim1, lim2 = limites[tipo_maquina]
    
    if vrms <= lim1:
        return f"Aceptable"
    elif vrms <= lim2:
        return f"Condicional"
    else:
        return f"Inaceptable"