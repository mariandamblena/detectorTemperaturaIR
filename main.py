import time
import datetime
import csv
import megabas

# Configuración de pines y canales
STACK = 0  # Nivel de pila del HAT
SENSORES_IR_CANALES = [1, 2, 3, 4]  # Canales analógicos para los sensores IR
SENSOR_PROXIMIDAD_CANAL = 5  # Canal digital para el sensor de proximidad
VENTILADOR_CANAL = 1  # Canal de salida digital para el ventilador

# Setpoint para activar el ventilador
SETPOINT_TEMPERATURA = 90.0  # Grados Celsius

# Función para configurar las entradas analógicas
def configurar_entradas_analogicas():
    for canal in SENSORES_IR_CANALES:
        megabas.incfgwr(STACK, canal, 0)  # 0 para 0-10V

# Función para leer la temperatura de un sensor IR
def leer_temperatura(canal):
    voltaje = megabas.getUin(STACK, canal)
    temperatura = convertir_voltaje_a_temperatura(voltaje)
    return temperatura

# Función para convertir el voltaje leído a temperatura
def convertir_voltaje_a_temperatura(voltaje):
    # Ejemplo: Supongamos que 0V corresponde a 0°C y 10V a 100°C
    temperatura = (voltaje / 10.0) * 100.0
    return temperatura

# Función para leer el estado del sensor de proximidad
def leer_sensor_proximidad():
    estado = megabas.getDin(STACK, SENSOR_PROXIMIDAD_CANAL)
    return estado == 1

# Función para controlar el ventilador
def controlar_ventilador(encender):
    estado = 1 if encender else 0
    megabas.setRelays(STACK, VENTILADOR_CANAL, estado)

# Función para guardar las temperaturas en un archivo CSV
def guardar_temperaturas(datos):
    archivo = 'datos_temperatura.csv'
    with open(archivo, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(datos)

# Configurar las entradas analógicas
configurar_entradas_analogicas()

# Bucle principal
try:
    print("Iniciando medición...")
    while True:
        if leer_sensor_proximidad():
            temperaturas = []
            for canal in SENSORES_IR_CANALES:
                temp = leer_temperatura(canal)
                temperaturas.append(temp)
                print(f"Sensor canal {canal}: {temp:.2f}°C")

            # Guardar con timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            guardar_temperaturas([timestamp] + temperaturas)

            # Controlar ventilador según temperatura del sensor 3
            if temperaturas[2] > SETPOINT_TEMPERATURA:
                controlar_ventilador(True)
                print("Ventilador ACTIVADO")
            else:
                controlar_ventilador(False)
                print("Ventilador DESACTIVADO")

            time.sleep(1)  # Espera 1 segundo entre lecturas

        else:
            controlar_ventilador(False)
            time.sleep(0.1)  # Pequeña espera para evitar saturar el CPU

except KeyboardInterrupt:
    print("Programa terminado por el usuario")

finally:
    controlar_ventilador(False)
    print("GPIO limpiado correctamente.")
