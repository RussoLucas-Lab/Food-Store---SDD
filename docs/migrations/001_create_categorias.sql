-- Migration: Create categorias table
-- Description: Crear tabla 'categorias' para gestionar categorías de productos
-- Date: 2026-05-06

CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Índices para mejor performance
    CONSTRAINT nombre_not_empty CHECK (nombre != '')
);

-- Índices
CREATE INDEX idx_categorias_nombre ON categorias(nombre);
CREATE INDEX idx_categorias_is_active ON categorias(is_active);
CREATE INDEX idx_categorias_created_at ON categorias(created_at);

-- Comentarios de tabla
COMMENT ON TABLE categorias IS 'Tabla de categorías de productos del catálogo. Soporta soft delete via deleted_at.';
COMMENT ON COLUMN categorias.id IS 'Identificador único de la categoría';
COMMENT ON COLUMN categorias.nombre IS 'Nombre único de la categoría (ej: Bebidas, Postres)';
COMMENT ON COLUMN categorias.descripcion IS 'Descripción opcional de la categoría';
COMMENT ON COLUMN categorias.is_active IS 'Indica si la categoría está activa (visible en listados)';
COMMENT ON COLUMN categorias.created_at IS 'Timestamp de creación del registro';
COMMENT ON COLUMN categorias.updated_at IS 'Timestamp de última actualización del registro';
COMMENT ON COLUMN categorias.deleted_at IS 'Timestamp de soft delete; NULL si la categoría está activa';
