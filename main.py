from PyQt5.QtWidgets import QApplication
from GUI import MainWindow
from DataAcquisition import WorkerThread
from DSP import determinar_estado

# Función para actualizar la interfaz
def actualizar_gui(datos):
    # Actualizar gráficos
    window.accel_x.setData(datos["tiempo_list"], datos["acelX_list"])
    window.accel_y.setData(datos["tiempo_list"], datos["acelY_list"])
    window.accel_z.setData(datos["tiempo_list"], datos["acelZ_list"])

    # Graficar pitch y roll
    window.pitch.setData(datos["tiempo_list"], datos["pitch_list"])
    window.roll.setData(datos["tiempo_list"], datos["roll_list"])

    # Graficar PSD
    tx, psdx, ty, psdy, tz, psdz = datos["psd"]
    window.PSDx.setData(tx, psdx)
    window.PSDy.setData(ty, psdy)
    window.PSDz.setData(tz, psdz)

    # Graficar velocidad
    window.vel.setData(datos["tiempo_list"], datos["velocidad_list"])
    window.velrms.setData(datos["tiempo_list"], datos["v_rms_list"])

    # Determinar estado de la máquina
    selected_machine = window.combobox_machine.currentText()    # Obtener el tipo de máquina seleccionado
    estado = determinar_estado(selected_machine, datos["v_rms_list"][-1])
    window.update_led(estado)   # Actualizar estado de la máquina

    
# Ejecutar aplicación
app = QApplication([])
window = MainWindow()

# Iniciar hilo de adquisición
hilo_adquisicion = WorkerThread()
hilo_adquisicion.data.connect(actualizar_gui)  # Conectar señal de datos a la función de actualización
hilo_adquisicion.start()

# Mostrar ventana principal
window.show()
app.exec_()
