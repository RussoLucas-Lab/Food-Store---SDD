## Context

Se parte de un proyecto Food Store sin backend implementado, solo documentación y plan de changes. El objetivo es establecer una base técnica y arquitectónica robusta, siguiendo una estructura en capas que facilite la escalabilidad, el testing y la posterior extensión por features. Se requiere preparar todo lo necesario para que los siguientes changes agreguen lógica real sin deuda técnica ni improvisación.

## Goals / Non-Goals

**Goals:**
- Definir estructura de carpetas y módulos backend según clean/hexagonal architecture (config, repository, unit-of-work, models, tests)
- Implementar patrón Repository y Unit of Work reusable para todo el dominio
- Crear modelos base (categoría, ingrediente, producto, usuario, cliente) sin lógica de negocio, solo estructura
- Configuración de entorno multiplataforma (dev/prod/test) con variables centralizadas y seeds de ejemplo
- Dejar lista la base para integración de tests automáticos (estructura, ejemplos vacíos)
- Documentar dependencias y convenciones de arquitectura para onboarding rápido

**Non-Goals:**
- No implementar endpoints, routes ni lógica de dominio específica (eso se hará en otros changes)
- No configurar integración continua/entrega (ci/cd)
- No crear lógica de negocio ni validaciones (solo estructura y contratos base)

## Decisions

- Se elige arquitectura en capas (clean/hexagonal) para separar dependencias y facilitar evolución/fork de features
- Se usa patrón Repository para persistencia y Unit of Work para orquestar transacciones/operaciones atómicas
- Configuración mediante archivos .env y carpeta config/, soportando variables sensibles y no sensibles
- Modelos iniciales en models/, una clase por modelo de dominio, sin atributos computados ni métodos de negocio
- Base para seeds en scripts/ o setup/, exportando datos mínimos para dev/test
- Testing: crear carpeta tests/ y ejemplo de test runner, pero sin cobertura real hasta que haya lógica implementada
- Documentación de contratos y convenciones de nombres en README o docs/ propios del backend

## Risks / Trade-offs

- [Rigid structure] → Mitigado permitiendo carpetas feature-slice a futuro si es necesario
- [Re-trabajo en modelos] → Mitigado dejando modelos minimalistas/extensibles
- [Fuga de configuración sensible] → Usar .env y excluir con .gitignore
- [Demora inicial] → Justificada para acelerar velocidad y calidad en fases siguientes con base sólida
