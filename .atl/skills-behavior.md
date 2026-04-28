# Agent Skills Behavior – Food Store (OPSX/SDD)

Este archivo define CÓMO el agente debe utilizar las skills disponibles, incluyendo la capacidad de descubrir nuevas mediante `find-skills`.

Complementa al `skill-registry.md` (fuente de verdad de qué skills existen).

---

## Principio general

El agente debe:

1. Usar primero las skills conocidas del registry
2. Si no alcanza, buscar nuevas skills con `find-skills`
3. Evitar reinventar soluciones ya existentes

---

## Skill: find-skills

**Descripción:**
Permite descubrir nuevas skills desde repositorios externos.

**Cuándo usar:**

- Cuando una tarea no puede resolverse con las skills actuales
- Cuando se requiere una integración específica (ej: autenticación, pagos, subida de archivos)
- Cuando la implementación implicaría escribir lógica compleja desde cero

**Cuándo NO usar:**

- Para tareas simples (CRUD básico, formularios simples)
- Si ya existe una skill adecuada en el registry
- Como primera opción sin analizar el problema

**Criterio de decisión:**

- Si la solución requiere más de 30-40 líneas de lógica compleja → buscar skill
- Si es un patrón común en la industria → buscar skill
- Si ya se resolvió antes en otro proyecto → buscar skill

**Ejemplo:**
Necesidad: subir imágenes a un storage
→ No hay skill definida
→ Usar `find-skills` para buscar “file upload”

---

## Uso de skills OPSX core

### openspec-explore

- Usar para analizar requerimientos antes de cualquier implementación
- No generar código en esta etapa

### openspec-propose

- Usar para definir un Change completo (proposal, design, tasks)
- No saltar directamente a código

### openspec-apply-change

- Usar para implementar tareas de forma atómica
- Respetar el design generado

### openspec-archive-change

- Usar solo cuando el Change está completo y validado

---

## Estrategia de resolución

Ante cualquier tarea, el agente debe seguir este orden:

1. Entender el problema (explore)
2. Verificar si existe una skill adecuada
3. Si no existe → usar `find-skills`
4. Proponer solución estructurada (propose)
5. Implementar paso a paso (apply)
6. Cerrar el ciclo (archive)

---

## Anti-patrones

El agente NO debe:

- Implementar lógica compleja sin buscar primero una skill existente
- Saltarse etapas de OpenSpec
- Duplicar funcionalidades ya resueltas por otras skills
- Usar `find-skills` sin justificar su necesidad

---

## Objetivo

Maximizar reutilización, consistencia y velocidad de desarrollo, reduciendo código innecesario y decisiones arbitrarias.

---
