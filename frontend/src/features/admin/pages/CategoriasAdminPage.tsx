/**
 * CategoriasAdminPage — Gestión CRUD de categorías en el panel de administración.
 *
 * Features:
 * - Tabla paginada (10/página) con columnas: ID / Nombre / Descripción / Estado / Acciones
 * - Modal crear/editar con validación en cliente
 * - Eliminación con window.confirm() + toast de feedback
 * - Loading skeleton y estado vacío
 */

import React, { useState, useMemo } from 'react';
import {
  useCategoriasQuery,
  useCreateCategoria,
  useUpdateCategoria,
  useDeleteCategoria,
} from '../hooks/useCategorias';
import type { Categoria } from '../services/adminCategoriasApi';

// ── Constants ──────────────────────────────────────────────────────────────────

const PAGE_SIZE = 10;

// ── Toast ──────────────────────────────────────────────────────────────────────

interface ToastState {
  message: string;
  type: 'success' | 'error';
}

// ── Form state ─────────────────────────────────────────────────────────────────

interface FormData {
  nombre: string;
  descripcion: string;
}

const EMPTY_FORM: FormData = { nombre: '', descripcion: '' };

// ── Validation ─────────────────────────────────────────────────────────────────

function validateForm(data: FormData): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!data.nombre.trim()) {
    errors.nombre = 'El nombre es requerido';
  } else if (data.nombre.trim().length > 100) {
    errors.nombre = 'El nombre no puede superar 100 caracteres';
  }
  if (data.descripcion.length > 500) {
    errors.descripcion = 'La descripción no puede superar 500 caracteres';
  }
  return errors;
}

// ── Component ──────────────────────────────────────────────────────────────────

const CategoriasAdminPage: React.FC = () => {
  const { data: categorias = [], isLoading, isError } = useCategoriasQuery();
  const createMutation = useCreateCategoria();
  const updateMutation = useUpdateCategoria();
  const deleteMutation = useDeleteCategoria();

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Categoria | null>(null);
  const [formData, setFormData] = useState<FormData>(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Pagination state
  const [page, setPage] = useState(1);

  // Toast state
  const [toast, setToast] = useState<ToastState | null>(null);

  // ── Derived data ─────────────────────────────────────────────────────────────

  const totalPages = Math.max(1, Math.ceil(categorias.length / PAGE_SIZE));
  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return categorias.slice(start, start + PAGE_SIZE);
  }, [categorias, page]);

  // ── Toast helpers ─────────────────────────────────────────────────────────────

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  }

  // ── Modal helpers ─────────────────────────────────────────────────────────────

  function openCreateModal() {
    setEditingItem(null);
    setFormData(EMPTY_FORM);
    setFormErrors({});
    setModalOpen(true);
  }

  function openEditModal(cat: Categoria) {
    setEditingItem(cat);
    setFormData({ nombre: cat.nombre, descripcion: cat.descripcion ?? '' });
    setFormErrors({});
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditingItem(null);
    setFormData(EMPTY_FORM);
    setFormErrors({});
  }

  // ── Form handlers ─────────────────────────────────────────────────────────────

  function handleChange(field: keyof FormData, value: string) {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors((prev) => ({ ...prev, [field]: '' }));
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errors = validateForm(formData);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    const payload = {
      nombre: formData.nombre.trim(),
      descripcion: formData.descripcion.trim() || undefined,
    };

    try {
      if (editingItem) {
        await updateMutation.mutateAsync({ id: editingItem.id, data: payload });
        showToast('Categoría actualizada correctamente', 'success');
      } else {
        await createMutation.mutateAsync(payload);
        showToast('Categoría creada correctamente', 'success');
      }
      closeModal();
    } catch {
      showToast(
        editingItem ? 'Error al actualizar la categoría' : 'Error al crear la categoría',
        'error'
      );
    }
  }

  // ── Delete handler ────────────────────────────────────────────────────────────

  async function handleDelete(cat: Categoria) {
    const confirmed = window.confirm(
      `¿Estás seguro de que querés eliminar la categoría "${cat.nombre}"?`
    );
    if (!confirmed) return;
    try {
      await deleteMutation.mutateAsync(cat.id);
      showToast('Categoría eliminada correctamente', 'success');
      if (page > 1 && paginated.length === 1) {
        setPage((p) => p - 1);
      }
    } catch {
      showToast('Error al eliminar la categoría', 'error');
    }
  }

  // ── Submitting flag ───────────────────────────────────────────────────────────

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  // ── Render ────────────────────────────────────────────────────────────────────

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium transition-all ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          }`}
          role="alert"
        >
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Categorías</h1>
        <button
          onClick={openCreateModal}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
        >
          + Nueva Categoría
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
        <p className="text-red-500 text-sm">Error al cargar las categorías.</p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full bg-white text-left text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">ID</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Nombre</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Descripción</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Estado</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {paginated.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-10 text-center text-gray-400">
                      No hay categorías registradas
                    </td>
                  </tr>
                ) : (
                  paginated.map((cat) => (
                    <tr key={cat.id} className="border-b hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-gray-500">{cat.id}</td>
                      <td className="px-4 py-3 font-medium text-gray-900">{cat.nombre}</td>
                      <td className="px-4 py-3 text-gray-600 max-w-xs truncate">
                        {cat.descripcion || '—'}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                            cat.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-500'
                          }`}
                        >
                          {cat.is_active ? 'Activa' : 'Inactiva'}
                        </span>
                      </td>
                      <td className="px-4 py-3 flex gap-2">
                        <button
                          onClick={() => openEditModal(cat)}
                          className="text-xs text-indigo-600 hover:underline font-medium"
                          aria-label={`Editar categoría ${cat.nombre}`}
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(cat)}
                          className="text-xs text-red-600 hover:underline font-medium"
                          aria-label={`Eliminar categoría ${cat.nombre}`}
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
              <span>
                Página {page} de {totalPages}
              </span>
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
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="px-6 py-4 border-b flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">
                {editingItem ? 'Editar Categoría' : 'Nueva Categoría'}
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
                  value={formData.nombre}
                  onChange={(e) => handleChange('nombre', e.target.value)}
                  maxLength={100}
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    formErrors.nombre ? 'border-red-400' : 'border-gray-300'
                  }`}
                  placeholder="Nombre de la categoría"
                  aria-required="true"
                />
                {formErrors.nombre && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.nombre}</p>
                )}
                <p className="text-gray-400 text-xs mt-1 text-right">
                  {formData.nombre.length}/100
                </p>
              </div>

              {/* Descripción */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.descripcion}
                  onChange={(e) => handleChange('descripcion', e.target.value)}
                  maxLength={500}
                  rows={3}
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none ${
                    formErrors.descripcion ? 'border-red-400' : 'border-gray-300'
                  }`}
                  placeholder="Descripción opcional"
                />
                {formErrors.descripcion && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.descripcion}</p>
                )}
                <p className="text-gray-400 text-xs mt-1 text-right">
                  {formData.descripcion.length}/500
                </p>
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

export default CategoriasAdminPage;
