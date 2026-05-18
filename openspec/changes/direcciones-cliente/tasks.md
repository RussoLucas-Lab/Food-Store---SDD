# Tasks — direcciones-cliente

## 1. Hooks centralizados de direcciones

- [ ] 1.1 Crear `frontend/src/features/pedidos/hooks/useDirecciones.ts` exportando la
  constante `DIRECCIONES_QUERY_KEY = ['direcciones']`.
- [ ] 1.2 Implementar `useDirecciones()` con `useQuery` (`queryKey` = `DIRECCIONES_QUERY_KEY`,
  `queryFn` = `getDirecciones`, `staleTime` 5 min).
- [ ] 1.3 Implementar `useCreateDireccion()` con `useMutation` (`mutationFn` =
  `createDireccion`, `onSuccess` invalida `DIRECCIONES_QUERY_KEY`).
- [ ] 1.4 Implementar `useUpdateDireccion()` con `useMutation` que recibe `{ id, dto }`
  e invalida `DIRECCIONES_QUERY_KEY` en `onSuccess`.
- [ ] 1.5 Implementar `useDeleteDireccion()` con `useMutation` (`mutationFn` =
  `deleteDireccion`, invalida `DIRECCIONES_QUERY_KEY`).
- [ ] 1.6 Implementar `useSetDireccionPredeterminada()` con `useMutation` (`mutationFn`
  = `setDireccionPredeterminada`, invalida `DIRECCIONES_QUERY_KEY`).
- [ ] 1.7 Exponer los hooks en `frontend/src/features/pedidos/hooks/index.ts` si existe
  barrel export.

## 2. Refactor de componentes existentes

- [ ] 2.1 Reemplazar en `DireccionManager.tsx` la `useQuery` inline y las 4 mutations
  inline por los hooks de `useDirecciones.ts`, sin alterar markup ni `data-testid`.
- [ ] 2.2 Reemplazar en `DirectionSelector.tsx` la `useQuery` inline por `useDirecciones()`,
  conservando la pre-selección de la dirección predeterminada.
- [ ] 2.3 Verificar que no quedan llamadas directas a `direccionClient` ni `useQuery`/
  `useMutation` inline de direcciones fuera de `useDirecciones.ts`.

## 3. Página dedicada de direcciones

- [ ] 3.1 Crear `frontend/src/features/pedidos/pages/DireccionesPage.tsx` que renderiza
  `<DireccionManager />` con un encabezado de página.
- [ ] 3.2 Importar `DireccionesPage` en `frontend/src/router.tsx`.
- [ ] 3.3 Agregar la ruta protegida `/perfil/direcciones` dentro del bloque
  `ProtectedRoute` que ya cubre `/perfil` (envuelta en `LayoutRoute`).

## 4. Integración en el perfil

- [ ] 4.1 Montar `<DireccionManager />` en `PerfilPage.tsx` como sección
  "Mis Direcciones", visible tanto en modo vista como tras cargar el perfil.
- [ ] 4.2 Agregar un enlace/botón en `PerfilPage` hacia `/perfil/direcciones`
  (opcional si la sección embebida ya cubre la gestión).

## 5. Consistencia del checkout

- [ ] 5.1 Actualizar en `DirectionSelector.tsx` los enlaces "Agregar Nueva Dirección"
  para apuntar a `/perfil/direcciones` (usar `<Link>` de react-router en vez de `<a>`).
- [ ] 5.2 Verificar que `CheckoutPage` deshabilita o bloquea la creación del pedido
  cuando `selectedDirectionId` es `null`.

## 6. Verificación

- [ ] 6.1 Ejecutar `npm run build` (o `tsc --noEmit`) en `frontend/` sin errores de tipos.
- [ ] 6.2 Verificación manual del flujo: perfil → "Mis Direcciones" → crear / editar /
  eliminar / marcar predeterminada.
- [ ] 6.3 Verificación manual: ruta `/perfil/direcciones` accesible y funcional.
- [ ] 6.4 Verificación manual del checkout: el selector muestra direcciones, pre-selecciona
  la predeterminada y permite continuar con una dirección elegida.
- [ ] 6.5 Verificar RN-DI01 (primera dirección queda predeterminada) y RN-DI02
  (marcar predeterminada desmarca al resto) reflejadas correctamente en la UI tras
  la invalidación de caché.
