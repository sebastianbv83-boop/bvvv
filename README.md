# Control de luz LED Bluetooth desde el computador

Dos formas de encontrar y controlar una luz LED Bluetooth (BLE) barata desde el computador.

## La forma más fácil (3 pasos)

1. Instala Python desde <https://www.python.org/downloads/>.
   En Windows, **marca la casilla "Add Python to PATH"** durante la instalación.
2. Descarga esta carpeta: en GitHub, botón verde **Code → Download ZIP**, y descomprímela.
3. Cierra la app Govee del celular y haz **doble clic** en:
   - Windows: `iniciar-windows.bat`
   - Mac: `iniciar-mac.command` (si te bloquea: clic derecho → Abrir)

Se abre una ventana que busca la luz sola y te muestra un menú: escribe `E` para encender,
`A` para apagar, un número para elegir color, `B` para el brillo, y pulsa Enter.

## Detalles técnicos

Protocolos soportados:

| Protocolo | Apps del celular | Nombre típico de la luz |
|---|---|---|
| Govee BLE | Govee Home | `Govee_H6…`, `ihoment_H6…`, `GBK_H6…`, `Minger_H6…` |
| ELK-BLEDOM (servicio `FFF0`) | duoCo Strip, Lotus Lamp X, Lotus Lantern | `ELK-BLEDOM`, `MELK-…`, `duoCo…` |
| Triones (servicio `FFD5`) | HappyLighting, Triones, LEDBLE | `Triones-…`, `LEDBLE-…`, `QHM-…`, `Dream~…` |

> **Antes de empezar:** enciende la luz y **cierra la app del celular** (o apaga el Bluetooth del
> celular). Estas luces solo aceptan una conexión a la vez.

## Opción 1: página web (sin instalar nada)

Funciona en **Chrome o Edge** (Windows, macOS, Linux, Android). Safari y Firefox no soportan Web Bluetooth.

1. Descarga este repositorio.
2. En la carpeta, ejecuta `python -m http.server 8000` y abre <http://localhost:8000>
   (o simplemente abre `index.html` con Chrome).
3. Pulsa **Buscar y conectar**, elige tu luz en la lista y contrólala: encender, apagar, color y brillo.

En Linux quizá debas activar `chrome://flags/#enable-experimental-web-platform-features`.

## Opción 2: script de Python (también sirve para ubicar la luz)

```bash
pip install -r requirements.txt

python led_control.py scan                # lista dispositivos cercanos con la intensidad de señal
python led_control.py on
python led_control.py off
python led_control.py color 255 0 128     # rojo, verde, azul (0-255)
python led_control.py brightness 40       # 1-100
python led_control.py --address AA:BB:CC:DD:EE:FF on
python led_control.py --address AA:BB:CC:DD:EE:FF services   # diagnóstico
```

### Cómo ubicar la luz

`scan` marca con 💡 las probables luces LED y muestra la señal en dBm. Para saber dónde está
físicamente, repite `scan` mientras te mueves con el portátil: cuanto más alto el número
(p. ej. `-45` es más fuerte que `-80`), más cerca estás.

## Si no funciona

- Ejecuta `python led_control.py --address <dirección> services` y comparte la salida:
  con ella se puede añadir el protocolo de tu luz.
- Algunos modelos Govee muy recientes cifran la conexión Bluetooth y no responden; en ese caso dime el modelo (empieza por `H`, viene en la caja o en la app).
- Philips Hue o Magic Home Wi-Fi usan otros protocolos y no están soportadas todavía.
