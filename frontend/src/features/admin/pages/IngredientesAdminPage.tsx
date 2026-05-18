/**
 * IngredientesAdminPage — Gestión CRUD de ingredientes en el panel de administración.
 *
 * Features:
 * - Tabla paginada (10/página) con columnas: ID / Nombre / Unidad / Stock / Mínimo / Alerta / Estado / Acciones
 * - Badge rojo cuando alerta_stock_bajo=true
 * - Modal crear con todos los campos; modal editar solo con campos editables
 * - Eliminación con window.confirm() + toast de feedback
 */

import React, { useState, useMemo } from 'react';
import {
  useIngredientesQuery,
  useCreateIngrediente,
  useUpdateIngrediente,
  useDeleteIngrediente,
} from '../hooks/useIngredientes';
import { useCategoriasQuery } from '../hooks/useCategorias';
import type { Ingrediente, UnidadMedida } from '../services/adminIngredientesApi';

// ── Constants ──────────────────────────────────────────────────────────────────

const PAGE_SIZE = 10;

const UNIDADES: { value: UnidadMedida; label: string }[] = [
  { value: 'gramos', label: 'Gramos' },
  { value: 'kilos', label: 'Kilos' },
  { value: 'litros', label: 'Litros' },
  { value: 'mililitros', label: 'Mililitros' },
  { value: 'unidades', label: 'Unidades' },
];

// ── Toast ──────────────────────────────────────────────────────────────────────

interface ToastState {
  message: string;
  type: 'success' | 'error';
}

// ── Form state ─────────────────────────────────────────────────────────────────

interface CreateFormData {
  nombre: string;
  unidad_medida: UnidadMedida;
  cantidad_stock: string;
  cantidad_minima: string;
  descripcion: string;
  categoria_id: string;
}

interface EditFormData {
  nombre: string;
  descripcion: string;
  cantidad_stock: string;
  cantidad_minima: string;
}

const EMPTY_CREATE_FORM: CreateFormData = {
  nombre: '',
  unidad_medida: 'unidades',
  cantidad_stock: '0',
  cantidad_minima: '0',
  descripcion: '',
  categoria_id: '',
};

const EMPTY_EDIT_FORM: EditFormData = {
  nombre: '',
  descripcion: '',
  cantidad_stock: '0',
  cantidad_minima: '0',
};

// ── Validation ─────────────────────────────────────────────────────────────────

function validateCreateForm(data: CreateFormData): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!data.nombre.trim()) {
    errors.nombre = 'El nombre es requerido';
  } else if (data.nombre.trim().length > 100) {
    errors.nombre = 'El nombre no puede superar 100 caracteres';
  }
  const stock = Number(data.cantidad_stock);
  if (isNaN(stock) || stock < 0) {
    errors.cantidad_stock = 'La cantidad en stock debe ser ≥ 0';
  }
  const minima = Number(data.cantidad_minima);
  if (isNaN(minima) || minima < 0) {
    errors.cantidad_minima = 'La cantidad mínima debe ser ≥ 0';
  }
  if (data.descripcion.length > 500) {
    errors.descripcion = 'La descripción no puede superar 500 caracteres';
  }
  return errors;
}

function validateEditForm(data: EditFormData): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!data.nombre.trim()) {
    errors.nombre = 'El nombre es requerido';
  } else if (data.nombre.trim().length > 100) {
    errors.nombre = 'El nombre no puede superar 100 caracteres';
  }
  const stock = Number(data.cantidad_stock);
  if (isNaN(stock) || stock < 0) {
    errors.cantidad_stock = 'La cantidad en stock debe ser ≥ 0';
  }
  const minima = Number(data.cantidad_minima);
  if (isNaN(minima) || minima < 0) {
    errors.cantidad_minima = 'La cantidad mínima debe ser ≥ 0';
  }
  if (data.descripcion.length > 500) {
    errors.descripcion = 'La descripción no puede superar 500 caracteres';
  }
  return errors;
}

// ── Component ──────────────────────────────────────────────────────────────────

const IngredientesAdminPage: React.FC = () => {
  const { data: ingredientes = [], isLoading, isError } = useIngredientesQuery();
  const { data: categorias = [] } = useCategoriasQuery();
  const createMutation = useCreateIngrediente();
  const updateMutation = useUpdateIngrediente();
  const deleteMutation = useDeleteIngrediente();

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Ingrediente | null>(null);
  const [createForm, setCreateForm] = useState<CreateFormData>(EMPTY_CREATE_FORM);
  const [editForm, setEditForm] = useState<EditFormData>(EMPTY_EDIT_FORM);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Pagination state
  const [page, setPage] = useState(1);

  // Toast state
  const [toast, setToast] = useState<ToastState | null>(null);

  // ── Derived data ─────────────────────────────────────────────────────────────

  const totalPages = Math.max(1, Math.ceil(ingredientes.length / PAGE_SIZE));
  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return ingredientes.slice(start, start + PAGE_SIZE);
  }, [ingredientes, page]);

  // ── Toast helpers ─────────────────────────────────────────────────────────────

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  }

  // ── Modal helpers ─────────────────────────────────────────────────────────────

  function openCreateModal() {
    setEditingItem(null);
    setCreateForm(EMPTY_CREATE_FORM);
    setFormErrors({});
    setModalOpen(true);
  }

  function openEditModal(ing: Ingrediente) {
    setEditingItem(ing);
    setEditForm({
      nombre: ing.nombre,
      descripcion: ing.descripcion ?? '',
      cantidad_stock: String(ing.cantidad_stock),
      cantidad_minima: String(ing.cantidad_minima),
    });
    setFormErrors({});
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditingItem(null);
    setCreateForm(EMPTY_CREATE_FORM);
    setEditForm(EMPTY_EDIT_FORM);
    setFormErrors({});
  }

  // ── Form handlers ─────────────────────────────────────────────────────────────

  function handleCreateChange(field: keyof CreateFormData, value: string) {
    setCreateForm((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) setFormErrors((prev) => ({ ...prev, [field]: '' }));
  }

  function handleEditChange(field: keyof EditFormData, value: string) {
    setEditForm((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) setFormErrors((prev) => ({ ...prev, [field]: '' }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (editingItem) {
      const errors = validateEditForm(editForm);
      if (Object.keys(errors).length > 0) { setFormErrors(errors); return; }
      try {
        await updateMutation.mutateAsync({
          id: editingItem.id,
          data: {
            nombre: editForm.nombre.trim(),
            descripcion: editForm.descripcion.trim() || undefined,
            cantidad_stock: Number(editForm.cantidad_stock),
            cantidad_minima: Number(editForm.cantidad_minima),
          },
        });
        showToast('Ingrediente actualizado correctamente', 'success');
        closeModal();
      } catch {
        showToast('Error al actualizar el ingrediente', 'error');
      }
    } else {
      const errors = validateCreateForm(createForm);
      if (Object.keys(errors).length > 0) { setFormErrors(errors); return; }
      try {
        await createMutation.mutateAsync({
          nombre: createForm.nombre.trim(),
          unidad_medida: createForm.unidad_medida,
          cantidad_stock: Number(createForm.cantidad_stock),
          cantidad_minima: Number(createForm.cantidad_minima),
          descripcion: createForm.descripcion.trim() || undefined,
          categoria_id: createForm.categoria_id ? Number(createForm.categoria_id) : undefined,
        });
        showToast('Ingrediente creado correctamente', 'success');
        closeModal();
      } catch {
        showToast('Error al crear el ingrediente', 'error');
      }
    }
  }

  // ── Delete handler ────────────────────────────────────────────────────────────

  async function handleDelete(ing: Ingrediente) {
    const confirmed = window.confirm(
      `¿Estás seguro de que querés eliminar el ingrediente "${ing.nombre}"?`
    );
    if (!confirmed) return;
    try {
      await deleteMutation.mutateAsync(ing.id);
      showToast('Ingrediente eliminado correctamente', 'success');
      if (page > 1 && paginated.length === 1) setPage((p) => p - 1);
    } catch {
      showToast('Error al eliminar el ingrediente', 'error');
    }
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  // ── Render ────────────────────────────────────────────────────────────────────

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          }`}
          role="alert"
        >
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Ingredientes</h1>
        <button
          onClick={openCreateModal}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
        >
          + Nuevo Ingrediente
        </button>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      ) : isError ? (
        <p className="text-red-500 text-sm">Error al cargar los ingredientes.</p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full bg-white text-left text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">ID</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Nombre</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Unidad</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Stock</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Mínimo</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Alerta</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Estado</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {paginated.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-10 text-center text-gray-400">
                      No hay ingredientes registrados
                    </td>
                  </tr>
                ) : (
                  paginated.map((ing) => (
                    <tr key={ing.id} className="border-b hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-gray-500">{ing.id}</td>
                      <td className="px-4 py-3 font-medium text-gray-900">{ing.nombre}</td>
                      <td className="px-4 py-3 text-gray-600 capitalize">{ing.unidad_medida}</td>
                      <td className="px-4 py-3 text-gray-900">{ing.cantidad_stock}</td>
                      <td className="px-4 py-3 text-gray-600">{ing.cantidad_minima}</td>
                      <td className="px-4 py-3">
                        {ing.alerta_stock_bajo ? (
                          <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700">
                            Stock bajo
                          </span>
                        ) : (
                          <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">
                            OK
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                            ing.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-500'
                          }`}
                        >
                          {ing.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-4 py-3 flex gap-2">
                        <button
                          onClick={() => openEditModal(ing)}
                          className="text-xs text-indigo-600 hover:underline font-medium"
                          aria-label={`Editar ingrediente ${ing.nombre}`}
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(ing)}
                          className="text-xs text-red-600 hover:underline font-medium"
                          aria-label={`Eliminar ingrediente ${ing.nombre}`}
                        >
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 text-sm text-gray-600">
              <span>Página {page} de {totalPages}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md my-4">
            <div className="px-6 py-4 border-b flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">
                {editingItem ? 'Editar Ingrediente' : 'Nuevo Ingrediente'}
              </h2>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600 text-xl leading-none"
                aria-label="Cerrar modal"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
              {/* Nombre */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={editingItem ? editForm.nombre : createForm.nombre}
                  onChange={(e) =>
                    editingItem
                      ? handleEditChange('nombre', e.target.value)
                      : handleCreateChange('nombre', e.target.value)
                  }
                  maxLength={100}
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    formErrors.nombre ? 'border-red-400' : 'border-gray-300'
                  }`}
                  placeholder="Nombre del ingrediente"
                />
                {formErrors.nombre && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.nombre}</p>
                )}
              </div>

              {/* Unidad de medida — solo en creación */}
              {!editingItem && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Unidad de medida <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={createForm.unidad_medida}
                    onChange={(e) => handleCreateChange('unidad_medida', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {UNIDADES.map((u) => (
                      <option key={u.value} value={u.value}>
                        {u.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Cantidad stock */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cantidad en stock <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  min={0}
                  value={editingItem ? editForm.cantidad_stock : createForm.cantidad_stock}
                  onChange={(e) =>
                    editingItem
                      ? handleEditChange('cantidad_stock', e.target.value)
                      : handleCreateChange('cantidad_stock', e.target.value)
                  }
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    formErrors.cantidad_stock ? 'border-red-400' : 'border-gray-300'
                  }`}
                />
                {formErrors.cantidad_stock && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.cantidad_stock}</p>
                )}
              </div>

              {/* Cantidad mínima */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cantidad mínima <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  min={0}
                  value={editingItem ? editForm.cantidad_minima : createForm.cantidad_minima}
                  onChange={(e) =>
                    editingItem
                      ? handleEditChange('cantidad_minima', e.target.value)
                      : handleCreateChange('cantidad_minima', e.target.value)
                  }
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    formErrors.cantidad_minima ? 'border-red-400' : 'border-gray-300'
                  }`}
                />
                {formErrors.cantidad_minima && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.cantidad_minima}</p>
                )}
              </div>

              {/* Descripción */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  value={editingItem ? editForm.descripcion : createForm.descripcion}
                  onChange={(e) =>
                    editingItem
                      ? handleEditChange('descripcion', e.target.value)
                      : handleCreateChange('descripcion', e.target.value)
                  }
                  maxLength={500}
                  rows={2}
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none ${
                    formErrors.descripcion ? 'border-red-400' : 'border-gray-300'
                  }`}
                  placeholder="Descripción opcional"
                />
                {formErrors.descripcion && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.descripcion}</p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 justify-end pt-2">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {isSubmitting ? 'Guardando...' : editingItem ? 'Guardar cambios' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default IngredientesAdminPage;
