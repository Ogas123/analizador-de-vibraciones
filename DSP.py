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


def promedio_movil(datos, n):
    """
    Calcula el promedio móvil de una lista de datos si la longitud es mayor que 'n'.

    Parámetros:
    - datos: Lista de números.
    - n: Tamaño del intervalo para calcular el promedio móvil.

    Retorna:
    - Una lista con los valores del promedio móvil o la lista original si es menor o igual a 'n'.
    """
    if len(datos) <= n:
        return datos  # Si la longitud es menor o igual a 'n', devolver la lista original.

    promedios = [sum(datos[i:i + n]) / n for i in range(len(datos) - n + 1)]
    return promedios


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
    "Grupo 1: Grandes máquinas >300 kW (base flexible)": [3.5, 7.1, 11],
    "Grupo 1: Grandes máquinas >300 kW (base rígida)": [2.3, 4.5, 7.1],
    "Grupo 2: Máquinas de 15-300 kW (base flexible)": [2.3, 4.5, 7.1],
    "Grupo 2: Máquinas de 15-300 kW (base rigida)": [1.4, 2.8, 4.5],
    "Grupo 3: Bombas <15 kW con motor separado (base flexible)": [3.5, 7.1, 11],
    "Grupo 3: Bombas <15 kW con motor separado (base rígida)": [2.3, 4.5, 7.1],
    "Grupo 4: Bombas <15 kW con motor integrado (base flexible)": [2.3, 4.5, 7.1],
    "Grupo 4: Bombas <15 kW con motor integrado(base rígida)": [1.4, 2.8, 4.5]
}

    # Verifica si el tipo de máquina tiene límites definidos
    if tipo_maquina not in limites:
        return "Error"  # Tipo de máquina desconocido

    # Obtiene los límites para el tipo de máquina
    A, B, C = limites[tipo_maquina]

    # Determina el estado según los límites
    if vrms <= A:
        return "Maquina nueva o reacondicionada"
    elif vrms <= B:
        return "La maquina puede operar indefinidamente"
    elif vrms <= C:
        return "La maquina no puede operar un tiempo prolongado"
    else:
        return "La vibracion esta provocando daños"
