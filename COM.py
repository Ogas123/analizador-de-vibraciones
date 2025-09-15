import serial
import serial.tools.list_ports
import binascii
import csv

puerto_serie = None

archivo_csv = None
writer = None

# Funciones de comunicación
def enviar(VectorRS):
    if puerto_serie and puerto_serie.is_open:
        datos_binarios = binascii.unhexlify(VectorRS.replace(' ', ''))
        puerto_serie.write(datos_binarios)

def recibir(tamano):
    if puerto_serie and puerto_serie.is_open:
        try:
            datos = puerto_serie.read(tamano)
            return [int(f'{byte:02X}', 16) for byte in datos]
        except Exception as e:
            return None

def procesar_aceleracion(high_byte, low_byte):          #Transforma los datos recibidos en reales
        valor = ((high_byte << 8) | low_byte) >> 2
        if valor & 0x2000:
            valor -= 0x4000
        return (valor / 4096.0) * 9.80665

def listar_puertos():
    """Devuelve una lista de puertos COM disponibles."""
    return [port.device for port in serial.tools.list_ports.comports()]

def conectar_puerto(com, baudrate=19200):
    """Conecta al puerto serie especificado."""
    global puerto_serie
    try:
        puerto_serie = serial.Serial(port=com, baudrate=baudrate)
        print(f"Conectado a {com}")
        return puerto_serie
    except Exception as e:
        print(f"Error al conectar al puerto {com}: {e}")
        return None

def desconectar_puerto():
    """Desconecta el puerto serie si está conectado."""
    global puerto_serie
    if puerto_serie and puerto_serie.is_open:
        puerto_serie.close()
        print("Desconectado del puerto COM")

def crear_csv(filename):
    global archivo_csv, writer
    # Crear y abrir el archivo CSV
    archivo_csv = open(filename, mode='w', newline='')
    writer = csv.writer(archivo_csv)
    writer.writerow(['acelX', 'acelY', 'acelZ'])  #encabezados

def guardar_csv(acelX, acelY, acelZ):
    global writer
    if writer:
        writer.writerow([acelX, acelY, acelZ])
        
def cerrar_csv():
    global archivo_csv, writer
    if archivo_csv:
        archivo_csv.close() 
        archivo_csv = None  # Desvincula el archivo
    writer = None  # Desvincula el writer