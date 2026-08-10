-- =============================================================================
-- PROYECTO BIG DATA: EPEN 2023 (INEI - PERÚ)
-- SCRIPT DDL LIMPIO PARA POSTGRESQL (pgAdmin / DBeaver)
-- =============================================================================

-- 1. ELIMINACIÓN DE OBJETOS PREVIOS (EJECUCIÓN LIMPIA Y REPETIBLE)
DROP FUNCTION IF EXISTS sp_obtener_estadisticas_departamento(INT);
DROP VIEW IF EXISTS vw_ingreso_promedio_genero_edad;
DROP VIEW IF EXISTS vw_resumen_informalidad_departamento;
DROP TABLE IF EXISTS Fact_Empleo CASCADE;
DROP TABLE IF EXISTS Dim_CondicionLaboral CASCADE;
DROP TABLE IF EXISTS Dim_Demografia CASCADE;
DROP TABLE IF EXISTS Dim_Departamento CASCADE;

-- 2. CREACIÓN DE TABLAS DE DIMENSIÓN (3FN)

CREATE TABLE Dim_Departamento (
    IdDepartamento INT PRIMARY KEY,
    NombreDepartamento VARCHAR(100) NOT NULL,
    RegionNatural VARCHAR(50) NOT NULL
);

CREATE TABLE Dim_Demografia (
    IdDemografia INT PRIMARY KEY,
    CodigoSexo INT NOT NULL,
    DescripcionSexo VARCHAR(20) NOT NULL,
    GrupoEdad VARCHAR(50) NOT NULL
);

CREATE TABLE Dim_CondicionLaboral (
    IdCondicion INT PRIMARY KEY,
    CodigoOcupacion INT,
    DescripcionCondicion VARCHAR(50) NOT NULL,
    CodigoInformalidad INT,
    DescripcionInformalidad VARCHAR(50) NOT NULL
);

-- 3. CREACIÓN DE TABLA DE HECHOS (Fact_Empleo)

CREATE TABLE Fact_Empleo (
    IdFact INT PRIMARY KEY,
    IdDepartamento INT NOT NULL,
    IdDemografia INT NOT NULL,
    IdCondicion INT NOT NULL,
    Anio INT NOT NULL,
    Mes INT NOT NULL,
    Edad INT NOT NULL,
    IngresoTotal NUMERIC(12, 2) DEFAULT 0.00,
    HorasTrabajadas NUMERIC(8, 2) DEFAULT 0.00,
    FactorPonderador NUMERIC(12, 4) DEFAULT 1.0000,
    CONSTRAINT FK_Fact_Departamento FOREIGN KEY (IdDepartamento) REFERENCES Dim_Departamento(IdDepartamento),
    CONSTRAINT FK_Fact_Demografia FOREIGN KEY (IdDemografia) REFERENCES Dim_Demografia(IdDemografia),
    CONSTRAINT FK_Fact_Condicion FOREIGN KEY (IdCondicion) REFERENCES Dim_CondicionLaboral(IdCondicion)
);

-- 4. CREACIÓN DE ÍNDICES DE ALTO RENDIMIENTO
CREATE INDEX idx_fact_departamento ON Fact_Empleo (IdDepartamento);
CREATE INDEX idx_fact_anio_mes ON Fact_Empleo (Anio, Mes);
CREATE INDEX idx_fact_condicion_ingreso ON Fact_Empleo (IdCondicion, IngresoTotal);

-- 5. CREACIÓN DE VISTAS ANALÍTICAS

CREATE VIEW vw_resumen_informalidad_departamento AS
SELECT 
    d.NombreDepartamento,
    d.RegionNatural,
    COUNT(f.IdFact) AS Total_Encuestados,
    SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1 ELSE 0 END) AS Total_Informales,
    SUM(CASE WHEN c.DescripcionInformalidad = 'Formal' THEN 1 ELSE 0 END) AS Total_Formales,
    ROUND(
        (SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
        NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2
    ) AS Tasa_Informalidad_Porcentaje
FROM Fact_Empleo f
JOIN Dim_Departamento d ON f.IdDepartamento = d.IdDepartamento
JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
GROUP BY d.NombreDepartamento, d.RegionNatural;

CREATE VIEW vw_ingreso_promedio_genero_edad AS
SELECT 
    dem.DescripcionSexo,
    dem.GrupoEdad,
    COUNT(f.IdFact) AS Total_Personas_Trabajando,
    ROUND(AVG(f.IngresoTotal), 2) AS Ingreso_Promedio_Soles,
    ROUND(AVG(f.HorasTrabajadas), 1) AS Horas_Promedio_Semanales
FROM Fact_Empleo f
JOIN Dim_Demografia dem ON f.IdDemografia = dem.IdDemografia
JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
WHERE c.DescripcionCondicion = 'Ocupado' AND f.IngresoTotal > 0
GROUP BY dem.DescripcionSexo, dem.GrupoEdad;

-- 6. CREACIÓN DE PROCEDIMIENTO ALMACENADO (PL/pgSQL)

CREATE OR REPLACE FUNCTION sp_obtener_estadisticas_departamento(p_id_departamento INT)
RETURNS TABLE (
    Departamento VARCHAR,
    TotalEncuestados BIGINT,
    IngresoMedio NUMERIC,
    InformalidadPct NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.NombreDepartamento::VARCHAR,
        COUNT(f.IdFact) AS TotalEncuestados,
        ROUND(AVG(f.IngresoTotal), 2) AS IngresoMedio,
        ROUND(
            (SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
            NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2
        ) AS InformalidadPct
    FROM Fact_Empleo f
    JOIN Dim_Departamento d ON f.IdDepartamento = d.IdDepartamento
    JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
    WHERE f.IdDepartamento = p_id_departamento
    GROUP BY d.NombreDepartamento;
END;
$$ LANGUAGE plpgsql;
