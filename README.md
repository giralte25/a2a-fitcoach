# FitCoach — Comunicación cliente-servidor con el protocolo A2A

Caso de uso **nuevo y autónomo** que demuestra el protocolo **A2A (Agent2Agent)**
con [Microsoft Agent Framework](https://github.com/microsoft/agent-framework).

**FitCoach** es un *entrenador personal virtual*: un agente que se **hospeda** como
servidor A2A y un **cliente** que lo **consume** de forma remota mediante el
protocolo estándar A2A (descubrimiento por `AgentCard` + JSON-RPC + streaming SSE).

> Inspirado en los ejemplos oficiales de hosting
> ([04-hosting/a2a](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/a2a))
> y de cliente
> ([02-agents/a2a](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/a2a)),
> pero con un dominio totalmente nuevo (fitness / salud).

## ¿Qué hace el agente?

FitCoach responde en español y usa *function tools* deterministas para no inventar números:

| Herramienta | Descripción |
| --- | --- |
| `calcular_imc` | Índice de Masa Corporal y categoría (OMS). |
| `metabolismo_basal` | Tasa Metabólica Basal (fórmula Mifflin-St Jeor). |
| `calorias_quemadas` | Gasto calórico por actividad usando valores MET. |
| `recomendar_rutina` | Rutina semanal según objetivo, nivel y días. |
| `plan_hidratacion` | Litros de agua recomendados al día. |

## Estructura

```
a2a-fitcoach/
├── fitness_tools.py     # Function tools (cálculos deterministas)
├── fitness_agent.py     # Agente FitCoach + AgentCard + selección de cliente LLM
├── fitness_server.py    # Servidor A2A (hosting)
├── fitness_client.py    # Cliente A2A (consumo remoto)
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos previos

- Python 3.10+
- Una clave de **OpenAI** o un recurso de **Azure OpenAI**.

## Instalación

```bash
cd a2a-fitcoach
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows (PowerShell)
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Copia el fichero de variables de entorno y rellénalo:

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
```

## Ejecución

### 1. Arrancar el servidor A2A (terminal 1)

```bash
python fitness_server.py --port 5005
```

Esto publica:
- El `AgentCard` en `http://localhost:5005/.well-known/agent.json`
- El endpoint JSON-RPC del protocolo A2A en `http://localhost:5005/`

### 2. Ejecutar el cliente A2A (terminal 2)

```bash
python fitness_client.py
```

O con tu propia pregunta:

```bash
python fitness_client.py "¿Cuántas calorías quemo corriendo 45 min si peso 75 kg?"
```

## Flujo A2A demostrado

1. **Descubrimiento**: el cliente resuelve el `AgentCard` con `A2ACardResolver`.
2. **Conexión**: crea un `A2AAgent` que envuelve el endpoint remoto.
3. **Request/response**: `await agent.run("...")` espera la respuesta completa.
4. **Streaming**: `agent.run("...", stream=True)` recibe el progreso vía SSE.

## Notas

- El servidor selecciona automáticamente el cliente LLM: usa **Azure OpenAI** si
  está definido `AZURE_OPENAI_ENDPOINT`, y en caso contrario **OpenAI**.
- Los cálculos son orientativos y no sustituyen el consejo de un profesional médico.
