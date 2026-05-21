import argparse
import asyncio
import logging

from typing import List

from day_schema import Schedule
from pydantic import ValidationError
from snmp_schema import SNMPSchema
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.proto.rfc1902 import (
    Integer, OctetString, ObjectIdentifier, IpAddress,
    Counter32, Counter64, Gauge32, TimeTicks, Unsigned32
)
from pysnmp.proto.rfc1905 import Null

# Logs (En archivo snmp.log) y tambien en consola
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("snmp.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def seconds_until_interval(minutes: int):
    return minutes * 60


# Este metodo es el encargado de realizar las consultas
async def snmp_get_run(snmp_data: SNMPSchema):
    snmp_engine = SnmpEngine()

    try:
        transport_target = await UdpTransportTarget.create(
            (str(snmp_data.ip), snmp_data.port),
            timeout=1.5,
            retries=1
        )

        iterator = get_cmd(
            snmp_engine,
            CommunityData(snmp_data.community, mpModel=1),
            transport_target,
            ContextData(),
            *[
                ObjectType(ObjectIdentity(oid))
                for oid in snmp_data.oids
            ]
        )

        error_indication, error_status, error_index, var_binds = await iterator

        if error_indication:
            logger.error(f"[{snmp_data.ip}] SNMP error: {error_indication}")

            return {
                "success": False,
                "error": str(error_indication)
            }

        if error_status:

            logger.error(
                f"[{snmp_data.ip}] SNMP status error: "
                f"{error_status.prettyPrint()}"
            )

            return {
                "success": False,
                "error": error_status.prettyPrint()
            }

        results = []

        for var_bind in var_binds:

            oid, raw_value = var_bind
            processed_value = None

            try:

                if isinstance(
                    raw_value,
                    (
                        Integer,
                        Unsigned32,
                        Counter32,
                        Counter64,
                        Gauge32,
                        TimeTicks
                    )
                ):

                    processed_value = int(raw_value)

                elif isinstance(raw_value, OctetString):

                    processed_value = raw_value.prettyPrint()

                elif isinstance(raw_value, ObjectIdentifier):

                    processed_value = raw_value.prettyPrint()

                elif isinstance(raw_value, IpAddress):

                    processed_value = str(raw_value)

                elif isinstance(raw_value, Null):

                    processed_value = None

                else:

                    processed_value = raw_value.prettyPrint()

            except Exception:

                processed_value = str(raw_value)

            result = {
                "oid": oid.prettyPrint(),
                "value": processed_value,
                "type": type(raw_value).__name__,
            }

            results.append(result)

            logger.info(
                f"[{snmp_data.ip}] "
                f"{result['oid']} = {result['value']}"
            )

        return {
            "success": True,
            "results": results
        }

    except Exception as e:

        logger.exception(f"[{snmp_data.ip}] Error SNMP GET: {e}")

        return {
            "success": False,
            "error": str(e)
        }

    finally:

        snmp_engine.close_dispatcher()


# Este metodo es el que realiza de forma ciclica por el periodo establecido
async def task(snmp_data: SNMPSchema, schedule: Schedule):

    logging.info(
        f"Ejecución cada {schedule.interval_minutes} minuto(s)"
    )

    while True:

        wait_time = seconds_until_interval(
            schedule.interval_minutes
        )

        logging.info(
            f"Esperando {wait_time:.0f}s hasta la siguiente ejecución"
        )

        await asyncio.sleep(wait_time)

        logging.info(
            f"Iniciando llamadas SNMP "
            f"(intervalo {schedule.interval_minutes}min)"
        )

        await snmp_get_run(snmp_data)


# Funcion que se ejecuta al correr el script.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Scheduler de llamadas a SNMPGET (con intervalo)."
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        dest="interval_minutes",
        help="Intervalo en minutos entre ejecuciones",
    )

    args = parser.parse_args()

    try:

        schedule = Schedule(
            interval_minutes=args.interval_minutes,
        )


        # Aqui se define los parametros del equipo
        ## Los oids son los ID con los que se obtiene un parámetro en concreto de los equipos
        ## por ejemplo, nivel de bateria, etc. Estos se encuentran en el MIB.
        snmp_data = SNMPSchema(
            ip="127.0.0.1",
            port=161,
            community="public",
            oids=[
                "1.3.6.1.2.1.1.1.0"
            ]
        )

        try:

            asyncio.run(task(snmp_data, schedule))

        except KeyboardInterrupt:

            logging.info("Scheduler detenido por el usuario (Ctrl+C)")
            print("Scheduler detenido por el usuario")

    except ValidationError as ve:

        logging.error(f"Error de configuración: {ve}")
        print("Error de configuración:", ve)

    except Exception as e:

        logging.error(f"Error inesperado en el scheduler: {e}")
        print("Error inesperado:", e)