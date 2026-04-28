# Skill Registry – Food Store SDD/OPSX

Este registro centraliza y documenta TODAS las skills recomendadas u obligatorias para operar correctamente este proyecto bajo OPSX/SDD.

> ⚠️ ¡NO copies skills acá! Cada skill se instala en forma individual en el entorno global de cada dev o agente (no en el repo). Este archivo es la FUENTE DE LA VERDAD (source-of-truth) sobre qué skills y flujos hay que usar y para qué.

---

## Formato sugerido para skills nuevas

### nombre-de-la-skill
- **Fuente:** [url-del-skill]
- **Motivo:** Breve descripción de funcionalidad o problema que resuelve
- **Cómo instalar:** Comando recomendado (npx/opencode/apt/etc)

---

## Skills recomendadas/obligatorias

### openspec-init
- **Fuente:** incluida (core OPSX)
- **Motivo:** Inicializa el contexto OPSX/SDD en cualquier proyecto.
- **Cómo instalar:** Integrado (corre: `openspec init`)

### openspec-explore
- **Fuente:** incluida (core OPSX)
- **Motivo:** Permite investigar, pensar y analizar requisitos antes de proponer changes.
- **Cómo instalar:** Integrado

### openspec-propose
- **Fuente:** incluida (core OPSX)
- **Motivo:** Genera en un paso todos los artefactos necesarios para un change (proposal, design, tasks), siguiendo SDD.
- **Cómo instalar:** Integrado

### openspec-apply-change
- **Fuente:** incluida (core OPSX)
- **Motivo:** Implementa tareas de un change de forma trazable y atómica, leyendo design y tasks.
- **Cómo instalar:** Integrado

### openspec-archive-change
- **Fuente:** incluida (core OPSX)
- **Motivo:** Archiva changes completos, sincronizando specs y manteniendo historial.
- **Cómo instalar:** Integrado

---

### find-skills
- **Fuente:** https://github.com/vercel-labs/skills
- **Motivo:** Permite buscar y descubrir nuevas skills para agentes OPSX/ATL, acelerando la integración de nuevas capacidades.
- **Cómo instalar:**

  ```bash
  npx skills add https://github.com/vercel-labs/skills --skill find-skills
  ```

---

## Buenas prácticas

> Para patrones y reglas de uso de skills (cuándo invocar, anti-patrones, ejemplos y flujo decisional), ver también:
> 
> `.atl/skills-behavior.md` 

Esto centraliza criterios para sub-agentes OPSX, AI y humanos.
- Mantené este archivo y compartilo en onboarding para que todos los devs/agentes trabajen con las skills correctas.
- Si agregás skills custom o de terceros, documentá bien el motivo, el link y el comando real de instalación.
- Si el equipo desarrolla skills propias, documentarlas aquí con instrucciones.
- Este manifest NO debe incluir archivos, sólo referencias y explicación.

---

Última edición: 27/04/2026
Responsable: OPSX/SDD Coordinator
