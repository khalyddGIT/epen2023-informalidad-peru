-- =============================================================================
-- PROYECTO BIG DATA: EPEN 2023 (INEI - PERÚ)
-- SCRIPT DDL PARA MICROSOFT SQL SERVER (T-SQL)
-- =============================================================================

-- 1. CREACIÓN DE LA BASE DE DATOS
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DB_EPEN2023')
BEGIN
    CREATE DATABASE DB_EPEN2023;
END
GO

USE DB_EPEN2023;
GO

-- 2. ELIMINACIÓN PREVIA DE TABLAS SI EXISTEN (Para ejecución limpia)
IF OBJECT_ID('dbo.Fact_Empleo', 'U') IS NOT NULL DROP TABLE dbo.Fact_Empleo;
IF OBJECT_ID('dbo.Dim_Departamento', 'U') IS NOT NULL DROP TABLE dbo.Dim_Departamento;
IF OBJECT_ID('dbo.Dim_Demografia', 'U') IS NOT NULL DROP TABLE dbo.Dim_Demografia;
IF OBJECT_ID('dbo.Dim_CondicionLaboral', 'U') IS NOT NULL DROP TABLE dbo.Dim_CondicionLaboral;
GO

-- 3. CREACIÓN DE TABLAS DE DIMENSIÓN (3FN)

CREATE TABLE Dim_Departamento (
    IdDepartamento INT NOT NULL CONSTRAINT PK_Dim_Departamento PRIMARY KEY,
    NombreDepartamento VARCHAR(100) NOT NULL,
    RegionNatural VARCHAR(50) NOT NULL
);
GO

CREATE TABLE Dim_Demografia (
    IdDemografia INT NOT NULL CONSTRAINT PK_Dim_Demografia PRIMARY KEY,
    CodigoSexo INT NOT NULL,
    DescripcionSexo VARCHAR(20) NOT NULL,
    GrupoEdad VARCHAR(50) NOT NULL
);
GO

CREATE TABLE Dim_CondicionLaboral (
    IdCondicion INT NOT NULL CONSTRAINT PK_Dim_CondicionLaboral PRIMARY KEY,
    CodigoOcupacion INT NULL,
    DescripcionCondicion VARCHAR(50) NOT NULL,
    CodigoInformalidad INT NULL,
    DescripcionInformalidad VARCHAR(50) NOT NULL
);
GO

-- 4. CREACIÓN DE TABLA DE HECHOS (Fact_Empleo)

CREATE TABLE Fact_Empleo (
    IdFact INT NOT NULL CONSTRAINT PK_Fact_Empleo PRIMARY KEY,
    IdDepartamento INT NOT NULL,
    IdDemografia INT NOT NULL,
    IdCondicion INT NOT NULL,
    Anio INT NOT NULL,
    Mes INT NOT NULL,
    Edad INT NOT NULL,
    IngresoTotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    HorasTrabajadas DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    FactorPonderador DECIMAL(12, 4) NOT NULL DEFAULT 1.0000,
    CONSTRAINT FK_Fact_Departamento FOREIGN KEY (IdDepartamento) REFERENCES Dim_Departamento(IdDepartamento),
    CONSTRAINT FK_Fact_Demografia FOREIGN KEY (IdDemografia) REFERENCES Dim_Demografia(IdDemografia),
    CONSTRAINT FK_Fact_Condicion FOREIGN KEY (IdCondicion) REFERENCES Dim_CondicionLaboral(IdCondicion)
);
GO

-- 5. CREACIÓN DE ÍNDICES DE ALTO RENDIMIENTO
CREATE INDEX idx_fact_departamento ON Fact_Empleo (IdDepartamento);
GO

CREATE INDEX idx_fact_anio_mes ON Fact_Empleo (Anio, Mes);
GO

CREATE INDEX idx_fact_condicion_ingreso ON Fact_Empleo (IdCondicion, IngresoTotal);
GO

CREATE INDEX idx_fact_dept_condicion_incl ON Fact_Empleo (IdDepartamento, IdCondicion) INCLUDE (IngresoTotal, FactorPonderador);
GO

-- 6. CREACIÓN DE VISTAS ANALÍTICAS

IF OBJECT_ID('dbo.vw_resumen_informalidad_departamento', 'V') IS NOT NULL 
    DROP VIEW dbo.vw_resumen_informalidad_departamento;
GO

CREATE VIEW vw_resumen_informalidad_departamento AS
SELECT 
    d.NombreDepartamento,
    d.RegionNatural,
    COUNT(f.IdFact) AS Total_Encuestados,
    SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1 ELSE 0 END) AS Total_Informales,
    SUM(CASE WHEN c.DescripcionInformalidad = 'Formal' THEN 1 ELSE 0 END) AS Total_Formales,
    CAST(
        ROUND(
            (SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
            NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2
        ) AS DECIMAL(5,2)
    ) AS Tasa_Informalidad_Porcentaje
FROM Fact_Empleo f
INNER JOIN Dim_Departamento d ON f.IdDepartamento = d.IdDepartamento
INNER JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
GROUP BY d.NombreDepartamento, d.RegionNatural;
GO

IF OBJECT_ID('dbo.vw_ingreso_promedio_genero_edad', 'V') IS NOT NULL 
    DROP VIEW dbo.vw_ingreso_promedio_genero_edad;
GO

CREATE VIEW vw_ingreso_promedio_genero_edad AS
SELECT 
    dem.DescripcionSexo,
    dem.GrupoEdad,
    COUNT(f.IdFact) AS Total_Personas_Trabajando,
    CAST(ROUND(AVG(f.IngresoTotal), 2) AS DECIMAL(12,2)) AS Ingreso_Promedio_Soles,
    CAST(ROUND(AVG(f.HorasTrabajadas), 1) AS DECIMAL(8,1)) AS Horas_Promedio_Semanales
FROM Fact_Empleo f
INNER JOIN Dim_Demografia dem ON f.IdDemografia = dem.IdDemografia
INNER JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
WHERE c.DescripcionCondicion = 'Ocupado' AND f.IngresoTotal > 0
GROUP BY dem.DescripcionSexo, dem.GrupoEdad;
GO

-- 7. CREACIÓN DE PROCEDIMIENTO ALMACENADO (STORED PROCEDURE)

IF OBJECT_ID('dbo.sp_obtener_estadisticas_departamento', 'P') IS NOT NULL 
    DROP PROCEDURE dbo.sp_obtener_estadisticas_departamento;
GO

CREATE PROCEDURE sp_obtener_estadisticas_departamento
    @p_id_departamento INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        d.NombreDepartamento,
        COUNT(f.IdFact) AS TotalEncuestados,
        CAST(ROUND(AVG(f.IngresoTotal), 2) AS DECIMAL(12,2)) AS IngresoMedio,
        CAST(
            ROUND(
                (SUM(CASE WHEN c.DescripcionInformalidad = 'Informal' THEN 1.0 ELSE 0.0 END) * 100.0) / 
                NULLIF(SUM(CASE WHEN c.DescripcionInformalidad IN ('Informal', 'Formal') THEN 1.0 ELSE 0.0 END), 0), 2
            ) AS DECIMAL(5,2)
        ) AS InformalidadPct
    FROM Fact_Empleo f
    INNER JOIN Dim_Departamento d ON f.IdDepartamento = d.IdDepartamento
    INNER JOIN Dim_CondicionLaboral c ON f.IdCondicion = c.IdCondicion
    WHERE f.IdDepartamento = @p_id_departamento
    GROUP BY d.NombreDepartamento;
END;
GO
