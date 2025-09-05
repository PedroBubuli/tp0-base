# TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).


### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación. Respetar las entradas de log planteadas en los ejercicios, pues son las que se chequean en cada uno de los tests.

La corrección personal tendrá en cuenta la calidad del código entregado y casos de error posibles, se manifiesten o no durante la ejecución del trabajo práctico. Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).



# DOCUMENTACION

## Ejercicio N°1:

El objetivo de este ejercicio es automatizar la creación de un archivo docker-compose.yaml con una cantidad configurable de clientes.


- Se implementó un script de Bash llamado generar-compose.sh, ubicado en la raíz del proyecto.

- El script recibe dos parámetros:

    Nombre del archivo de salida (ejemplo: docker-compose-dev.yaml)

    Número de clientes a generar (ejemplo: 5)

- Se utilizó un bucle for en Bash para generar dinámicamente la sección de cada cliente en el yaml.

- Se mantuvo la estructura de red y servidor que ya existía en el archivo docker-compose-dev.yaml del repositorio original.


Ejemplo de ejecución:

```bash
./generar-compose.sh docker-compose-dev.yaml 5
```
Esto genera un archivo docker-compose-dev.yaml con 1 servidor y 5 clientes.

Generación de clientes:

```bash
for i in $(seq 1 "$NUM_CLIENTS"); do
cat >> "$OUTPUT" <<EOF

  client$i:
    container_name: client$i
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=$i
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
EOF
done
```
donde OUTPUT es el primer parámetro (nombre del archivo de salida) y NUM_CLIENTS el segundo parámetro (la cantidad de clientes a generar).




## Ejercicio N°2:

En este ejercicio se modificó la forma en que se inyectan los archivos de configuración de cliente y servidor.

El objetivo es que los contenedores no requieran ser reconstruidos cuando se cambie la configuración.

Cambios realizados

#### Cliente:

  - Se eliminó del Dockerfile la instrucción que copiaba config.yaml dentro de la imagen.

  - Ahora el config.yaml se monta dinámicamente mediante un volume en docker-compose.


  ```bash
  for i in $(seq 1 "$NUM_CLIENTS"); do
  cat >> "$OUTPUT" <<EOF

    client$i:
      container_name: client$i
      image: client:latest
      entrypoint: /client
      environment:
        - CLI_ID=$i
      volumes:
        - ./client/config.yaml:/config.yaml
      networks:
        - testing_net
      depends_on:
        - server
  EOF
  done
  ```

#### Servidor:

  - No fue necesario modificar el codigo (main.py ya lee el config.ini directamente).

  - Solo se agregó un volumen en el docker-compose para que el archivo se monte en el contenedor.


  ```bash
  cat > "$OUTPUT" <<EOF
  name: tp0
  services:
    server:
      container_name: server
      image: server:latest
      entrypoint: python3 /main.py
      environment:
        - PYTHONUNBUFFERED=1
      volumes:
        - ./server/config.ini:/config.ini
      networks:
        - testing_net
  EOF
  ```




## Ejercicio N°3:

En este ejercicio se crea un validar-echo-server.sh con el fin de verificar el correcto funcionamiento del servidor mediante netcat. el test consiste en enviar un mensaje y verificar que se reciba exactamente el mismo mensaje de vuelta.

el script hace lo siguiente: 

```bash
REPLY=$(docker run --rm --network tp0_testing_net alpine \
    sh -c "echo $TEST_MSG | nc -w 2 server 12345")
```
 #### `1. docker run --rm --network tp0_testing_net alpine`
  - crea un contenedor temporal a partir de la imagen alpine (la cual ya viene con netcat)
  - --rm hace que el contenedor se elimine cuado termine
  - --network tp0_testing_net conecta este contenedor a la red tp0_testing_net que es la misma que usan el server y los clientes.

#### `2. sh -c "..."`
 - ejecuta un comando de shell dentro del contenedor alpine.

#### `3. echo $TEST_MSG | nc -w 2 server 12345`
 - echo $TEST_MSG imprime el mensaje que queremos enviar
 - | nc -w 2 server 12345 lo pasa a netcat que se conecta al host server en el puerto 12345
  - -w 2 indica que netcat espera máximo 2 segundos por una respuesta

#### `4. REPLY=$( ... )`
 - Captura la salida de todo el comando y lo guarda en la variable REPLY

#### `5. Validacion`
```bash
if [ "$REPLY" = "$TEST_MSG" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
```
 - Si reply es igual a test_msg, se imprime "success", en su defecto "fail"





## Ejercicio N°4:

Se modificó la implementación de client.go y server.py para que tanto el client como el server cierren de forma graceful al recibir la signal SIGTERM. 

#### `En client.go :`
  - dentro del metodo SartClientLoop se creo el siguiente channel:
  ```go
  signalChannel := make(chan os.Signal, 1)
	signal.Notify(signalChannel, os.Interrupt, syscall.SIGTERM)
  ```
  este signalChannel recibe de forma directa singlas de parte del sistema operativo. Después del envío de cada mensaje, se chequea si llegó alguna señal al channel de la siguiente forma:

  ```go
  select {
		case <-signalChannel:
			log.Infof("action: exit | result: success | client_id: %v", c.config.ID)
			c.conn.Close()
			return
		default:
  ```
  Donde en el default se ejecuta el envío del siguiente mensaje. También se editó la implementación del Client para que deje de crear una nueva conexión por cada mensaje que quiere enviar y cerrarla después de enviar un solo mensaje. En cambio, ahora crea una sola conexión para enviar todos los mensajes que desea.

  A futuro se podria considerar el caso donde el cliente se queda bloqueado en el read y agregarle un timeout al read para que chequee el channel mientras espera respuesta del servidor.

  #### `En server.py :`

  Se modificó la implementación del servidor para que pueda cerrar de forma graceful al recibir señales del sistema operativo, como SIGTERM o SIGINT.

  Se registra un signal handler para SIGINT y SIGTERM usando la librería signal:
  ```python
  signal.signal(signal.SIGINT, self._signal_handler)
  signal.signal(signal.SIGTERM, self._signal_handler)
  ```
  Cuando el servidor recibe alguna de estas señales, se ejecuta el método _signal_handler:

  ```python
  def _signal_handler(self, sig, frame):
    logging.Info("action: exit | result: success | reason: signal_received | signal: SIGTERM")

    self._running = False
    self._server_socket.shutdown(socket.SHUT_RDWR)
    self._server_socket.close()
  ```

  La implementación del server se cambió para recibir mensajes del client hasta que el client cierre la conexion con el server.


  ## Ejercicio N°5:

  Se modifica el Cliente y Servidor para que funcionen como apostador y agencia de quinela respectivamente. 

  #### `cambios en el server:`

  A la clase Server se le agregan dos atributos nuevos:

  ```python
  self.client_id = 0
  self.clients_dictionary = {}
  ```
  luego en run se hace:
  ```python
  client_connection = self.__accept_new_connection()
  if client_connection:
    self.clients_dictionary[self.client_id] = client_connection
    self.__handle_client_connection(self.client_id)
    self.client_id += 1
  ```
  Esto se incluyo para dejar lugar a que el Server pueda atender a mas de un cliente a la vez y organizar todos los sockets de sus clientes en el diccionario para poder despues liberarlos comodamente cuando haga falta.

  client_connection en este caso es un objeto de la clase ServerProtocol el cual posee el socket de la conexion con un cliente especifico y se encarga de la comunicación con el mismo.

  - recv_bet_info() -> metodo del protocolo que se encarga de recibir toda la informacion de una apuesta. Hace uso de los siguinetes metodos:
  recv_string() y recv_bytes().
  ```python
  def recv_bytes(self, bytes_to_recv):
    buffer = self.recv_all(bytes_to_recv)
    if buffer is None:
        return None
    return int.from_bytes(buffer, byteorder='big')
  ```
  int.from_bytes(buffer, byteorder='big') se interpretan los bytes de buffer como un numero entero con los bytes ordenados por bigendian (que es como los envia el cliente).

  ```python
  def recv_string(self):
    string_size = self.recv_bytes(1)
    if string_size is None:
        return None

    string = self.recv_all(string_size)
    if string is None:
        return None
    return string.decode('utf-8')
  ```
  string.decode('utf-8') se interpretan los bytes de 'string' como texto en codificacion UTF-8 y los convierte a un string de python.

  ```python
  def recv_all(self, length):
    data = b''
    while len(data) < length:
        more = self.socket.recv(length - len(data))
        if not more:
            return None
        data += more
    return data
  ```
con este metodo recv_all se evita un short read al estar pidiendo en bucle que la cantidad total recibida sea igual a lenght.


 #### `cambios en el cliente:`

 Para empezar, el main busca del archivo docker-compose la informacion sobre el cliente:
```go
name := v.GetString("nombre")
surname := v.GetString("apellido")
dni := uint32(v.GetInt("documento"))
date_of_birth := v.GetString("nacimiento")
number := uint32(v.GetInt("numero"))
```
en client.go se creo el metodo Bet() para el struct Client. Bet() se conecta al servidor con connectToServer() y de esta forma Client adquiere una instancia de ClientProtocol que contiene el socket con la conexion al servidor.

```go
type ClientProtocol struct {
	skt net.Conn
}
```
Desde Bet() se hace uso del ClientProtocol del Client y se llama al metodo sendBetInfo() de ClientProtocol, pasandole por parametro la info del cliente.
```go
func (cp *ClientProtocol) SendNumber(num uint32) error {
	data := make([]byte, sizeofUint32)
	binary.BigEndian.PutUint32(data, num)
	err := cp.SendAll(data)
	return err
}
```
binary.BigEndian.PutUint32(data, num) esto hace que los bytes de 'num' se pasen a 'data' en orden Big Endian (como los espera el server).

```go
func (cp *ClientProtocol) SendAll(data []byte) error {
	totalSent := 0
	dataLen := len(data)

	for totalSent < dataLen {
		n, err := cp.skt.Write(data[totalSent:])
		if err != nil {
			return err
		}
		totalSent += n
	}
	return nil
}
```
el contador totalSent de marca bytes ya se enviaron y gracias a eso se puede repetir el ciclo de envio hasta que totalSent == dataLen enviando en cada write la porcion restante de data.


  ## Ejercicio N°6:

  Se modifica el cliente para que envie varias apuestas en un solo mensaje (sin excederse de 8kb de envio de informacion o de mas de 99 apuestas por mensaje).

  #### `cambios en el cliente:`

  El cliente ahora saca de su archivo agency.csv la informacion de las bets a enviar. Se lee el archivo una linea a la vez, serializandola con el protoclo para almacenarla en el chunk que se va a enviar al servidor.
  
  ```go
  bytes := c.protocol.serializeBetInfo(parts[NAME_POS], parts[SURNAME_POS], uint32(dni), parts[DATE_OF_BIRTH_POS], uint32(num))

  chunk = append(chunk, bytes...)
  ```
  El protocolo envia la informacion al server en este orden:
 
  `AgencyID(1byte) | cantidadDeApuestas(1byte) | apuesta1 | apuesta2 | ...`
  
  las apuestas conservan el mismo formato de antes.

  Se lee del archivo acumulando bets hasta que:
  - la cantidad de apuestas sea mayor a 99
  - la cantidad de bytes acumulados supere los 8kb
  cuando una de esas dos cosas ocurre se envia lo que se tiene acumulado hasta el momento, pero no se le envia al server el codigo indicando que ya se enviaron todas las apuestas y recibe del server el mensaje de success al procesarse las apuestas enviadas.

  De esta forma el server mantiene la conexion con el cliente porque sabe que todavia le quedan bets por enviar.

  El cliente sigue acumulando bets hasta que se vuelva a cumplir una de las dos condiciones anteriores o hasta que llegue al fin del archivo.

  si llega al fin del archivo sale del loop de lectura, y si todavia hay bets para enviar, se hace un ultimo envio. Finalmente se envia la SendDoneSignal() para indicarle al server que este cliente ya no enviara mas apuestas y que puede cerrar la conexion.

  #### `cambios en el server:`

  El server cambia el protocolo acorde a todo lo que va a enviar ahora el cliente. 

  se crean estos metodos para el protocolo para adquirir la informacion nueva de parte del cliente:
 ```python
  def recv_agency_id(self):
    return self.recv_bytes(1)

  def recv_number_of_bets(self):
      return self.recv_bytes(1)
 ```
  Se crea el metodo send_success_message para notificar al cliente que sus apuestas fueron procesadas correctamente:
  ```python
  def send_success_message(self):
      self.socket.sendall(b'\x01')
  ```

  finalmente, en el loop de recvs que hace el server para salir de el mismo y terminar la conexion con el cliente, el cliente debe enviarle la SendDoneSignal() la cual ocupa 1byte al igual que la agency_id.

  por ende cuando el server termina de procesar un chunk de apuestas y recibe que el agency_id es igual a cero (cero es la DoneSignal), sabe que el cliente no enviara mas apuestas y hace break del loop para poder terminar la conexion.
  ```python
  while True:  
    agency_id = client_connection.recv_agency_id()
    if agency_id is None:
        logging.error("action: receive_agency_id | result: fail | error: agency_id_not_received")
        client_connection.close()
        del self.clients_dictionary[client_id]
        return
    
    if agency_id < 1:
        break
  ```

  ## Ejercicio N°7:

  El server espera a que todos los clientes le envien sus bets y le pidan sus ganadores. Una vez que el server recibe todas las peticiones, procede a designar ganadores con el nuevo metodo choose_winner() y dentro ese metodo hace uso del nuevo metodo del protocolo para enviar los ganadores.

  ```python
  client_connection.send_winners(winners[agency_id])
  ```

  ```python
  def send_winners(self, winners):
    self.send_number(len(winners))
    for document in winners:
        self.send_number(int(document))
    return
  ```

  El server envia los ganadores al cliente con el siguiente formato:

  |cantidad_de_ganadores(4bytes) | dni_ganador1(4bytes) | dni_ganador2(4bytes) | ... |dni_ganador_n(4bytes)|

  En el cliente se agrega la peticion de los ganadores al server y se agrega al protocolo un metodo para recibir los mismos.
  
  ```go
  func (cp *ClientProtocol) AskForWinners() error {
	return cp.SendAll([]byte{0})
}

func (cp *ClientProtocol) ReceiveWinners() ([]int, error) {
	sizeBuf, err := cp.ReadAll(4)
	if err != nil {
		return nil, err
	}
	size := binary.BigEndian.Uint32(sizeBuf)
	winners := make([]int, size)
	for i := uint32(0); i < size; i++ {
		numBuf, err := cp.ReadAll(4)
		if err != nil {
			return nil, err
		}
		number := binary.BigEndian.Uint32(numBuf)
		winners[i] = int(number)
	}
	return winners, nil
}
```

 ## Ejercicio N°8:

 Se modifica el archivo server.py para hacer que el servidor ahora atienda clinetes en paralelo haciendo uso de threads.

 Se lanza un thread por cliente que se conecta y se guarda ese thread en una lista como atributo de la clase Server. Los threads son coordinados entre si con una Barrier para que ningun thread pueda enviar los ganadores del sorteo hasta que todos los threads de todos los clientes hayan enviado todas las apuestas:

 logging.info("action: agency_waiting__for_winners | result: success")
  ```python
  self.barrier.wait()
  # si ya estan todas las agencias esperando, sorteo
  winners = monitor.load_winners(agency)
  client_connection.send_winners(winners)
  ```

  Como se puede apreciar en el segmento de codigo anterior, ahora existe un monitor que se encarga de coordinar el acceso a Utils. Internamente UtilsMonitor usa un lock para que los archivos que abre Utils no sean abiertos por dos threads a la vez y asi evitar una race condition.

  Para el cierre del server, cuando se recibe una signal SIGINT o SIGTERM se ejecuta el signal_handler que se encarga de cerrar los sockets y joinear los threads:


  ```python
  def _signal_handler(self, sig, frame):
    #con este lock me aseguro que no se acepte ninguna conexion nueva/cree un thread mientras se esta cerrando el server
    with self._accept_lock:
        logging.Info("action: exit | result: success | reason: signal_received | signal: SIGTERM")
        self._shutting_down = True
        for client_id in list(self.clients_dictionary.keys()):
            self.clients_dictionary[client_id].close()
            del self.clients_dictionary[client_id]

        #agrego esto para destrabar los threads que puedan estar en la barrier
        if hasattr(self, 'barrier'):
            self.barrier.abort()
            
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        for thread in self.threads:
            thread.join()
  ```

  Por mas que haya un socket conectado al cliente que este en la operacion bloqueante del recv(), al hacerle shutdown y close eso lo destraba para que pueda terminar la ejecucion y se pueda luego joinear el thread correctamente, lo mismo con la barrier a la cual se le hace abort para destrabar cualquier hilo que haya podido estar bloqueado ahi. `self._accept_lock` es un lock que me asegura que mientras se esta ejecutando el handler para cerrar el server, no se estan creando en paralelo nuevas conexiones o nuevos threads que quedarian sin cerrar. Finalmente luego de que se ejecute el handler, el loop principal luego de agarrar el lock y antes de aceptar nuevas conexiones va a chequear el flag `_shutting_down` que es true y va a detener la ejecucion.

  ### _"En caso de que el alumno implemente el servidor en Python utilizando multithreading, deberán tenerse en cuenta las limitaciones propias del lenguaje."_

  python tiene un GIL (global interpreter lock) que es un mutex que previene a multiples threads de ejecutar bytecode de python en simultaneo.
  Esto hace que aunque hayan nucleos libres en mi cpu, python haga solo uso de uno para ejecutar bytecode, limitando las capacidades de concurrencia del lenguaje.

  Pero el GIL solo proteje la ejecucion del bytecode de python, no evita que se realicen operacion de lectura y escritura de archivos o de mensajeria a traves de sockets, y eso es mayoritariamente lo que sucede en este TP. El GIL reduce mucho el rendimiento en programas que son muy cpu intensive, que requieren de mucho procesamiento.

  Como en este trabajo hay muchas operaciones de sockets y lectura de archivos, el GIL se libera frecuentemente lo que hace que no sea inconsecuente tener threads.

 ## Cambios pedidos por el corrector:

 Me asegure de hacer un commit por cada cambio agregado asi que tambien se puede ir a ver que agrega cada commit del dia 4/9/25 para ver que se cambio facilmente.

se cambio el metodo sendBetInfo para que ahora envie el size del batch de bets que se esta por enviar y no la cantidad de bets como se enviaba anteriormente.

```go
func (cp *ClientProtocol) sendBetInfo(data []byte, size uint32) error {

	size_buffer := make([]byte, 4)
	binary.BigEndian.PutUint32(size_buffer, size)

	return cp.SendAll(append(size_buffer, data...))
}
```

se usan 4 bytes que se envian en bigEndian delante de las bets. Ahora el formato del paquete es el siguiente:


| size de las bets(4bytes) | (bet.1,bet.2,...,bet.n) |

dentro de cada bet:

| name_size(1byte) | name | surname_size(1byte) | surname | DNI(4bytes) | date_of_birth_size(1byte) | date of birth | number (4bytes) |


En el server ahora se hace un recv para recibir el size del batch en bytes y se hace un solo recv de ese size para recibir todo el batch de una vez:


en `handle_client_connection()`:

```python
size_of_batch = client_connection.recv_size_of_bets_batch()

batch_data = client_connection.recv_all(size_of_batch)
```

luego esa batch_data es enviada denuevo al protocolo para que la parsee y obtenga los datos necesarios de las bets.
```python
bet_info, offset = client_connection.parse_bet_info(batch_data, offset)
```
##

Luego para solucionar el caso en el que un thread podia estar trabado en la barrier mientras se ejecutaba el signal_handler, se agrego al metodo `_signal_handler(self, sig, frame)` lo siguiente:

```python
   if hasattr(self, 'barrier'):
    self.barrier.abort()
```

y en `handle_client_connection()` se agrego un catcheo de la excepcion producida por el abort:
```python
try:
  self.barrier.wait()
except threading.BrokenBarrierError:
  logging.info("action: barrier_broken | result: success")
  return
```
##
Finalmente para evitar que durante la ejecucion del `_signal_handler()` se crearan nuevas conexiones y/o nuevos hilos, se agrego un atributo al server llamado `self._accept_lock` el se necesita para poder ejecutar el signal handler o para poder aceptar conexiones y crear threads, pero ninguna de las dos en simultaneo.


```python
def _signal_handler(self, sig, frame):

        #con este lock me aseguro que no se acepte ninguna conexion nueva/cree un thread mientras se esta cerrando el server
        with self._accept_lock:
            logging.Info("action: exit | result: success | reason: signal_received | signal: SIGTERM")
            self._shutting_down = True
            for client_id in list(self.clients_dictionary.keys()):
                self.clients_dictionary[client_id].close()
                del self.clients_dictionary[client_id]

            #agrego esto para destrabar los threads que puedan estar en la barrier
            if hasattr(self, 'barrier'):
                self.barrier.abort()
                
            self._server_socket.shutdown(socket.SHUT_RDWR)
            self._server_socket.close()
            for thread in self.threads:
                thread.join()
```

y dentro del run:

```python
while not self._shutting_down:
  try:
    with self._accept_lock:
      if self._shutting_down:
        break
      client_connection = self.__accept_new_connection()
      if client_connection:
        self.client_id += 1
        self.clients_dictionary[self.client_id] = client_connection
        thread = Thread(target=self.__handle_client_connection, args=(self.client_id, client_connection, monitor))
        thread.start()
        self.threads.append(thread)
```
