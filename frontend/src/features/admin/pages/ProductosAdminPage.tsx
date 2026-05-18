/**
 * ProductosAdminPage — Gestión CRUD de productos en el panel de administración.
 *
 * Features:
 * - Tabla paginada (10/página) con columnas: ID / Nombre / Precio / Estado / Acciones
 * - Modal crear: nombre, base_price, descripcion, checkboxes de categorías, tabla dinámica de ingredientes
 * - Modal editar: usa useProductoDetalle(id) para pre-cargar categorías e ingredientes actuales
 * - Eliminación con window.confirm() + toast de feedback
 */

import React, { useState, useMemo, useEffect } from 'react';
import {
  useProductosAdminQuery,
  useProductoDetalle,
  useCreateProducto,
  useUpdateProducto,
  useDeleteProducto,
} from '../hooks/useProductosAdmin';
import { useCategoriasQuery } from '../hooks/useCategorias';
import { useIngredientesQuery } from '../hooks/useIngredientes';
import type { Producto } from '../services/adminProductosApi';

// ── Constants ──────────────────────────────────────────────────────────────────

const PAGE_SIZE = 10;

// ── Toast ──────────────────────────────────────────────────────────────────────

interface ToastState {
  message: string;
  type: 'success' | 'error';
}

// ── Form types ─────────────────────────────────────────────────────────────────

interface IngredienteRow {
  ingredient_id: string;
  quantity_required: string;
}

interface ProductoFormData {
  nombre: string;
  base_price: string;
  descripcion: string;
  categoryIds: number[];
  ingredientRows: IngredienteRow[];
}

const EMPTY_FORM: ProductoFormData = {
  nombre: '',
  base_price: '',
  descripcion: '',
  categoryIds: [],
  ingredientRows: [{ ingredient_id: '', quantity_required: '' }],
};

// ── Validation ─────────────────────────────────────────────────────────────────

function validateForm(data: ProductoFormData): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!data.nombre.trim()) {
    errors.nombre = 'El nombre es requerido';
  } else if (data.nombre.trim().length > 100) {
    errors.nombre = 'El nombre no puede superar 100 caracteres';
  }
  const price = Number(data.base_price);
  if (!data.base_price || isNaN(price) || price <= 0) {
    errors.base_price = 'El precio debe ser mayor a 0';
  }
  if (data.descripcion.length > 500) {
    errors.descripcion = 'La descripción no puede superar 500 caracteres';
  }
  if (data.categoryIds.length === 0) {
    errors.categories = 'Seleccioná al menos una categoría';
  }
  const validIngredients = data.ingredientRows.filter(
    (r) => r.ingredient_id && Number(r.quantity_required) > 0
  );
  if (validIngredients.length === 0) {
    errors.ingredients = 'Agregá al menos un ingrediente con cantidad mayor a 0';
  }
  return errors;
}

// ── ProductModal ───────────────────────────────────────────────────────────────

interface ProductModalProps {
  editingId: number | null;
  onClose: () => void;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

/**
 * ProductModal — subcomponent that owns all hooks for the create/edit form.
 * Separated so that useProductoDetalle can be called unconditionally at the top level.
 */
const ProductModal: React.FC<ProductModalProps> = ({
  editingId,
  onClose,
  onSuccess,
  onError,
}) => {
  const { data: categorias = [] } = useCategoriasQuery();
  const { data: ingredientes = [] } = useIngredientesQuery();
  const { data: detalle, isLoading: detalleLoading } = useProductoDetalle(editingId);
  const createMutation = useCreateProducto();
  const updateMutation = useUpdateProducto();

  const [formData, setFormData] = useState<ProductoFormData>(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [initialized, setInitialized] = useState(false);

  // Pre-fill when editing detail loads
  useEffect(() => {
    if (editingId === null) {
      setFormData(EMPTY_FORM);
      setInitialized(true);
      return;
    }
    if (detalle && !initialized) {
      setFormData({
        nombre: detalle.nombre,
        base_price: String(detalle.base_price),
        descripcion: detalle.descripcion ?? '',
        categoryIds: detalle.categories.map((c) => c.id),
        ingredientRows:
          detalle.ingredients.length > 0
            ? detalle.ingredients.map((i) => ({
                ingredient_id: String(i.ingredient_id),
                quantity_required: String(i.quantity_required),
              }))
            : [{ ingredient_id: '', quantity_required: '' }],
      });
      setInitialized(true);
    }
  }, [detalle, editingId, initialized]);

  function handleFieldChange(
    field: keyof Omit<ProductoFormData, 'categoryIds' | 'ingredientRows'>,
    value: string
  ) {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) setFormErrors((prev) => ({ ...prev, [field]: '' }));
  }

  function toggleCategory(id: number) {
    setFormData((prev) => ({
      ...prev,
      categoryIds: prev.categoryIds.includes(id)
        ? prev.categoryIds.filter((c) => c !== id)
        : [...prev.categoryIds, id],
    }));
    if (formErrors.categories) setFormErrors((prev) => ({ ...prev, categories: '' }));
  }

  function addIngredientRow() {
    setFormData((prev) => ({
      ...prev,
      ingredientRows: [...prev.ingredientRows, { ingredient_id: '', quantity_required: '' }],
    }));
  }

  function removeIngredientRow(index: number) {
    setFormData((prev) => ({
      ...prev,
      ingredientRows: prev.ingredientRows.filter((_, i) => i !== index),
    }));
    if (formErrors.ingredients) setFormErrors((prev) => ({ ...prev, ingredients: '' }));
  }

  function updateIngredientRow(index: number, field: keyof IngredienteRow, value: string) {
    setFormData((prev) => ({
      ...prev,
      ingredientRows: prev.ingredientRows.map((row, i) =>
        i === index ? { ...row, [field]: value } : row
      ),
    }));
    if (formErrors.ingredients) setFormErrors((prev) => ({ ...prev, ingredients: '' }));
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
      base_price: Number(formData.base_price),
      descripcion: formData.descripcion.trim() || undefined,
      categories: formData.categoryIds,
      ingredients: formData.ingredientRows
        .filter((r) => r.ingredient_id && Number(r.quantity_required) > 0)
        .map((r) => ({
          ingredient_id: Number(r.ingredient_id),
          quantity_required: Number(r.quantity_required),
        })),
    };

    try {
      if (editingId !== null) {
        await updateMutation.mutateAsync({ id: editingId, data: payload });
        onSuccess('Producto actualizado correctamente');
      } else {
        await createMutation.mutateAsync(payload);
        onSuccess('Producto creado correctamente');
      }
      onClose();
    } catch {
      onError(
        editingId !== null ? 'Error al actualizar el producto' : 'Error al crear el producto'
      );
    }
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending;
  const isEditing = editingId !== null;

  if (isEditing && detalleLoading) {
    return (
      <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-xl p-8 text-center">
          <p className="text-gray-500 text-sm">Cargando datos del producto...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-start justify-center z-40 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl my-4">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">
            {isEditing ? 'Editar Producto' : 'Nuevo Producto'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
            aria-label="Cerrar modal"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-5">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nombre <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => handleFieldChange('nombre', e.target.value)}
              maxLength={100}
              className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                formErrors.nombre ? 'border-red-400' : 'border-gray-300'
              }`}
              placeholder="Nombre del producto"
            />
            {formErrors.nombre && (
              <p className="text-red-500 text-xs mt-1">{formErrors.nombre}</p>
            )}
          </div>

          {/* Precio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Precio base <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={formData.base_price}
              onChange={(e) => handleFieldChange('base_price', e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                formErrors.base_price ? 'border-red-400' : 'border-gray-300'
              }`}
              placeholder="0.00"
            />
            {formErrors.base_price && (
              <p className="text-red-500 text-xs mt-1">{formErrors.base_price}</p>
            )}
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => handleFieldChange('descripcion', e.target.value)}
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

          {/* Categorías */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categorías <span className="text-red-500">*</span>
            </label>
            {categorias.filter((c) => c.is_active).length === 0 ? (
              <p className="text-gray-400 text-sm">No hay categorías disponibles</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-36 overflow-y-auto border border-gray-200 rounded-lg p-3">
                {categorias
                  .filter((c) => c.is_active)
                  .map((cat) => (
                    <label key={cat.id} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.categoryIds.includes(cat.id)}
                        onChange={() => toggleCategory(cat.id)}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-sm text-gray-700 truncate">{cat.nombre}</span>
                    </label>
                  ))}
              </div>
            )}
            {formErrors.categories && (
              <p className="text-red-500 text-xs mt-1">{formErrors.categories}</p>
            )}
          </div>

          {/* Ingredientes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ingredientes <span className="text-red-500">*</span>
            </label>
            <div className="space-y-2">
              {formData.ingredientRows.map((row, index) => (
                <div key={index} className="flex gap-2 items-center">
                  <select
                    value={row.ingredient_id}
                    onChange={(e) => updateIngredientRow(index, 'ingredient_id', e.target.value)}
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Seleccionar ingrediente</option>
                    {ingredientes
                      .filter((i) => i.is_active)
                      .map((ing) => (
                        <option key={ing.id} value={String(ing.id)}>
                          {ing.nombre} ({ing.unidad_medida})
                        </option>
                      ))}
                  </select>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={row.quantity_required}
                    onChange={(e) =>
                      updateIngredientRow(index, 'quantity_required', e.target.value)
                    }
                    className="w-28 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Cantidad"
                  />
                  <button
                    type="button"
                    onClick={() => removeIngredientRow(index)}
                    disabled={formData.ingredientRows.length === 1}
                    className="text-red-500 hover:text-red-700 disabled:opacity-30 text-lg leading-none px-1"
                    aria-label="Eliminar fila de ingrediente"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={addIngredientRow}
              className="mt-2 text-sm text-indigo-600 hover:text-indigo-800 font-medium"
            >
              + Agregar ingrediente
            </button>
            {formErrors.ingredients && (
              <p className="text-red-500 text-xs mt-1">{formErrors.ingredients}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ── Main component ─────────────────────────────────────────────────────────────

const ProductosAdminPage: React.FC = () => {
  const { data: productos = [], isLoading, isError } = useProductosAdminQuery();
  const deleteMutation = useDeleteProducto();

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Pagination state
  const [page, setPage] = useState(1);

  // Toast state
  const [toast, setToast] = useState<ToastState | null>(null);

  // ── Derived data ─────────────────────────────────────────────────────────────

  const totalPages = Math.max(1, Math.ceil(productos.length / PAGE_SIZE));
  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return productos.slice(start, start + PAGE_SIZE);
  }, [productos, page]);

  // ── Toast helpers ─────────────────────────────────────────────────────────────

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  }

  // ── Modal helpers ─────────────────────────────────────────────────────────────

  function openCreateModal() {
    setEditingId(null);
    setModalOpen(true);
  }

  function openEditModal(producto: Producto) {
    setEditingId(producto.id);
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditingId(null);
  }

  // ── Delete handler ────────────────────────────────────────────────────────────

  async function handleDelete(producto: Producto) {
    const confirmed = window.confirm(
      `¿Estás seguro de que querés eliminar el producto "${producto.nombre}"?`
    );
    if (!confirmed) return;
    try {
      await deleteMutation.mutateAsync(producto.id);
      showToast('Producto eliminado correctamente', 'success');
      if (page > 1 && paginated.length === 1) setPage((p) => p - 1);
    } catch {
      showToast('Error al eliminar el producto', 'error');
    }
  }

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
        <h1 className="text-2xl font-bold text-gray-800">Productos</h1>
        <button
          onClick={openCreateModal}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
        >
          + Nuevo Producto
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
        <p className="text-red-500 text-sm">Error al cargar los productos.</p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full bg-white text-left text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">ID</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Nombre</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Precio</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Stock disp.</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Estado</th>
                  <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {paginated.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-gray-400">
                      No hay productos registrados
                    </td>
                  </tr>
                ) : (
                  paginated.map((prod) => (
                    <tr key={prod.id} className="border-b hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-gray-500">{prod.id}</td>
                      <td className="px-4 py-3 font-medium text-gray-900">{prod.nombre}</td>
                      <td className="px-4 py-3 text-gray-700">${prod.base_price.toFixed(2)}</td>
                      <td className="px-4 py-3 text-gray-600">{prod.stock_disponible}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                            prod.status === 'active'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-500'
                          }`}
                        >
                          {prod.status === 'active' ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-4 py-3 flex gap-2">
                        <button
                          onClick={() => openEditModal(prod)}
                          className="text-xs text-indigo-600 hover:underline font-medium"
                          aria-label={`Editar producto ${prod.nombre}`}
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(prod)}
                          className="text-xs text-red-600 hover:underline font-medium"
                          aria-label={`Eliminar producto ${prod.nombre}`}
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

      {/* Modal — rendered conditionally to reset state on open/close */}
      {modalOpen && (
        <ProductModal
          editingId={editingId}
          onClose={closeModal}
          onSuccess={(msg) => showToast(msg, 'success')}
          onError={(msg) => showToast(msg, 'error')}
        />
      )}
    </div>
  );
};

export default ProductosAdminPage;
