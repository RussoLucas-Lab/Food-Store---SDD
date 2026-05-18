/**
 * DireccionManager — Gestión CRUD de direcciones de entrega del cliente.
 *
 * Funcionalidades:
 * - Listar direcciones activas del cliente
 * - Crear nueva dirección
 * - Editar dirección existente
 * - Eliminar dirección (soft delete)
 * - Marcar como predeterminada
 *
 * Estado de servidor: TanStack Query (no Zustand).
 * Uso previsto: panel de perfil del cliente o dentro del flujo de checkout.
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getDirecciones,
  createDireccion,
  updateDireccion,
  deleteDireccion,
  setDireccionPredeterminada,
  type DireccionEntregaResponse,
  type DireccionCreateDTO,
  type DireccionUpdateDTO,
} from '../services/direccionClient';

// ── Formulario de dirección ────────────────────────────────────────────────────

interface DireccionFormData {
  calle: string;
  numero: string;
  ciudad: string;
  provincia: string;
  codigo_postal: string;
  piso: string;
  departamento: string;
  referencia: string;
  es_predeterminada: boolean;
}

const EMPTY_FORM: DireccionFormData = {
  calle: '',
  numero: '',
  ciudad: '',
  provincia: '',
  codigo_postal: '',
  piso: '',
  departamento: '',
  referencia: '',
  es_predeterminada: false,
};

function direccionToForm(dir: DireccionEntregaResponse): DireccionFormData {
  return {
    calle: dir.calle,
    numero: dir.numero,
    ciudad: dir.ciudad,
    provincia: dir.provincia,
    codigo_postal: dir.codigo_postal,
    piso: dir.piso ?? '',
    departamento: dir.departamento ?? '',
    referencia: dir.referencia ?? '',
    es_predeterminada: dir.es_predeterminada,
  };
}

interface DireccionFormProps {
  initial: DireccionFormData;
  onSubmit: (data: DireccionFormData) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const DireccionForm: React.FC<DireccionFormProps> = ({
  initial,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const [form, setForm] = useState<DireccionFormData>(initial);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3" data-testid="direccion-form">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Calle <span className="text-red-500">*</span>
          </label>
          <input
            name="calle"
            value={form.calle}
            onChange={handleChange}
            required
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
            placeholder="Av. Siempreviva"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Número <span className="text-red-500">*</span>
          </label>
          <input
            name="numero"
            value={form.numero}
            onChange={handleChange}
            required
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
            placeholder="742"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Ciudad <span className="text-red-500">*</span>
          </label>
          <input
            name="ciudad"
            value={form.ciudad}
            onChange={handleChange}
            required
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Provincia <span className="text-red-500">*</span>
          </label>
          <input
            name="provincia"
            value={form.provincia}
            onChange={handleChange}
            required
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Código Postal <span className="text-red-500">*</span>
          </label>
          <input
            name="codigo_postal"
            value={form.codigo_postal}
            onChange={handleChange}
            required
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Piso</label>
          <input
            name="piso"
            value={form.piso}
            onChange={handleChange}
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
            placeholder="3"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Departamento</label>
          <input
            name="departamento"
            value={form.departamento}
            onChange={handleChange}
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
            placeholder="A"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">Referencia</label>
          <input
            name="referencia"
            value={form.referencia}
            onChange={handleChange}
            className="mt-1 block w-full border rounded px-3 py-2 text-sm"
            placeholder="Entre calles X e Y"
          />
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          name="es_predeterminada"
          checked={form.es_predeterminada}
          onChange={handleChange}
        />
        Marcar como dirección predeterminada
      </label>

      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="border border-gray-300 text-gray-700 px-4 py-2 rounded text-sm font-medium hover:bg-gray-50"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
};

// ── Tarjeta de dirección ───────────────────────────────────────────────────────

interface DireccionCardProps {
  direccion: DireccionEntregaResponse;
  onEdit: () => void;
  onDelete: () => void;
  onSetPredeterminada: () => void;
  isDeleting: boolean;
  isSettingPredeterminada: boolean;
}

const DireccionCard: React.FC<DireccionCardProps> = ({
  direccion,
  onEdit,
  onDelete,
  onSetPredeterminada,
  isDeleting,
  isSettingPredeterminada,
}) => (
  <div
    className={`border rounded-lg p-4 ${
      direccion.es_predeterminada
        ? 'border-green-400 bg-green-50'
        : 'border-gray-200 bg-white'
    }`}
    data-testid="direccion-card"
  >
    <div className="flex justify-between items-start">
      <div>
        <p className="font-medium text-gray-900">
          {direccion.calle} {direccion.numero}
          {direccion.piso ? `, Piso ${direccion.piso}` : ''}
          {direccion.departamento ? ` Dpto. ${direccion.departamento}` : ''}
        </p>
        <p className="text-sm text-gray-600">
          {direccion.ciudad}, {direccion.provincia} ({direccion.codigo_postal})
        </p>
        {direccion.referencia && (
          <p className="text-xs text-gray-500 mt-1">{direccion.referencia}</p>
        )}
        {direccion.es_predeterminada && (
          <span className="inline-block mt-1 text-xs text-green-700 font-semibold">
            Predeterminada
          </span>
        )}
      </div>

      <div className="flex flex-col gap-1 ml-4">
        {!direccion.es_predeterminada && (
          <button
            onClick={onSetPredeterminada}
            disabled={isSettingPredeterminada}
            className="text-xs text-blue-600 hover:underline disabled:opacity-50"
          >
            {isSettingPredeterminada ? '...' : 'Hacer predeterminada'}
          </button>
        )}
        <button
          onClick={onEdit}
          className="text-xs text-gray-600 hover:underline"
        >
          Editar
        </button>
        <button
          onClick={onDelete}
          disabled={isDeleting}
          className="text-xs text-red-500 hover:underline disabled:opacity-50"
        >
          {isDeleting ? 'Eliminando...' : 'Eliminar'}
        </button>
      </div>
    </div>
  </div>
);

// ── Componente principal ───────────────────────────────────────────────────────

const DireccionManager: React.FC = () => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // ── Query ──────────────────────────────────────────────────────────────────

  const { data: direcciones = [], isLoading, isError } = useQuery<DireccionEntregaResponse[]>({
    queryKey: ['direcciones'],
    queryFn: getDirecciones,
    staleTime: 1000 * 60 * 5,
  });

  // ── Mutations ──────────────────────────────────────────────────────────────

  const invalidateDirecciones = () => {
    queryClient.invalidateQueries({ queryKey: ['direcciones'] });
  };

  const createMutation = useMutation({
    mutationFn: (dto: DireccionCreateDTO) => createDireccion(dto),
    onSuccess: invalidateDirecciones,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, dto }: { id: number; dto: DireccionUpdateDTO }) =>
      updateDireccion(id, dto),
    onSuccess: () => {
      invalidateDirecciones();
      setEditingId(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteDireccion(id),
    onSuccess: invalidateDirecciones,
  });

  const setPredMutation = useMutation({
    mutationFn: (id: number) => setDireccionPredeterminada(id),
    onSuccess: invalidateDirecciones,
  });

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleCreate = (form: DireccionFormData) => {
    const dto: DireccionCreateDTO = {
      calle: form.calle,
      numero: form.numero,
      ciudad: form.ciudad,
      provincia: form.provincia,
      codigo_postal: form.codigo_postal,
      piso: form.piso || null,
      departamento: form.departamento || null,
      referencia: form.referencia || null,
      es_predeterminada: form.es_predeterminada,
    };
    createMutation.mutate(dto, {
      onSuccess: () => setShowForm(false),
    });
  };

  const handleUpdate = (form: DireccionFormData) => {
    if (editingId === null) return;
    const dto: DireccionUpdateDTO = {
      calle: form.calle,
      numero: form.numero,
      ciudad: form.ciudad,
      provincia: form.provincia,
      codigo_postal: form.codigo_postal,
      piso: form.piso || null,
      departamento: form.departamento || null,
      referencia: form.referencia || null,
      es_predeterminada: form.es_predeterminada,
    };
    updateMutation.mutate({ id: editingId, dto });
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  if (isLoading) {
    return <p className="text-sm text-gray-500">Cargando direcciones...</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-500">
        No se pudieron cargar las direcciones. Intentá de nuevo más tarde.
      </p>
    );
  }

  return (
    <div className="space-y-4" data-testid="direccion-manager">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Mis Direcciones</h3>
        {!showForm && (
          <button
            onClick={() => {
              setEditingId(null);
              setShowForm(true);
            }}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded font-medium hover:bg-blue-700"
          >
            + Nueva Dirección
          </button>
        )}
      </div>

      {/* Error de mutations */}
      {(createMutation.isError || updateMutation.isError || deleteMutation.isError) && (
        <p className="text-sm text-red-500">
          Ocurrió un error. Por favor, intentá de nuevo.
        </p>
      )}

      {/* Formulario de creación */}
      {showForm && editingId === null && (
        <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Nueva dirección</h4>
          <DireccionForm
            initial={EMPTY_FORM}
            onSubmit={handleCreate}
            onCancel={() => setShowForm(false)}
            isLoading={createMutation.isPending}
          />
        </div>
      )}

      {/* Lista de direcciones */}
      {direcciones.length === 0 && !showForm ? (
        <p className="text-sm text-gray-500">
          No tenés direcciones guardadas. Agregá una para poder realizar pedidos.
        </p>
      ) : (
        <ul className="space-y-3">
          {direcciones.map((dir) => (
            <li key={dir.id}>
              {editingId === dir.id ? (
                <div className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                  <h4 className="text-sm font-semibold text-gray-800 mb-3">
                    Editando dirección
                  </h4>
                  <DireccionForm
                    initial={direccionToForm(dir)}
                    onSubmit={handleUpdate}
                    onCancel={() => setEditingId(null)}
                    isLoading={updateMutation.isPending}
                  />
                </div>
              ) : (
                <DireccionCard
                  direccion={dir}
                  onEdit={() => {
                    setShowForm(false);
                    setEditingId(dir.id);
                  }}
                  onDelete={() => deleteMutation.mutate(dir.id)}
                  onSetPredeterminada={() => setPredMutation.mutate(dir.id)}
                  isDeleting={deleteMutation.isPending && deleteMutation.variables === dir.id}
                  isSettingPredeterminada={
                    setPredMutation.isPending && setPredMutation.variables === dir.id
                  }
                />
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DireccionManager;
