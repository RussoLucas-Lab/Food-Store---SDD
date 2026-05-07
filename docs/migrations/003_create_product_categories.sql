-- Migration: Create product_categories junction table
-- Description: Crear tabla de relación many-to-many entre productos y categorías
-- Date: 2026-05-07

CREATE TABLE IF NOT EXISTS product_categories (
    product_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (product_id, category_id),
    
    -- Foreign keys
    FOREIGN KEY (product_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categorias(id) ON DELETE CASCADE
);

-- Índices para mejor performance
CREATE INDEX idx_product_categories_product_id ON product_categories(product_id);
CREATE INDEX idx_product_categories_category_id ON product_categories(category_id);

-- Comentarios de tabla
COMMENT ON TABLE product_categories IS 'Tabla de relación muchos-a-muchos entre productos y categorías. Un producto puede estar en múltiples categorías.';
COMMENT ON COLUMN product_categories.product_id IS 'Referencia al producto';
COMMENT ON COLUMN product_categories.category_id IS 'Referencia a la categoría';
COMMENT ON COLUMN product_categories.created_at IS 'Timestamp de creación de la relación';
