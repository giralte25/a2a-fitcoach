# Copyright (c) 2026. Caso de uso A2A — FitCoach.

"""Servidor A2A — Expone el agente FitCoach como endpoint A2A.

Crea una aplicación Starlette (vía a2a-sdk) que:
  - Publica el AgentCard en /.well-known/agent.json
  - Atiende peticiones JSON-RPC del protocolo A2A en /
  - Ejecuta el agente FitCoach con streaming activado.

Uso:
    python fitness_server.py --port 5005

Variables de entorno (definirlas en un fichero .env):
    OPENAI_API_KEY / OPENAI_CHAT_MODEL_ID         (cliente OpenAI), o
    AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY  (cliente Azure OpenAI)
"""

from __future__ import annotations

import argparse

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from agent_framework.a2a import A2AExecutor
from dotenv import load_dotenv
from starlette.applications import Starlette

from fitness_agent import create_fitcoach_agent, get_fitcoach_agent_card

load_dotenv()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Servidor A2A del agente FitCoach")
    parser.add_argument("--host", default="localhost", help="Host de escucha (por defecto: localhost)")
    parser.add_argument("--port", type=int, default=5005, help="Puerto de escucha (por defecto: 5005)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    url = f"http://{args.host}:{args.port}/"

    # 1. Crear el agente y su tarjeta de presentación A2A.
    agent = create_fitcoach_agent()
    agent_card = get_fitcoach_agent_card(url)

    # 2. Envolver el agente en un ejecutor A2A (con streaming).
    executor = A2AExecutor(agent, stream=True)

    # 3. Construir el manejador de peticiones del protocolo A2A.
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    # 4. Montar las rutas (AgentCard + JSON-RPC) en una app Starlette.
    app = Starlette(
        routes=[
            *create_agent_card_routes(agent_card),
            *create_jsonrpc_routes(request_handler, "/"),
        ]
    )

    print(f"Iniciando servidor A2A: {agent_card.name}")
    print(f"  Escuchando : {url}")
    print(f"  AgentCard  : {url}.well-known/agent.json")
    print()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
