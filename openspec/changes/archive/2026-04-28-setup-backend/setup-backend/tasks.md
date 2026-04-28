## 1. Estructura inicial del backend

- [ ] 1.1 Crear carpetas base: config/, models/, repositories/, uow/, tests/
- [x] 1.2 Generar archivo README/backend-base.md documentando arquitectura y convenciones
- [x] 1.3 Agregar archivo .env.example y folder config/ para variables de entorno

## 2. Implementar contratos Repository y Unit of Work

- [x] 2.1 Escribir interfaces base y una implementación simple para Repository y UoW en repositories/ y uow/
- [x] 2.2 Documentar contratos públicos en README/backend-base.md

## 3. Modelos base minimalistas

- [x] 3.1 Crear archivos de modelos: categoria.py/js, ingrediente.py/js, producto.py/js, usuario.py/js, cliente.py/js
- [x] 3.2 Definir sólo los atributos principales vacíos o ejemplo, sin lógica

## 4. Configuración de entorno

- [x] 4.1 Implementar carga básica de variables de entorno desde config/ y .env
- [ ] 4.2 Proteger .env real vía .gitignore y dejar solo .env.example en el repo

## 5. Script/data seed mínima

- [x] 5.1 Crear script/documentación de seed inicial para desarrollo/test
- [x] 5.2 Asegurar que población de datos demo NO se ejecute en producción

## 6. Estructura de tests

- [x] 6.1 Crear carpeta tests/ con ejemplo de runner vacío (ej: test_placeholder.py, test_placeholder.js)
- [x] 6.2 Documentar cómo correr tests en README/backend-base.md
