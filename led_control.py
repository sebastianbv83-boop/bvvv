#!/usr/bin/env python3
"""Find and control a cheap Bluetooth LE LED light from the computer.

Examples:
    python led_control.py scan
    python led_control.py on
    python led_control.py color 255 0 128
    python led_control.py brightness 40 --address AA:BB:CC:DD:EE:FF
    python led_control.py services --address AA:BB:CC:DD:EE:FF
"""
import argparse
import asyncio
import sys

from bleak import BleakClient, BleakScanner


def uuid16(short):
    return f"0000{short:04x}-0000-1000-8000-00805f9b34fb"


PROTOCOLS = {
    "elk": {  # ELK-BLEDOM, duoCo Strip, Lotus Lamp, MELK...
        "service": uuid16(0xFFF0),
        "char": uuid16(0xFFF3),
        "on": lambda: [0x7E, 0x00, 0x04, 0xF0, 0x00, 0x01, 0xFF, 0x00, 0xEF],
        "off": lambda: [0x7E, 0x00, 0x04, 0x00, 0x00, 0x00, 0xFF, 0x00, 0xEF],
        "color": lambda r, g, b: [0x7E, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xEF],
        "brightness": lambda p: [0x7E, 0x00, 0x01, p, 0x00, 0x00, 0x00, 0x00, 0xEF],
    },
    "triones": {  # Triones, HappyLighting, LEDBLE, QHM, Dream~...
        "service": uuid16(0xFFD5),
        "char": uuid16(0xFFD9),
        "on": lambda: [0xCC, 0x23, 0x33],
        "off": lambda: [0xCC, 0x24, 0x33],
        "color": lambda r, g, b: [0x56, r, g, b, 0x00, 0xF0, 0xAA],
        "brightness": None,  # emulated by scaling white
    },
}

LED_NAME_HINTS = ("ELK", "BLEDOM", "MELK", "DUOCO", "LED", "TRIONES", "QHM", "DREAM", "LIGHT", "LAMP", "STRIP")


def signal_label(rssi):
    if rssi >= -55:
        return "muy cerca"
    if rssi >= -70:
        return "cerca"
    if rssi >= -85:
        return "lejos"
    return "muy lejos"


def looks_like_led(name, service_uuids):
    known = {p["service"] for p in PROTOCOLS.values()}
    return bool(known & set(service_uuids)) or any(h in (name or "").upper() for h in LED_NAME_HINTS)


async def scan(timeout):
    print(f"Escaneando {timeout:.0f} s... (cierra la app del celular para que la luz sea visible)\n")
    found = await BleakScanner.discover(timeout=timeout, return_adv=True)
    rows = sorted(found.values(), key=lambda da: da[1].rssi, reverse=True)
    for dev, adv in rows:
        name = adv.local_name or dev.name or "(sin nombre)"
        mark = "💡" if looks_like_led(name, adv.service_uuids) else "  "
        print(f"{mark} {dev.address:<40} {adv.rssi:>4} dBm  {signal_label(adv.rssi):<10} {name}")
    print("\n💡 = probable luz LED. Acércate con el portátil: la señal (dBm) sube cuanto más cerca estés.")
    return rows


async def find_led(timeout):
    found = await BleakScanner.discover(timeout=timeout, return_adv=True)
    leds = [(d, a) for d, a in found.values() if looks_like_led(a.local_name or d.name, a.service_uuids)]
    if not leds:
        sys.exit("No encontré ninguna luz LED. Ejecuta 'scan' y pasa la dirección con --address.")
    dev, adv = max(leds, key=lambda da: da[1].rssi)
    print(f"Usando {adv.local_name or dev.name} [{dev.address}]")
    return dev.address


def detect_protocol(client, forced):
    if forced != "auto":
        return PROTOCOLS[forced]
    uuids = {s.uuid.lower() for s in client.services}
    for proto in PROTOCOLS.values():
        if proto["service"] in uuids:
            return proto
    sys.exit("Protocolo no reconocido. Ejecuta 'services' y comparte el resultado.")


async def run(args):
    if args.cmd == "scan":
        await scan(args.timeout)
        return

    address = args.address or await find_led(args.timeout)
    async with BleakClient(address) as client:
        if args.cmd == "services":
            for service in client.services:
                print(f"Servicio {service.uuid}")
                for ch in service.characteristics:
                    print(f"   {ch.uuid}  {','.join(ch.properties)}")
            return

        proto = detect_protocol(client, args.protocol)
        if args.cmd in ("on", "off"):
            payload = proto[args.cmd]()
        elif args.cmd == "color":
            payload = proto["color"](args.r, args.g, args.b)
        elif args.cmd == "brightness":
            if proto["brightness"]:
                payload = proto["brightness"](args.percent)
            else:
                level = round(255 * args.percent / 100)
                payload = proto["color"](level, level, level)
        await client.write_gatt_char(proto["char"], bytes(payload), response=False)
        print(f"Enviado: {bytes(payload).hex(' ')}")


def byte(value):
    v = int(value)
    if not 0 <= v <= 255:
        raise argparse.ArgumentTypeError("debe estar entre 0 y 255")
    return v


def percent(value):
    v = int(value)
    if not 1 <= v <= 100:
        raise argparse.ArgumentTypeError("debe estar entre 1 y 100")
    return v


def main():
    parser = argparse.ArgumentParser(description="Control de luz LED Bluetooth")
    parser.add_argument("--address", help="Dirección MAC/UUID de la luz (si no, se busca sola)")
    parser.add_argument("--protocol", choices=["auto", *PROTOCOLS], default="auto")
    parser.add_argument("--timeout", type=float, default=8.0, help="Segundos de escaneo")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan", help="Buscar dispositivos Bluetooth cercanos")
    sub.add_parser("services", help="Listar servicios de la luz (diagnóstico)")
    sub.add_parser("on", help="Encender")
    sub.add_parser("off", help="Apagar")
    c = sub.add_parser("color", help="Cambiar color RGB")
    c.add_argument("r", type=byte)
    c.add_argument("g", type=byte)
    c.add_argument("b", type=byte)
    b = sub.add_parser("brightness", help="Brillo 1-100")
    b.add_argument("percent", type=percent)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
