-- Migration: Create product_ingredients junction table with quantities
-- Description: Crear tabla de relación many-to-many entre productos e ingredientes con cantidades
-- Date: 2026-05-07

CREATE TABLE IF NOT EXISTS product_ingredients (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity_required DECIMAL(10, 2) NOT NULL CHECK (quantity_required > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint: un producto no puede usar el mismo ingrediente dos veces
    UNIQUE(product_id, ingredient_id),
    
    -- Foreign keys
    FOREIGN KEY (product_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredientes(id) ON DELETE CASCADE
);

-- Índices para mejor performance
CREATE INDEX idx_product_ingredients_product_id ON product_ingredients(product_id);
CREATE INDEX idx_product_ingredients_ingredient_id ON product_ingredients(ingredient_id);
CREATE INDEX idx_product_ingredients_product_ingredient ON product_ingredients(product_id, ingredient_id);

-- Comentarios de tabla
COMMENT ON TABLE product_ingredients IS 'Tabla de relación muchos-a-muchos entre productos e ingredientes. Almacena la cantidad requerida de cada ingrediente para un producto.';
COMMENT ON COLUMN product_ingredients.id IS 'Identificador único de la relación';
COMMENT ON COLUMN product_ingredients.product_id IS 'Referencia al producto';
COMMENT ON COLUMN product_ingredients.ingredient_id IS 'Referencia al ingrediente';
COMMENT ON COLUMN product_ingredients.quantity_required IS 'Cantidad requerida del ingrediente para este producto (> 0)';
COMMENT ON COLUMN product_ingredients.created_at IS 'Timestamp de creación de la relación';
COMMENT ON COLUMN product_ingredients.updated_at IS 'Timestamp de última actualización de la relación';
