# Copyright (c) 2026. Caso de uso A2A — FitCoach.

"""Definición del Agente Entrenador Personal "FitCoach" y su AgentCard A2A.

Este módulo concentra:
  - La selección del cliente de modelo de lenguaje (OpenAI o Azure OpenAI).
  - La creación del agente Agent Framework con sus herramientas.
  - La fábrica del AgentCard que se publica en /.well-known/agent.json.
"""

from __future__ import annotations

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from agent_framework import Agent

from fitness_tools import FITNESS_TOOLS

# ---------------------------------------------------------------------------
# Instrucciones del agente (system prompt)
# ---------------------------------------------------------------------------

FITCOACH_INSTRUCTIONS = """\
Eres "FitCoach", un entrenador personal virtual experto en fitness, nutrición \
deportiva e hidratación. Respondes siempre en español, con tono motivador, \
cercano y profesional.

Reglas de comportamiento:
- Usa SIEMPRE las herramientas disponibles para cualquier cálculo (IMC, \
metabolismo basal, calorías quemadas, rutinas o hidratación). Nunca inventes \
los números: apóyate en los resultados que devuelven las herramientas.
- Si te falta algún dato necesario para una herramienta (peso, altura, edad, \
sexo, objetivo, nivel o días), pídelo de forma breve antes de calcular.
- Tras dar un resultado numérico, añade una recomendación práctica y clara.
- Recuerda al usuario, cuando sea pertinente, que esto es orientativo y no \
sustituye el consejo de un profesional médico.
"""


# ---------------------------------------------------------------------------
# Cliente de modelo de lenguaje
# ---------------------------------------------------------------------------

def build_chat_client():
    """Devuelve un cliente de chat según las variables de entorno disponibles.

    OpenAIChatClient detecta automáticamente el routing:
    - Azure OpenAI: define AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY
      (y opcionalmente AZURE_OPENAI_CHAT_MODEL + AZURE_OPENAI_API_VERSION).
    - OpenAI estándar: define OPENAI_API_KEY.
    """
    from agent_framework.openai import OpenAIChatClient

    return OpenAIChatClient()


# ---------------------------------------------------------------------------
# Fábrica del agente
# ---------------------------------------------------------------------------

def create_fitcoach_agent() -> Agent:
    """Crea el agente FitCoach con sus herramientas registradas."""
    return Agent(
        client=build_chat_client(),
        name="FitCoach",
        instructions=FITCOACH_INSTRUCTIONS,
        tools=FITNESS_TOOLS,
    )


# ---------------------------------------------------------------------------
# Fábrica del AgentCard (metadatos públicos A2A)
# ---------------------------------------------------------------------------

def get_fitcoach_agent_card(url: str) -> AgentCard:
    """Devuelve el AgentCard A2A que describe las capacidades de FitCoach."""
    capabilities = AgentCapabilities(streaming=True, push_notifications=False)

    skills = [
        AgentSkill(
            id="calculo_imc",
            name="Cálculo de IMC",
            description="Calcula el Índice de Masa Corporal y su categoría.",
            tags=["fitness", "salud", "imc"],
            examples=["¿Cuál es mi IMC si peso 80 kg y mido 178 cm?"],
        ),
        AgentSkill(
            id="metabolismo_basal",
            name="Metabolismo basal",
            description="Estima las calorías que gasta el cuerpo en reposo (TMB).",
            tags=["fitness", "nutricion", "calorias"],
            examples=["¿Cuál es mi metabolismo basal? Hombre, 30 años, 80 kg, 178 cm."],
        ),
        AgentSkill(
            id="gasto_calorico",
            name="Calorías quemadas",
            description="Estima las calorías quemadas en una actividad física.",
            tags=["fitness", "cardio", "calorias"],
            examples=["¿Cuántas calorías quemo corriendo 45 minutos si peso 75 kg?"],
        ),
        AgentSkill(
            id="rutina_entrenamiento",
            name="Rutina de entrenamiento",
            description="Genera una rutina semanal según objetivo y nivel.",
            tags=["fitness", "rutina", "entrenamiento"],
            examples=["Quiero una rutina para ganar músculo, nivel intermedio, 4 días."],
        ),
        AgentSkill(
            id="hidratacion",
            name="Plan de hidratación",
            description="Calcula la ingesta diaria de agua recomendada.",
            tags=["fitness", "salud", "hidratacion"],
            examples=["¿Cuánta agua debo beber si peso 70 kg y entreno 60 minutos?"],
        ),
    ]

    return AgentCard(
        name="FitCoach",
        description="Entrenador personal virtual: IMC, calorías, rutinas e hidratación.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=capabilities,
        supported_interfaces=[AgentInterface(url=url, protocol_binding="JSONRPC")],
        skills=skills,
    )
