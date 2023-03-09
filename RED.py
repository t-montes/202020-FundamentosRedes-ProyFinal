import matplotlib.pyplot as plt
from random import randint

"""Funciones adicionales"""

def promedio(lista, llave=None) -> float:  # función para facilitar el cálculo.
    suma = 0
    for i in lista:
        suma += i if llave is None else i[llave]
    return suma/len(lista)

"""Algoritmos"""

def RED(lst, minT, thresh, maxProb) -> list:
            """ Random Early Detection algorithm """
            mtx = [[lst[0][0], lst[0][2]]]
            counter = lst[0][1]
            total = []
            avgQlen = 0
            numdiscarted = 0
            for i in range(1,len(lst)):
                counter += lst[i][1]
                if len(total) < thresh:
                    total.append(counter)
                else:
                    total.append(counter)
                    del total[0]
                avgQlen = sum(total)/thresh
                if lst[i][1] != -1:
                    # Cuando es -1 el tiempo (es de llegada) no se tiene en cuenta para la matriz.
                    if avgQlen < minT:
                        mtx.append([lst[i][0], lst[i][2]]) #tiempo, bytes
                    elif avgQlen > minT + thresh:
                        pass # Se descarta
                        numdiscarted += 1
                    else:
                        probability = maxProb*(1 - (minT + thresh - avgQlen)/thresh) # Fórmula
                        num = randint(1, 100)/100 # número aleatorio entre 0.01 y 1
                        if num < probability:
                            pass # Se descarta
                            numdiscarted += 1
                        else:
                            mtx.append([lst[i][0], lst[i][2]])
            print(f"RED -> Elements discarted = {numdiscarted}")      
            return mtx

"""Constantes"""

filename = "datosParte2_90segundos.csv"

"""Programa Principal"""


"""Paso 1. Cargar los datos"""
# Se cargan los datos
matriz = []  # Matríz de datos
archivo = open(filename, 'r')  # Se abre el archivo
linea = archivo.readline().replace('\n', '').replace(
    ',', '.')  # Se lee la primera linea
linea = archivo.readline().rstrip()
while len(linea) > 0:
    linea = linea.split(',')
    datos = [0, 0]
    datos[0] = float(linea[0])
    datos[1] = float(linea[1])
    matriz.append(datos)  # Se adiciona la [tiempo,paquete] a la matriz
    linea = archivo.readline().replace('\n', '')  # Se vuelve a leer la linea
archivo.close()

del linea, archivo, filename, datos

#Se halla lambda
suma = [0,0] #[tiempoTotal,longitudTotal]
for fila in range(len(matriz)):  #Se recorren las filas de la matríz
    suma[0] += float(matriz[fila][0]) #Se le suma al tiempo total
    suma[1] += float(matriz[fila][1]) #Se le suma a la longitud total
lbd = suma[1]/suma[0]*len(matriz) #Se calcula el promedio de lambda

applied = []
def main(matriz, rhos, minT=5, thresh=10, maxProb=0.25, AQM=None):
    applied.append(AQM)
    for rho in rhos:
        """Paso 2. Calcular la tabla"""
        
        tabla = [[], [], [], []]
        mu = lbd/rho
        for fila in range(len(matriz)):  # Se recorren las filas de la matríz
            # Se calcula el tiempo de transmisión total
            tt = matriz[fila][1]/mu
            if fila == 0:  # Se analiza si es el primer dato
                # Se agrega el tiempo de inicio
                tabla[1].append(matriz[fila][0])
                tabla[3].append(tt)  # Tiempo en que termina la transmisión
            # Si el fin de transmisión
            elif tabla[3][fila-1] > matriz[fila][0]:
                tabla[1].append(tabla[3][fila-1])
                tabla[3].append(tt+tabla[3][fila-1])
            else:
                tabla[1].append(matriz[fila][0])
                tabla[3].append(matriz[fila][0]+tt)
    
            tabla[0].append(matriz[fila][0])
            tabla[2].append(tt)
        
        """Paso 3. Calcular lista de 0,1,-1 por paquete"""
        lst = []
        for i in range(len(tabla[0])):
            if tabla[0][i] == tabla[1][i]:
                lst.append((tabla[0][i], 0, matriz[i][1]))
            else:
                lst.append((tabla[0][i],  1, matriz[i][1]))
                lst.append((tabla[1][i], -1, matriz[i][1]))
    
        lst.sort(key=lambda x: x[0])
        
        """Paso 4. Aplicar AQM"""
        
        if AQM == "RED":
            global new
            new = RED(lst, minT, thresh, maxProb)
            main(new, rhos, minT, thresh, maxProb, "NEXT")
        
        """Paso 5. Calcular Qlen en cada toma"""
        Wlen = []
        times = []
        cont = 0
        for i in range(len(lst)):
            cont += lst[i][1]  # Suma 0, 1 o -1
            times.append(lst[i][0])
            Wlen.append(cont/lbd) # cont = Qlen
    
        if AQM == "NEXT":
            global x_RED, y_RED
            x_RED = times  # times
            y_RED = Wlen  # Qlens
        
        x = times
        y = Wlen
        return x,y
    
    

while float((rho := input("Digite Rho(s): ")).split(',')[0]) > 0:
    minThresh = input("\tDigite el minThresh ej=5: ")
    try:
        minThresh = float(minThresh)
        print(f"minThresh configurado como {minThresh}")
    except:
        print("minThresh cambiado a 5")
        minThresh = 5 # Min queue length threshold
    threshold = input("\tDigite el threshold ej=10: ")
    try:
        threshold = float(threshold)
        print(f"threshold configurado como {threshold}")
    except:
        print("threshold cambiado a 10")
        threshold = 10  # Max queue length threshold
    maxProbability = input("\tDigite la maxProbability ej=0.25: ")
    try:
        maxProbability = float(maxProbability)
        print(f"maxProbability configurado como {maxProbability}")
    except:
        print("maxProbability cambiado a 0.25")
        maxProbability = 0.25  # Probabilidad máxima de descartar paquete
    rhos = [eval(i) for i in rho.split(',')]
    AQM = "RED"
    x, y = main(matriz, rhos, minThresh, threshold, maxProbability, AQM)

    """Paso 6. Graficar"""
    plt.plot(x,y)
    plt.plot(x_RED, y_RED)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Time in Queue (seconds)")
    plt.title(f"Time in Queue with ρ={f'{0.9934}'.replace('.',',')}")
    plt.show()
