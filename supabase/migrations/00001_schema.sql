CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- PROYECTOS
-- ============================================================
CREATE TABLE proyectos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    ubicacion JSONB DEFAULT '{}'::jsonb,
    estado TEXT DEFAULT 'borrador' CHECK (estado IN ('borrador','arquitectura','diseno','calculado','completado')),
    parametros JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_proyectos_user ON proyectos(user_id);

-- ============================================================
-- PISOS
-- ============================================================
CREATE TABLE pisos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proyecto_id UUID REFERENCES proyectos ON DELETE CASCADE NOT NULL,
    nombre TEXT NOT NULL,
    nivel INTEGER NOT NULL DEFAULT 0,
    datos_arquitectura JSONB DEFAULT '{}'::jsonb,
    datos_electrico JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_pisos_proyecto ON pisos(proyecto_id);

-- ============================================================
-- AMBIENTES
-- ============================================================
CREATE TABLE ambientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    piso_id UUID REFERENCES pisos ON DELETE CASCADE NOT NULL,
    nombre TEXT NOT NULL,
    area_m2 NUMERIC(10,2),
    tipo TEXT DEFAULT 'otro',
    cargas JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_ambientes_piso ON ambientes(piso_id);

-- ============================================================
-- CIRCUITOS
-- ============================================================
CREATE TABLE circuitos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proyecto_id UUID REFERENCES proyectos ON DELETE CASCADE NOT NULL,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('alumbrado','tomacorriente','electrobomba','cocina','calentador','secadora','otro')),
    fase INTEGER DEFAULT 1,
    tension_v NUMERIC(6,2) DEFAULT 220,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_circuitos_proyecto ON circuitos(proyecto_id);

-- ============================================================
-- RESULTADOS
-- ============================================================
CREATE TABLE resultados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proyecto_id UUID REFERENCES proyectos ON DELETE CASCADE NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('calculo','cad','cotizacion','expediente')),
    resumen JSONB DEFAULT '{}'::jsonb,
    archivos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_resultados_proyecto ON resultados(proyecto_id);

-- ============================================================
-- TRIGGER: updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_proyectos
    BEFORE UPDATE ON proyectos
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at_pisos
    BEFORE UPDATE ON pisos
    FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

-- ============================================================
-- RLS (Row Level Security)
-- ============================================================
ALTER TABLE proyectos ENABLE ROW LEVEL SECURITY;
ALTER TABLE pisos ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE circuitos ENABLE ROW LEVEL SECURITY;
ALTER TABLE resultados ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuarios ven solo sus proyectos"
    ON proyectos FOR ALL
    USING (user_id = auth.uid());

CREATE POLICY "Pisos ligados a proyectos del usuario"
    ON pisos FOR ALL
    USING (proyecto_id IN (SELECT id FROM proyectos WHERE user_id = auth.uid()));

CREATE POLICY "Ambientes ligados a pisos del usuario"
    ON ambientes FOR ALL
    USING (piso_id IN (SELECT p.id FROM pisos p JOIN proyectos pr ON p.proyecto_id = pr.id WHERE pr.user_id = auth.uid()));

CREATE POLICY "Circuitos ligados a proyectos del usuario"
    ON circuitos FOR ALL
    USING (proyecto_id IN (SELECT id FROM proyectos WHERE user_id = auth.uid()));

CREATE POLICY "Resultados ligados a proyectos del usuario"
    ON resultados FOR ALL
    USING (proyecto_id IN (SELECT id FROM proyectos WHERE user_id = auth.uid()));
