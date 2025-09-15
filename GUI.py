from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QLineEdit, QFrame, QGridLayout, QFileDialog
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
import pyqtgraph as pg
from COM import enviar, listar_puertos, conectar_puerto, desconectar_puerto, crear_csv, cerrar_csv

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de vibraciones")

        self.setWindowIcon(QIcon("assets/icon.ico"))

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QHBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.init_left_panel()
        self.init_graphs()

    def init_left_panel(self):
        # Panel izquierdo
        self.left_panel = QVBoxLayout()

        # Sección: Título y subtítulo
        label1 = QLabel("<h1>ANALIZADOR DE VIBRACIONES</h1>")
        self.left_panel.addWidget(label1, alignment=Qt.AlignTop | Qt.AlignHCenter)
        
        label2 = QLabel("Universidad Nacional del Comahue - Facultad de Ingeniería - 2025")
        self.left_panel.addWidget(label2, alignment=Qt.AlignTop | Qt.AlignHCenter)

        label3 = QLabel("Diseño de Sistemas con Microcontroladores")
        self.left_panel.addWidget(label3, alignment=Qt.AlignTop | Qt.AlignHCenter)

        label4 = QLabel("Schwerdt Agustin")
        self.left_panel.addWidget(label4, alignment=Qt.AlignTop | Qt.AlignHCenter)

        label5 = QLabel("Prueba de vibración acorde al estándar ISO 10816")
        self.left_panel.addWidget(label5, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Sección: Comunicación y medición
        com_layout = QVBoxLayout()
        com_layout.addWidget(QLabel("<h2>Comunicación y Medición</h2>"))

        self.com_label = QLabel("Seleccionar Puerto COM:")
        com_layout.addWidget(self.com_label)

        # Layout horizontal para ComboBox y botón
        h_layout = QHBoxLayout()

        # ComboBox para los puertos
        self.combobox_com = QComboBox()
        self.combobox_com.addItems(listar_puertos())
        h_layout.addWidget(self.combobox_com)

        # Botón para actualizar puertos con ícono
        self.update_button = QPushButton()
        self.update_button.setIcon(QIcon("assets/refresh.png"))  # Ícono
        self.update_button.setIconSize(QSize(16, 16))  # Tamaño del ícono
        self.update_button.setFixedSize(30, 30)  # Tamaño del botón
        self.update_button.clicked.connect(self.actualizar_puertos)
        h_layout.addWidget(self.update_button)

        # Agregar el layout horizontal al principal
        com_layout.addLayout(h_layout)
        
        self.connect_button = QPushButton("Conectar")
        self.connect_button.clicked.connect(self.conectar_puerto)
        
        com_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Desconectar")
        self.disconnect_button.clicked.connect(desconectar_puerto)
        com_layout.addWidget(self.disconnect_button)

        self.start_button = QPushButton("Iniciar Medición")
        self.start_button.clicked.connect(self.iniciar_medicion)
        com_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Parar Medición")
        self.stop_button.clicked.connect(self.parar_medicion)
        com_layout.addWidget(self.stop_button)

        # Botón para limpiar datos
        self.clear_button = QPushButton("Limpiar Datos")
        self.clear_button.clicked.connect(self.clear_data)
        com_layout.addWidget(self.clear_button)

        self.left_panel.addLayout(com_layout)
        
        # Sección: Guardar datos
        save_layout = QVBoxLayout()
        save_layout.addWidget(QLabel("<h2>Guardar Datos</h2>"))

        self.save_button = QPushButton("Iniciar Grabación")
        self.save_button.clicked.connect(self.iniciar_grabacion)
        save_layout.addWidget(self.save_button)

        self.stop_save_button = QPushButton("Detener Grabación")
        self.stop_save_button.clicked.connect(self.detener_grabacion)
        save_layout.addWidget(self.stop_save_button)

        self.left_panel.addLayout(save_layout)

        # Sección: Análisis de maquinaria
        machine_layout = QVBoxLayout()
        machine_layout.addWidget(QLabel("<h2>Análisis de Maquinaria</h2>"))

        self.machine_label = QLabel("Seleccionar Máquina:")
        machine_layout.addWidget(self.machine_label)

        self.combobox_machine = QComboBox()
        self.combobox_machine.addItems([
            "Grupo 1: Grandes máquinas >300 kW (base flexible)",
            "Grupo 1: Grandes máquinas >300 kW (base rígida)",
            "Grupo 2: Máquinas de 15-300 kW (base flexible)",
            "Grupo 2: Máquinas de 15-300 kW (base rigida)",
            "Grupo 3: Bombas <15 kW con motor separado (base flexible)",
            "Grupo 3: Bombas <15 kW con motor separado (base rígida)",
            "Grupo 4: Bombas <15 kW con motor integrado (base flexible)",
            "Grupo 4: Bombas <15 kW con motor integrado(base rígida)"
        ])
        machine_layout.addWidget(self.combobox_machine)

        self.left_panel.addLayout(machine_layout)
        
        # Sección: Cuadro de Estado
        self.state_frame = QFrame()
        self.state_frame.setFrameShape(QFrame.StyledPanel)
        self.state_frame.setFixedSize(400, 200)

        state_layout = QVBoxLayout()
        self.state_label = QLabel("<h2>ESTADO</h2>")
        self.state_label.setAlignment(Qt.AlignHCenter)
        state_layout.addWidget(self.state_label)

        self.led_layout = QGridLayout()
        self.leds = {}
        states = ["Maquina nueva o reacondicionada", 
                  "La maquina puede operar indefinidamente", 
                  "La maquina no puede operar un tiempo prolongado", 
                  "La vibracion esta provocando daños"]
        for i, state in enumerate(states):
            led_label = QLabel(state)
            led_label.setAlignment(Qt.AlignHCenter)

            led = QLabel()
            led.setFixedSize(20, 20)
            led.setStyleSheet("background-color: gray; border-radius: 10px;")
            self.leds[state] = led

            self.led_layout.addWidget(led_label, i, 0)
            self.led_layout.addWidget(led, i, 1)

        state_layout.addLayout(self.led_layout)
        self.state_frame.setLayout(state_layout)

        self.left_panel.addWidget(self.state_frame, alignment=Qt.AlignBottom | Qt.AlignHCenter)

        self.layout.addLayout(self.left_panel)

    def init_graphs(self):
        # Panel de gráficos
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.plot_widget, 3)

        # Gráfica de aceleración
        self.accel_plot = self.plot_widget.addPlot(title="Aceleración")
        self.accel_plot.showGrid(x=True, y=True)
        self.accel_plot.addLegend()
        self.accel_plot.setLabel('bottom', 'Tiempo', units='s')
        self.accel_plot.setLabel('left', 'Aceleración', units='m/s²')
        self.accel_x = self.accel_plot.plot(pen='r', name='X')
        self.accel_y = self.accel_plot.plot(pen='g', name='Y')
        self.accel_z = self.accel_plot.plot(pen='b', name='Z')

        # Gráfica de pitch y roll
        self.plot_widget.nextRow()
        self.pitch_roll_plot = self.plot_widget.addPlot(title="Pitch y Roll")
        self.pitch_roll_plot.showGrid(x=True, y=True)
        self.pitch_roll_plot.addLegend()
        self.pitch_roll_plot.setLabel('bottom', 'Tiempo', units='s')
        self.pitch_roll_plot.setLabel('left', 'Ángulo', units='°')
        self.pitch = self.pitch_roll_plot.plot(pen='r', name='Pitch')
        self.roll = self.pitch_roll_plot.plot(pen='g', name='Roll')

        # Gráfica de PSD
        self.plot_widget.nextRow()
        self.PSD = self.plot_widget.addPlot(title="Densidad Espectral de Potencia")
        self.PSD.showGrid(x=True, y=True)
        self.PSD.addLegend()
        self.PSD.setLabel('bottom', 'Frecuencia', units='Hz')
        self.PSD.setLabel('left', 'Modulo', units='')
        self.PSDx = self.PSD.plot(pen='r', name='X')
        self.PSDy = self.PSD.plot(pen='g', name='Y')
        self.PSDz = self.PSD.plot(pen='b', name='Z')

        # Gráfica de velocidad
        self.plot_widget.nextRow()
        self.vel_plot = self.plot_widget.addPlot(title="Velocidad")
        self.vel_plot.showGrid(x=True, y=True)
        self.vel_plot.addLegend()
        self.vel_plot.setLabel('bottom', 'Tiempo', units='s')
        self.vel_plot.setLabel('left', 'Velocidad', units='mm/s')
        self.vrms = self.vel_plot.plot(pen='m', name='RMS')


    def iniciar_medicion(self):
        # Enviar comando para iniciar medición continua
        enviar('FD040198')  
         
    def parar_medicion(self):
        # Enviar comando para detener la transmisión
        enviar('FD040199')

    def actualizar_puertos(self):
        self.combobox_com.clear()
        self.combobox_com.addItems(listar_puertos())

    def conectar_puerto(self):
        com = self.combobox_com.currentText()
        conectar_puerto(com)

    def clear_data(self):
        #grafico listas vacias
        self.accel_x.setData([], [])
        self.accel_y.setData([], [])
        self.accel_z.setData([], [])
        self.pitch.setData([], [])
        self.roll.setData([], [])
        self.PSDx.setData([], [])
        self.PSDy.setData([], [])
        self.PSDz.setData([], [])
        self.vrms.setData([], [])

    def iniciar_grabacion(self):
        filename = QFileDialog.getSaveFileName(self, "Guardar Medición", "", "Archivos de texto (*.csv)")[0]
        crear_csv(filename)

    def detener_grabacion(self):
        cerrar_csv()

    def update_led(self, state):
        for key, led in self.leds.items():
            if key == state:
                led.setStyleSheet("background-color: red; border-radius: 10px;")
            else:
                led.setStyleSheet("background-color: gray; border-radius: 10px;")