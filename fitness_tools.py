# Copyright (c) 2026. Caso de uso A2A — FitCoach.

"""Herramientas (function tools) del Agente Entrenador Personal "FitCoach".

Todas las funciones son cálculos deterministas (sin dependencias externas ni
base de datos), de modo que el servidor A2A puede ejecutarse en local sin
configuración adicional más allá del modelo de lenguaje.
"""

from __future__ import annotations

import json
from typing import Annotated

from agent_framework import tool
from pydantic import Field

# ---------------------------------------------------------------------------
# Tablas de referencia (valores MET aproximados por actividad)
# ---------------------------------------------------------------------------

# MET = Metabolic Equivalent of Task. Fuente aproximada: Compendium of Physical
# Activities. Sirve para estimar el gasto calórico de cada actividad.
MET_POR_ACTIVIDAD: dict[str, float] = {
    "caminar": 3.5,
    "correr": 9.8,
    "ciclismo": 7.5,
    "natacion": 8.0,
    "yoga": 2.5,
    "pesas": 6.0,
    "hiit": 10.0,
    "elliptica": 5.0,
    "remo": 7.0,
    "saltar_cuerda": 11.0,
}


# ---------------------------------------------------------------------------
# Herramientas expuestas al agente
# ---------------------------------------------------------------------------

@tool(approval_mode="never_require")
def calcular_imc(
    peso_kg: Annotated[float, Field(description="Peso de la persona en kilogramos.")],
    altura_cm: Annotated[float, Field(description="Altura de la persona en centímetros.")],
) -> str:
    """Calcula el Índice de Masa Corporal (IMC) y devuelve su categoría OMS."""
    altura_m = altura_cm / 100.0
    imc = peso_kg / (altura_m * altura_m)

    if imc < 18.5:
        categoria = "Bajo peso"
    elif imc < 25:
        categoria = "Peso normal"
    elif imc < 30:
        categoria = "Sobrepeso"
    else:
        categoria = "Obesidad"

    return json.dumps(
        {"imc": round(imc, 1), "categoria": categoria},
        ensure_ascii=False,
    )


@tool(approval_mode="never_require")
def metabolismo_basal(
    peso_kg: Annotated[float, Field(description="Peso en kilogramos.")],
    altura_cm: Annotated[float, Field(description="Altura en centímetros.")],
    edad: Annotated[int, Field(description="Edad en años.")],
    sexo: Annotated[str, Field(description="Sexo biológico: 'hombre' o 'mujer'.")],
) -> str:
    """Estima la Tasa Metabólica Basal (TMB) con la fórmula de Mifflin-St Jeor."""
    base = 10 * peso_kg + 6.25 * altura_cm - 5 * edad
    if sexo.strip().lower().startswith("h"):
        tmb = base + 5
    else:
        tmb = base - 161

    return json.dumps(
        {
            "tmb_kcal_dia": round(tmb),
            "descripcion": "Calorías que el cuerpo gasta en reposo absoluto durante 24h.",
        },
        ensure_ascii=False,
    )


@tool(approval_mode="never_require")
def calorias_quemadas(
    actividad: Annotated[
        str,
        Field(description="Actividad física: caminar, correr, ciclismo, natacion, yoga, pesas, hiit, elliptica, remo, saltar_cuerda."),
    ],
    minutos: Annotated[int, Field(description="Duración de la actividad en minutos.")],
    peso_kg: Annotated[float, Field(description="Peso de la persona en kilogramos.")],
) -> str:
    """Estima las calorías quemadas en una actividad usando su valor MET."""
    clave = actividad.strip().lower().replace(" ", "_")
    met = MET_POR_ACTIVIDAD.get(clave)

    if met is None:
        return json.dumps(
            {
                "error": f"Actividad '{actividad}' no reconocida.",
                "actividades_disponibles": sorted(MET_POR_ACTIVIDAD.keys()),
            },
            ensure_ascii=False,
        )

    # kcal = MET * peso(kg) * tiempo(horas)
    kcal = met * peso_kg * (minutos / 60.0)

    return json.dumps(
        {
            "actividad": clave,
            "minutos": minutos,
            "met": met,
            "calorias_estimadas": round(kcal),
        },
        ensure_ascii=False,
    )


@tool(approval_mode="never_require")
def recomendar_rutina(
    objetivo: Annotated[
        str,
        Field(description="Objetivo del usuario: 'perder_peso', 'ganar_musculo' o 'mantener'."),
    ],
    nivel: Annotated[
        str,
        Field(description="Nivel de experiencia: 'principiante', 'intermedio' o 'avanzado'."),
    ],
    dias: Annotated[int, Field(description="Número de días de entrenamiento por semana (1-7).")],
) -> str:
    """Genera una rutina semanal de entrenamiento adaptada al objetivo y nivel."""
    objetivo = objetivo.strip().lower()
    nivel = nivel.strip().lower()
    dias = max(1, min(7, dias))

    bloques_por_objetivo = {
        "perder_peso": ["HIIT 20 min", "Cardio moderado 30 min", "Circuito full-body"],
        "ganar_musculo": ["Tren superior (empuje)", "Tren inferior", "Tren superior (tirón)"],
        "mantener": ["Fuerza full-body", "Cardio suave 30 min", "Movilidad y core"],
    }
    bloques = bloques_por_objetivo.get(objetivo, bloques_por_objetivo["mantener"])

    series_por_nivel = {"principiante": 2, "intermedio": 3, "avanzado": 4}
    series = series_por_nivel.get(nivel, 3)

    plan = []
    for dia in range(1, dias + 1):
        foco = bloques[(dia - 1) % len(bloques)]
        plan.append(
            {
                "dia": dia,
                "foco": foco,
                "series_por_ejercicio": series,
                "descanso_seg": 60 if objetivo == "perder_peso" else 90,
            }
        )

    return json.dumps(
        {
            "objetivo": objetivo,
            "nivel": nivel,
            "dias_semana": dias,
            "plan": plan,
        },
        ensure_ascii=False,
    )


@tool(approval_mode="never_require")
def plan_hidratacion(
    peso_kg: Annotated[float, Field(description="Peso en kilogramos.")],
    minutos_ejercicio: Annotated[int, Field(description="Minutos de ejercicio previstos en el día.")] = 0,
) -> str:
    """Calcula la ingesta diaria de agua recomendada (base + extra por ejercicio)."""
    # Base: ~35 ml por kg de peso corporal.
    litros_base = (peso_kg * 35) / 1000.0
    # Extra: ~0.5 L por cada 30 min de ejercicio.
    litros_extra = (minutos_ejercicio / 30.0) * 0.5
    total = litros_base + litros_extra

    return json.dumps(
        {
            "litros_base": round(litros_base, 2),
            "litros_extra_ejercicio": round(litros_extra, 2),
            "litros_totales_dia": round(total, 2),
        },
        ensure_ascii=False,
    )


# Lista de herramientas para registrar en el agente.
FITNESS_TOOLS = [
    calcular_imc,
    metabolismo_basal,
    calorias_quemadas,
    recomendar_rutina,
    plan_hidratacion,
]
