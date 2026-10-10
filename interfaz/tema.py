"""Colores y estilo visual centralizados."""
FONDO = '#202423'
PANEL = '#292e2c'
NEON = '#69ff99'
LINEA = '#48c878'
NODO = '#397d5a'
VISITADO = '#20452f'
TEXTO = '#e1f5e8'
ACTIVO = '#b5ffd0'

ESTILO = '''
QWidget { background: #202423; color: #e1f5e8; font-family: Sans Serif; font-size: 12px; }
QMainWindow, QStatusBar { background: #202423; }
QGroupBox { border: 1px solid #397d5a; border-radius: 9px; margin-top: 12px; padding: 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; color: #69ff99; }
QPushButton { background: #292e2c; border: 1px solid #48c878; border-radius: 6px; padding: 7px 10px; }
QPushButton:hover { background: #354d3d; border-color: #69ff99; }
QPushButton:pressed { background: #397d5a; }
QPushButton:disabled { color: #6c8174; border-color: #405348; }
QProgressBar { background: #292e2c; border: 1px solid #397d5a; border-radius: 4px; text-align: center; min-height: 17px; }
QProgressBar::chunk { background: #397d5a; }
QSpinBox { background: #292e2c; border: 1px solid #397d5a; border-radius: 5px; padding: 4px; }
QLineEdit { background: #292e2c; border: 1px solid #397d5a; border-radius: 5px; padding: 6px; }
QLineEdit:focus { border: 1px solid #69ff99; }
QToolButton { background: #292e2c; color: #69ff99; border: 1px solid #397d5a; border-radius: 6px; padding: 7px; }
QToolButton:checked { border-color: #69ff99; }
QComboBox { background: #292e2c; border: 1px solid #48c878; border-radius: 5px; padding: 5px; }
QComboBox QAbstractItemView { background: #292e2c; selection-background-color: #397d5a; }
QTabWidget::pane { border: 1px solid #397d5a; border-radius: 7px; }
QTabBar::tab { background: #292e2c; padding: 7px 15px; border-bottom: 2px solid #397d5a; }
QTabBar::tab:selected { color: #69ff99; border-bottom-color: #69ff99; }
QTableWidget, QListWidget { background: #252a28; border: 1px solid #397d5a; border-radius: 5px;
    gridline-color: #344a3c; selection-background-color: #397d5a; }
QHeaderView::section { background: #2d3831; color: #69ff99; border: none; padding: 4px; }
QSlider::groove:horizontal { height: 4px; background: #397d5a; border-radius: 2px; }
QSlider::handle:horizontal { background: #69ff99; width: 12px; margin: -4px 0; border-radius: 6px; }
QCheckBox::indicator { width: 13px; height: 13px; border: 1px solid #48c878; border-radius: 3px; }
QCheckBox::indicator:checked { background: #69ff99; }
QScrollBar:vertical { background: #252a28; width: 9px; }
QScrollBar::handle:vertical { background: #397d5a; min-height: 20px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QLabel#titulo { color: #69ff99; font-size: 17px; font-weight: bold; }
QLabel#estado { color: #b5ffd0; }
'''
