# Copyright (c) 2026. Caso de uso A2A — FitCoach.

"""Cliente A2A — Consume el agente remoto FitCoach.

Este script demuestra el flujo cliente del protocolo A2A:
  1. Descubrir el agente resolviendo su AgentCard (/.well-known/agent.json).
  2. Crear un A2AAgent que envuelve el endpoint remoto.
  3. Lanzar consultas en modo bloqueante (request/response) y en streaming.

Uso:
    python fitness_client.py
    # o pasando preguntas propias:
    python fitness_client.py "¿Cuánta agua debo beber si peso 72 kg y entreno 50 min?"

Variable de entorno:
    A2A_AGENT_HOST — URL del servidor A2A (por defecto http://localhost:5005/)
"""

from __future__ import annotations

import asyncio
import os
import sys

# Forzar UTF-8 en la salida estándar (Windows usa CP1252 por defecto)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent
from dotenv import load_dotenv

load_dotenv()

# Preguntas de demostración (se usan si no se pasa ninguna por línea de comandos).
PREGUNTAS_DEMO = [
    "Hola, ¿qué puedes hacer por mí?",
    "Peso 80 kg y mido 178 cm. ¿Cuál es mi IMC y qué significa?",
    "Quiero perder peso. Dame una rutina de 4 días para nivel principiante.",
]


async def main() -> None:
    host = os.getenv("A2A_AGENT_HOST", "http://localhost:5005/")
    preguntas = sys.argv[1:] or PREGUNTAS_DEMO

    print(f"Conectando con el agente A2A en: {host}")

    async with httpx.AsyncClient(timeout=120.0) as http_client:
        # 1. Resolver el AgentCard para descubrir las capacidades del agente.
        resolver = A2ACardResolver(httpx_client=http_client, base_url=host)
        agent_card = await resolver.get_agent_card()
        print(f"Agente encontrado: {agent_card.name} — {agent_card.description}\n")

        # 2. Crear el agente cliente que envuelve el endpoint remoto.
        async with A2AAgent(
            name=agent_card.name,
            description=agent_card.description,
            agent_card=agent_card,
            url=host,
        ) as agent:
            # 3a. Las primeras preguntas en modo request/response (bloqueante).
            for pregunta in preguntas[:-1]:
                print(f"Tú: {pregunta}")
                respuesta = await agent.run(pregunta)
                print(f"FitCoach: {respuesta.text}\n")

            # 3b. La última pregunta en modo streaming (SSE) para ver el progreso.
            ultima = preguntas[-1]
            print(f"Tú (streaming): {ultima}")
            print("FitCoach: ", end="", flush=True)
            stream = agent.run(ultima, stream=True)
            async for update in stream:
                for content in update.contents:
                    if content.text:
                        print(content.text, end="", flush=True)
            print("\n")


if __name__ == "__main__":
    asyncio.run(main())
