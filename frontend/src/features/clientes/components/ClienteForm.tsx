import React, { useEffect, useState } from 'react';
import { Cliente, ClienteCreate, ClienteUpdate } from '../../../shared/types';
import { FormField } from '../../../shared/components/molecules';
import { Button } from '../../../shared/components/atoms';
import './ClienteForm.css';

interface ClienteFormProps {
  cliente?: Cliente | null;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  onSubmit: (data: ClienteCreate | ClienteUpdate) => void;
  onCancel: () => void;
}

interface FormData {
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
}

const INITIAL_FORM_STATE: FormData = {
  nombre: '',
  email: '',
  telefono: '',
  direccion: '',
};

/**
 * ClienteForm Component
 * Reusable form for creating and editing clientes
 * - Validates email format, required fields, phone format
 * - Supports both create and edit modes
 * - Shows loading and error states
 */
export const ClienteForm: React.FC<ClienteFormProps> = ({
  cliente,
  isLoading,
  isSubmitting,
  error,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM_STATE);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const isEditMode = !!cliente;

  // Populate form with existing cliente data in edit mode
  useEffect(() => {
    if (cliente) {
      setFormData({
        nombre: cliente.nombre,
        email: cliente.email,
        telefono: cliente.telefono,
        direccion: cliente.direccion,
      });
    } else {
      setFormData(INITIAL_FORM_STATE);
    }
    setValidationErrors({});
  }, [cliente]);

  /**
   * Validate form fields
   * - Email: required, valid format
   * - Name: required, min 3 chars
   * - Phone: required, min 10 chars
   * - Address: required
   */
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      errors.nombre = 'El nombre es requerido';
    } else if (formData.nombre.trim().length < 3) {
      errors.nombre = 'El nombre debe tener al menos 3 caracteres';
    }

    if (!formData.email.trim()) {
      errors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'El email no tiene un formato válido';
    }

    if (!formData.telefono.trim()) {
      errors.telefono = 'El teléfono es requerido';
    } else if (formData.telefono.trim().length < 10) {
      errors.telefono = 'El teléfono debe tener al menos 10 dígitos';
    }

    if (!formData.direccion.trim()) {
      errors.direccion = 'La dirección es requerida';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear validation error for this field when user starts typing
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const updated = { ...prev };
        delete updated[name];
        return updated;
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (isEditMode) {
      // For edit mode, send only ClienteUpdate (partial)
      onSubmit({
        nombre: formData.nombre,
        email: formData.email,
        telefono: formData.telefono,
        direccion: formData.direccion,
      } as ClienteUpdate);
    } else {
      // For create mode, send ClienteCreate
      onSubmit({
        nombre: formData.nombre,
        email: formData.email,
        telefono: formData.telefono,
        direccion: formData.direccion,
      } as ClienteCreate);
    }
  };

  if (isLoading) {
    return <div className="cliente-form cliente-form--loading">Cargando formulario...</div>;
  }

  return (
    <form className="cliente-form" onSubmit={handleSubmit} noValidate>
      {error && <div className="cliente-form__error">{error}</div>}

      <div className="cliente-form__group">
        <FormField
          label="Nombre"
          id="nombre"
          name="nombre"
          type="text"
          value={formData.nombre}
          onChange={handleChange}
          error={validationErrors.nombre}
          disabled={isSubmitting}
          required
          placeholder="Ej: Juan Pérez"
        />
      </div>

      <div className="cliente-form__group">
        <FormField
          label="Email"
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          error={validationErrors.email}
          disabled={isSubmitting}
          required
          placeholder="Ej: juan@example.com"
        />
      </div>

      <div className="cliente-form__group">
        <FormField
          label="Teléfono"
          id="telefono"
          name="telefono"
          type="tel"
          value={formData.telefono}
          onChange={handleChange}
          error={validationErrors.telefono}
          disabled={isSubmitting}
          required
          placeholder="Ej: +54 11 1234 5678"
        />
      </div>

      <div className="cliente-form__group">
        <FormField
          label="Dirección"
          id="direccion"
          name="direccion"
          type="textarea"
          value={formData.direccion}
          onChange={handleChange}
          error={validationErrors.direccion}
          disabled={isSubmitting}
          required
          placeholder="Ej: Calle Principal 123, Apto 4, Buenos Aires"
        />
      </div>

      <div className="cliente-form__actions">
        <Button type="submit" disabled={isSubmitting} className="cliente-form__submit">
          {isSubmitting ? 'Guardando...' : isEditMode ? 'Guardar cambios' : 'Crear cliente'}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={isSubmitting}
          className="cliente-form__cancel"
        >
          Cancelar
        </Button>
      </div>
    </form>
  );
};

export default ClienteForm;
