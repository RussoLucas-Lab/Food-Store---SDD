-- Migration: Create productos table
-- Description: Crear tabla 'productos' para gestionar productos del catálogo
-- Date: 2026-05-07

CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(500),
    base_price DECIMAL(10, 2) NOT NULL CHECK (base_price > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT nombre_not_empty CHECK (nombre != '')
);

-- Índices para mejor performance
CREATE INDEX idx_productos_nombre ON productos(nombre);
CREATE INDEX idx_productos_status ON productos(status);
CREATE INDEX idx_productos_created_at ON productos(created_at);

-- Comentarios de tabla
COMMENT ON TABLE productos IS 'Tabla de productos del catálogo. Soporta soft delete via deleted_at. Stock es calculado transitivamente desde sus ingredientes.';
COMMENT ON COLUMN productos.id IS 'Identificador único del producto';
COMMENT ON COLUMN productos.nombre IS 'Nombre único del producto (ej: Pizza Margherita)';
COMMENT ON COLUMN productos.descripcion IS 'Descripción opcional del producto';
COMMENT ON COLUMN productos.base_price IS 'Precio base del producto en unidades monetarias (> 0)';
COMMENT ON COLUMN productos.status IS 'Estado del producto: active o inactive (soft delete)';
COMMENT ON COLUMN productos.created_at IS 'Timestamp de creación del registro';
COMMENT ON COLUMN productos.updated_at IS 'Timestamp de última actualización del registro';
COMMENT ON COLUMN productos.deleted_at IS 'Timestamp de soft delete; NULL si el producto está activo';
