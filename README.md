# Analizador de Vibraciones

## Descripción
Analizador de Vibraciones es una aplicación diseñada para conectarse con una IMU mediante puerto serie, ya sea Bluetooth o USB, para realizar mediciones de aceleración, pitch y roll, Densidad Espectral de Potencia (PSD) y velocidad en tiempo real. Además, cuenta con la posibilidad de exportar los datos crudos medidos de aceleración en un archivo .csv para su posterior análisis.

También permite analizar la condición de un motor rotativo estático, siguiendo la norma ISO 8528.

Esta aplicación fue desarrollada en el marco de la materia Diseño de Sistemas con Microcontroladores de la Facultad de Ingeniería de la Universidad Nacional del Comahue.

- 📡 **Firmware de la IMU y microcontrolador** (dsPIC33):  
  👉 [IMU](https://github.com/Ogas123/IMU)

![alt text](assets/screenshot.png)

## Características
- Conexión con IMU mediante puerto serie (Bluetooth o USB)
- Medición en tiempo real de:
  - Aceleración
  - Pitch y Roll
  - Densidad Espectral de Potencia (PSD)
  - Velocidad
- Exportación de datos crudos a archivo .csv
- Análisis de condición de motor rotativo estático según norma ISO 8528

## Requisitos
- Python 3.10 o superior
- PySide6
- pyqtgraph
- pyserial
- numpy
- scipy
- matplotlib

## Instalación
1.	Clona este repositorio:
    git clone https://github.com/Ogas123/analizador-de-vibraciones.git
2.	Navega al directorio del proyecto:
    cd analizador-de-vibraciones
3.	Instala las dependencias:
    pip install -r requirements.txt
    Alternativamente, podés instalar manualmente las librerías necesarias:
    pip install PySide6 pyqtgraph pyserial numpy scipy matplotlib
4.	Ejecuta la aplicación:
    python main.py
5.	Selecciona el puerto COM correspondiente y comienza la medición.

## Uso
- Conecta el acelerómetro o dispositivo de adquisición antes de iniciar la medición.
- La interfaz permite visualizar en tiempo real los datos de aceleración y vibración.
- Los datos pueden guardarse para análisis posterior en Python, Scilab o MATLAB.

## Notas
- Asegurate de tener los permisos adecuados para acceder al puerto COM en tu sistema operativo.
- Para mejorar la fluidez de la gráfica, se recomienda usar una computadora con al menos 8 GB de RAM.
- Si se presentan errores al ejecutar la aplicación, revisá que las versiones de Python y las librerías sean compatibles.

## Contacto

agustinschwerdt@gmail.com
