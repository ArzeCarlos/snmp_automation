# SNMP Async Polling Scheduler

Sistema de automatización de consultas SNMP mediante polling asíncrono utilizando Python y `pysnmp`.

El proyecto permite ejecutar consultas `SNMP GET` de manera periódica sobre dispositivos de red utilizando `asyncio`, registrando resultados y errores tanto en consola como en archivo de logs.

---

## Características

- Consultas SNMP asíncronas
- Scheduler configurable por intervalo
- Soporte para múltiples OIDs
- Validación mediante Pydantic
- Manejo de errores SNMP
- Logging en consola y archivo
- Compatible con SNMP v2c
- Conversión automática de tipos SNMP

---

## Tecnologías utilizadas

- Python 3.10+
- asyncio
- pysnmp
- pydantic

---

## Instalación

### Clonar el repositorio

```bash
git clone https://github.com/ArzeCarlos/snmp_automation
cd snmp_automation
```

````

### Crear entorno virtual

Linux / Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Dependencias principales

```txt
pysnmp
pydantic
```

---

## Estructura del proyecto

```text
project/
│
├── main.py
├── snmp_schema.py
├── day_schema.py
├── snmp.log
├── requirements.txt
└── README.md
```

---

## Configuración

### SNMPSchema

Define los parámetros de conexión SNMP:

```python
SNMPSchema(
    ip="127.0.0.1",
    port=161,
    community="public",
    oids=[
        "1.3.6.1.2.1.1.1.0"
    ]
)
```

---

## Ejecución

### Ejecutar el scheduler

```bash
python main.py --interval 1
```

---

## Parámetros disponibles

| Parámetro    | Descripción                               |
| ------------ | ----------------------------------------- |
| `--interval` | Intervalo en minutos entre consultas SNMP |

---

## Ejemplo de ejecución

```bash
python main.py --interval 5
```

Esto ejecuta consultas SNMP cada 5 minutos.

---

## Ejemplo de salida

```text
2026-05-21 10:00:00 - INFO - Ejecución cada 1 minuto(s)
2026-05-21 10:00:00 - INFO - Iniciando llamadas SNMP
2026-05-21 10:00:01 - INFO - [127.0.0.1] 1.3.6.1.2.1.1.1.0 = Linux localhost
```

---

## Logging

Los logs se guardan en:

```
snmp.log
```

También se muestran en consola en tiempo real.

---

## OIDs comunes

| Métrica   | OID               |
| --------- | ----------------- |
| SysDescr  | 1.3.6.1.2.1.1.1.0 |
| SysUptime | 1.3.6.1.2.1.1.3.0 |
| Hostname  | 1.3.6.1.2.1.1.5.0 |

---

## Manejo de errores

El sistema detecta automáticamente:

- Timeout SNMP
- Community inválida
- Host inaccesible
- OID inválido
- Errores de parsing

---

## Mejoras futuras

- Soporte SNMP v3
- SNMP WALK
- Polling concurrente masivo
- Exportación Prometheus
- Persistencia en base de datos
- Dockerización
- API REST
- Dashboard web

---

## Licencia

MIT License

---

## Autor

Proyecto de automatización SNMP con Python y asyncio -- Carlos Arze.

```

```
````
