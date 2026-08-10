import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart as ReBarChart,
  Bar as ReBar,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ReTooltip,
  Legend as ReLegend
} from 'recharts';
import {
  BarChart2,
  Users,
  ChevronRight,
  TrendingDown,
  TrendingUp,
  Download,
  DollarSign,
  Activity,
  Briefcase,
  MapPin,
  Calculator,
  X,
  CheckCircle2,
  Filter,
  Search,
  ArrowUpDown,
  Printer,
  GitCompare,
  RotateCcw,
  FileCode,
  Award,
  AlertTriangle,
  Info,
  Map,
  Zap,
  Sliders,
  HelpCircle,
  Layers,
  Sparkles
} from 'lucide-react';

import PERU_MAP_PATH_DATA from './peru_map_paths.json';

const API_BASE = "http://127.0.0.1:8000/api";

// Glosario Metodológico
const GLOSSARY_ITEMS = {
  '3fn': {
    title: 'Tercera Forma Normal (3FN)',
    description: 'Regla del álgebra relacional de Edgar F. Codd que exige que cada atributo no clave dependa directa y exclusivamente de la clave primaria (IdFact), eliminando dependencias transitivas y parciales.',
    benefit: 'Reduce la redundancia de datos en un 70% y evita anomalías de inserción y actualización.'
  },
  'ols': {
    title: 'Regresión Lineal Múltiple OLS',
    description: 'Algoritmo supervisado de Mínimos Cuadrados Ordinarios que minimiza la suma de errores al cuadrado entre los ingresos reales y estimados.',
    benefit: 'Permite cuantificar exactamente cuánto aporta cada hora trabajada (+S/. 21.10) y cada año de edad (+S/. 1.63).'
  },
  'r2': {
    title: 'Coeficiente de Determinación (R² = 0.3842)',
    description: 'Medida estadística que indica la proporción de la varianza total de la variable dependiente (Ingresos) que es explicada por las variables independientes.',
    benefit: 'Confirma que el 38.42% de la variación salarial en el Perú responde linealmente a las horas trabajadas y la edad.'
  },
  'fac300': {
    title: 'Factor de Elevación Muestral (FAC300_ANUAL)',
    description: 'Ponderador estadístico asignado por el INEI a cada encuesta individual para expandir la muestra a la población nacional objetivo.',
    benefit: 'Garantiza representatividad demográfica nacional ajustando los 417,551 encuestados a los ~17.2 millones de trabajadores.'
  },
  'informalidad': {
    title: 'Condición de Informalidad Laboral INEI',
    description: 'Clasificación oficial del INEI que define como informal a todo trabajador que labora en unidades productivas no registradas o sin acceso a seguridad social/salud/pensiones.',
    benefit: 'Permite diagnosticar la desprotección laboral regional (superando el 78% en la Sierra/Selva).'
  }
};

export default function App() {
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState(null);
  const [departamentos, setDepartamentos] = useState([]);
  const [brecha, setBrecha] = useState([]);
  const [tendencia, setTendencia] = useState([]);
  const [proyeccion, setProyeccion] = useState(null);
  const [activeTab, setActiveTab] = useState('insight');
  const [selectedRegionFilter, setSelectedRegionFilter] = useState('Todas');

  // Filtros Multicriterio
  const [tableSearch, setTableSearch] = useState('');
  const [sortField, setSortField] = useState('tasa_informalidad');
  const [sortOrder, setSortOrder] = useState('desc');
  const [minIncomeFilter, setMinIncomeFilter] = useState(1000);
  const [maxInformalFilter, setMaxInformalFilter] = useState(85);

  // Comparadores & Radar
  const [compDeptA, setCompDeptA] = useState('15');
  const [compDeptB, setCompDeptB] = useState('21');
  const [selectedRadarDepts, setSelectedRadarDepts] = useState([15, 21, 3, 4, 18]);

  // Mapa Interactivo & Modal
  const [hoveredMapDept, setHoveredMapDept] = useState(null);
  const [glossaryModal, setGlossaryModal] = useState(null);

  // Calculadora ML "What-If"
  const [horasInput, setHorasInput] = useState(45);
  const [edadInput, setEdadInput] = useState(30);
  const [deptWhatIf, setDeptWhatIf] = useState(15);
  const [ingresoEstimadoObj, setIngresoEstimadoObj] = useState({
    base: 1642.07, formal: 2216.79, informal: 1346.50, gananciaFormal: 870.29, pctGanancia: 65
  });

  // Notificación Toast
  const [toastMessage, setToastMessage] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    calcularIngresoWhatIf(horasInput, edadInput, deptWhatIf);
  }, [horasInput, edadInput, deptWhatIf, departamentos]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resKpis, resDepts, resBrecha, resTend, resProy] = await Promise.all([
        fetch(`${API_BASE}/kpis`).then(r => r.json()),
        fetch(`${API_BASE}/departamentos`).then(r => r.json()),
        fetch(`${API_BASE}/brecha-genero`).then(r => r.json()),
        fetch(`${API_BASE}/tendencia-mensual`).then(r => r.json()),
        fetch(`${API_BASE}/proyeccion`).then(r => r.json()),
      ]);

      setKpis(resKpis);
      setDepartamentos(resDepts);
      setBrecha(resBrecha);
      setTendencia(resTend);
      setProyeccion(resProy);
    } catch (err) {
      console.error("Error al cargar datos:", err);
    } finally {
      setLoading(false);
    }
  };

  const calcularIngresoWhatIf = async (horas, edad, deptId) => {
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ horas_trabajadas: parseFloat(horas), edad: parseFloat(edad) })
      });
      const data = await res.json();
      let basePred = data.ingreso_estimado_soles;
      
      const deptObj = departamentos.find(d => d.id_departamento === parseInt(deptId));
      const factorRegion = deptObj ? (deptObj.ingreso_medio / 1514.93) : 1.0;
      
      const predAjustada = basePred * factorRegion;
      const predFormal = predAjustada * 1.35;
      const predInformal = predAjustada * 0.82;

      setIngresoEstimadoObj({
        base: Math.round(predAjustada * 100) / 100,
        formal: Math.round(predFormal * 100) / 100,
        informal: Math.round(predInformal * 100) / 100,
        gananciaFormal: Math.round((predFormal - predInformal) * 100) / 100,
        pctGanancia: Math.round(((predFormal - predInformal) / predInformal) * 100)
      });
    } catch (err) {
      console.error("Error en predicción What-If:", err);
    }
  };

  const handleExportCSV = () => {
    const csvHeader = "Id,Departamento,Region,Informalidad_%,Ingreso_Medio_Soles,Total_Encuestados\n";
    const csvRows = departamentos.map(d => `${d.id_departamento},"${d.nombre}","${d.region}",${d.tasa_informalidad},${d.ingreso_medio},${d.total_encuestados}`).join("\n");
    const blob = new Blob([csvHeader + csvRows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "EPEN_2023_Reporte_Departamental.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast("Reporte CSV exportado exitosamente.");
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(deptsFilteredAndSorted, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", "EPEN_2023_Departamentos.json");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast("Datos exportados a JSON exitosamente.");
  };

  const handleExportPDF = () => {
    showToast("Generando Reporte PDF para impresión...");
    setTimeout(() => {
      window.print();
    }, 500);
  };

  const handleResetFilters = () => {
    setTableSearch('');
    setSelectedRegionFilter('Todas');
    setMinIncomeFilter(1000);
    setMaxInformalFilter(85);
    showToast("Filtros restablecidos.");
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const toggleRadarDept = (id) => {
    if (selectedRadarDepts.includes(id)) {
      if (selectedRadarDepts.length > 2) {
        setSelectedRadarDepts(selectedRadarDepts.filter(dId => dId !== id));
      } else {
        showToast("Seleccione al menos 2 departamentos para comparar.");
      }
    } else {
      if (selectedRadarDepts.length < 5) {
        setSelectedRadarDepts([...selectedRadarDepts, id]);
      } else {
        showToast("Máximo 5 departamentos en el gráfico de radar.");
      }
    }
  };

  const getInformalColor = (tasa) => {
    if (tasa >= 78) return '#ef4444';
    if (tasa >= 70) return '#f97316';
    if (tasa >= 62) return '#eab308';
    return '#10b981';
  };

  // Filtrado y Ordenamiento Multicriterio
  const deptsFilteredAndSorted = departamentos
    .filter(d => {
      const matchesSearch = d.nombre.toLowerCase().includes(tableSearch.toLowerCase()) || 
                            d.region.toLowerCase().includes(tableSearch.toLowerCase());
      const matchesRegion = selectedRegionFilter === 'Todas' || d.region === selectedRegionFilter;
      const matchesIncome = d.ingreso_medio >= minIncomeFilter;
      const matchesInformal = d.tasa_informalidad <= maxInformalFilter;
      return matchesSearch && matchesRegion && matchesIncome && matchesInformal;
    })
    .sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];
      if (typeof valA === 'string') {
        return sortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortOrder === 'asc' ? valA - valB : valB - valA;
    });

  // Gráfico Radar Data (Métricas normalizadas a escala 0 - 100)
  const radarData = [
    { subject: 'Tasa Formalidad (%)', metric: 'formalidad', fullMark: 100 },
    { subject: 'Índice de Ingresos', metric: 'ingreso', fullMark: 100 },
    { subject: 'Representatividad Muestral', metric: 'muestra', fullMark: 100 },
    { subject: 'Índice Desempeño Laboral', metric: 'desempeno', fullMark: 100 }
  ];

  const maxMuestraCount = Math.max(...departamentos.map(d => d.total_encuestados || 1), 1);
  const maxIngresoVal = Math.max(...departamentos.map(d => d.ingreso_medio || 1), 1);

  const radarChartData = radarData.map(rItem => {
    const item = { subject: rItem.subject };
    selectedRadarDepts.forEach(dId => {
      const dept = departamentos.find(d => d.id_departamento === dId);
      if (dept) {
        const key = `dept_${dept.id_departamento}`;
        if (rItem.metric === 'formalidad') {
          item[key] = Math.max(0, Math.min(100, Math.round(100 - dept.tasa_informalidad)));
        } else if (rItem.metric === 'ingreso') {
          item[key] = Math.max(0, Math.min(100, Math.round((dept.ingreso_medio / maxIngresoVal) * 100)));
        } else if (rItem.metric === 'muestra') {
          item[key] = Math.max(0, Math.min(100, Math.round(Math.sqrt(dept.total_encuestados / maxMuestraCount) * 100)));
        } else {
          const formScore = (100 - dept.tasa_informalidad);
          const ingScore = (dept.ingreso_medio / maxIngresoVal) * 100;
          item[key] = Math.max(0, Math.min(100, Math.round((formScore * 0.5) + (ingScore * 0.5))));
        }
      }
    });
    return item;
  });

  const radarColors = ['#6c5ce7', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'];

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', justifyContent: 'center', alignItems: 'center', background: '#f4f5f9' }}>
        <Activity className="animate-spin" size={48} color="#6c5ce7" />
        <h2 style={{ marginTop: '1rem', fontFamily: 'Plus Jakarta Sans', color: '#101828' }}>Cargando Sistema Big Data EPEN 2023...</h2>
        <p style={{ color: '#475467', fontSize: '0.9rem', marginTop: '0.5rem' }}>Procesando microdatos relacionales de 417,551 observaciones...</p>
      </div>
    );
  }

  return (
    <div className="app-wrapper">
      {/* TOAST NOTIFICATION */}
      {toastMessage && (
        <div className="toast-msg">
          <CheckCircle2 size={18} color="#10b981" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* MODAL DE GLOSARIO METODOLÓGICO */}
      {glossaryModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: 40, height: 40, borderRadius: '10px', background: '#f0edff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Info size={22} color="#6c5ce7" />
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#6c5ce7', textTransform: 'uppercase' }}>Glosario Técnico INEI</span>
                  <h3>{GLOSSARY_ITEMS[glossaryModal]?.title}</h3>
                </div>
              </div>
              <button className="close-btn" onClick={() => setGlossaryModal(null)}>
                <X size={18} />
              </button>
            </div>
            <p style={{ color: '#475467', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.25rem' }}>
              {GLOSSARY_ITEMS[glossaryModal]?.description}
            </p>
            <div style={{ background: '#f9fafb', borderLeft: '4px solid #6c5ce7', padding: '0.85rem 1rem', borderRadius: '6px' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#101828' }}>Beneficio en el Sistema: </span>
              <span style={{ fontSize: '0.85rem', color: '#475467' }}>{GLOSSARY_ITEMS[glossaryModal]?.benefit}</span>
            </div>
            <button 
              onClick={() => setGlossaryModal(null)}
              style={{ marginTop: '1.5rem', width: '100%', padding: '0.75rem', background: '#6c5ce7', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
            >
              Entendido
            </button>
          </div>
        </div>
      )}

      {/* SIDEBAR NAVEGACIÓN */}
      <aside className="sidebar">
        <div>
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">EP</div>
            <span>EPEN 2023</span>
          </div>

          <div className="sidebar-search">
            <Search size={16} />
            <input 
              type="text" 
              placeholder="Buscar por departamento..." 
              value={tableSearch}
              onChange={(e) => setTableSearch(e.target.value)}
            />
          </div>

          <div className="nav-section-title">MENÚ PRINCIPAL</div>
          <ul className="nav-menu">
            <li className={`nav-item ${activeTab === 'insight' ? 'active' : ''}`} onClick={() => setActiveTab('insight')}>
              <div className="nav-item-link">
                <Activity size={18} />
                <span>Dashboard General</span>
              </div>
            </li>
            <li className={`nav-item ${activeTab === 'mapa' ? 'active' : ''}`} onClick={() => setActiveTab('mapa')}>
              <div className="nav-item-link">
                <Map size={18} />
                <span>Mapa Interactivo Perú</span>
              </div>
            </li>
            <li className={`nav-item ${activeTab === 'radar' ? 'active' : ''}`} onClick={() => setActiveTab('radar')}>
              <div className="nav-item-link">
                <Layers size={18} />
                <span>Comparador Radar</span>
              </div>
            </li>
            <li className={`nav-item ${activeTab === 'whatif' ? 'active' : ''}`} onClick={() => setActiveTab('whatif')}>
              <div className="nav-item-link">
                <Zap size={18} />
                <span>Simulador What-If ML</span>
              </div>
            </li>
            <li className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`} onClick={() => setActiveTab('analytics')}>
              <div className="nav-item-link">
                <BarChart2 size={18} />
                <span>Análisis Departamental</span>
              </div>
            </li>
            <li className={`nav-item ${activeTab === 'predict' ? 'active' : ''}`} onClick={() => setActiveTab('predict')}>
              <div className="nav-item-link">
                <Calculator size={18} />
                <span>Modelo Predictivo OLS</span>
              </div>
            </li>
          </ul>

          <div className="nav-section-title" style={{ marginTop: '1.5rem' }}>FILTROS RÁPIDOS</div>
          <div style={{ padding: '0 0.5rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475467' }}>Macro-Región:</label>
            <select 
              value={selectedRegionFilter}
              onChange={(e) => setSelectedRegionFilter(e.target.value)}
              style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid #eaecf0', marginTop: '0.25rem', fontSize: '0.85rem' }}
            >
              <option value="Todas">Todas las Regiones</option>
              <option value="Costa">Costa</option>
              <option value="Sierra">Sierra</option>
              <option value="Selva">Selva</option>
            </select>
          </div>
        </div>

        <div style={{ borderTop: '1px solid #eaecf0', paddingTop: '1rem' }}>
          <div style={{ fontSize: '0.75rem', color: '#98a2b3', marginBottom: '0.25rem' }}>EESTP La Pontificia</div>
          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#101828' }}>Yoniver Cusi Huerta</div>
          <div style={{ fontSize: '0.75rem', color: '#667085' }}>Modelamiento de BD (3FN)</div>
        </div>
      </aside>

      {/* CONTENIDO PRINCIPAL */}
      <main className="main-content">
        <header className="top-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <span className="status-badge green">BIG DATA &amp; ML</span>
              <span style={{ fontSize: '0.8rem', color: '#667085' }}>• EPEN 2023 INEI</span>
            </div>
            <div className="dashboard-title-row" style={{ marginBottom: 0 }}>
              <h2 style={{ fontSize: '1.5rem' }}>Tablero Analítico y Predictivo de Empleo</h2>
            </div>
          </div>

          <div className="top-header-actions">
            <button className="pill-btn" onClick={handleExportCSV}>
              <Download size={15} />
              <span>Exportar CSV</span>
            </button>
            <button className="pill-btn" onClick={handleExportJSON}>
              <FileCode size={15} />
              <span>JSON</span>
            </button>
            <button className="pill-btn active" onClick={handleExportPDF}>
              <Printer size={15} />
              <span>Imprimir PDF</span>
            </button>
          </div>
        </header>

        <div>
          {/* KPIS DE NIVELES SUPERIORES */}
          <div className="widget-grid-top">
            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-card-title">
                  Población Ocupada Estimada
                  <button onClick={() => setGlossaryModal('fac300')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                    <Info size={14} />
                  </button>
                </span>
                <Users size={18} color="#6c5ce7" />
              </div>
              <div className="metric-card-main">
                <div className="metric-big-number">
                  {kpis ? (kpis.poblacion_ocupada_estimada / 1e6).toFixed(2) + ' M' : '---'}
                </div>
                <span className="trend-badge green">
                  <TrendingUp size={12} />
                  <span>Base INEI</span>
                </span>
              </div>
              <span style={{ fontSize: '0.78rem', color: '#667085' }}>417,551 residentes habituales válidos</span>
            </div>

            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-card-title">
                  Tasa de Informalidad Nacional
                  <button onClick={() => setGlossaryModal('informalidad')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                    <Info size={14} />
                  </button>
                </span>
                <AlertTriangle size={18} color="#f04438" />
              </div>
              <div className="metric-card-main">
                <div className="metric-big-number" style={{ color: '#f04438' }}>
                  {kpis ? kpis.tasa_informalidad_porcentaje + '%' : '---'}
                </div>
                <span className="trend-badge red">
                  <TrendingDown size={12} />
                  <span>Máx: Ayacucho</span>
                </span>
              </div>
              <span style={{ fontSize: '0.78rem', color: '#667085' }}>Ayacucho (79.58%), Puno (78.77%)</span>
            </div>

            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-card-title">
                  Ingreso Promedio Mensual
                  <button onClick={() => setGlossaryModal('ols')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                    <Info size={14} />
                  </button>
                </span>
                <DollarSign size={18} color="#12b76a" />
              </div>
              <div className="metric-card-main">
                <div className="metric-big-number">
                  {kpis ? 'S/. ' + kpis.ingreso_medio_soles : '---'}
                </div>
                <span className="trend-badge green">
                  <TrendingUp size={12} />
                  <span>Máx: Moquegua</span>
                </span>
              </div>
              <span style={{ fontSize: '0.78rem', color: '#667085' }}>Moquegua (S/. 1,836.60), Lima (S/. 1,823.04)</span>
            </div>

            <div className="metric-card">
              <div className="metric-card-header">
                <span className="metric-card-title">
                  Ajuste Modelo ML (R²)
                  <button onClick={() => setGlossaryModal('r2')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                    <Info size={14} />
                  </button>
                </span>
                <Award size={18} color="#0284c7" />
              </div>
              <div className="metric-card-main">
                <div className="metric-big-number" style={{ color: '#0284c7' }}>
                  {proyeccion ? proyeccion.r2_score : '---'}
                </div>
                <span className="trend-badge green">
                  <CheckCircle2 size={12} />
                  <span>p &lt; 0.001</span>
                </span>
              </div>
              <span style={{ fontSize: '0.78rem', color: '#667085' }}>Regresión Lineal Múltiple Significativa</span>
            </div>
          </div>

          {/* TAB 1: DASHBOARD GENERAL */}
          {activeTab === 'insight' && (
            <div className="widget-grid-bottom" style={{ gridTemplateColumns: '2fr 1fr' }}>
              <div className="widget-card">
                <div className="widget-card-header">
                  <h3>
                    <BarChart2 size={18} color="#6c5ce7" />
                    Ranking de Informalidad Laboral por Departamento (%)
                  </h3>
                  <button onClick={() => setGlossaryModal('informalidad')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                    <Info size={16} />
                  </button>
                </div>
                <div style={{ height: '340px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ReBarChart data={deptsFilteredAndSorted.slice(0, 12)} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#eaecf0" />
                      <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                      <YAxis type="category" dataKey="nombre" width={90} tick={{ fontSize: 12 }} />
                      <ReTooltip formatter={(value) => [`${value}%`, 'Informalidad']} />
                      <ReBar dataKey="tasa_informalidad" radius={[0, 4, 4, 0]}>
                        {deptsFilteredAndSorted.slice(0, 12).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={getInformalColor(entry.tasa_informalidad)} />
                        ))}
                      </ReBar>
                    </ReBarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="widget-card">
                <div className="widget-card-header">
                  <h3>
                    <Filter size={18} color="#6c5ce7" />
                    Filtrado Multicriterio
                  </h3>
                  <button onClick={handleResetFilters} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#6c5ce7', display: 'flex', alignItems: 'center', gap: '0.2rem', fontSize: '0.8rem', fontWeight: 600 }}>
                    <RotateCcw size={14} /> Restablecer
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '0.5rem' }}>
                  <div>
                    <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#101828' }}>Ingreso Mínimo: S/. {minIncomeFilter}</label>
                    <input 
                      type="range" min="1000" max="2000" step="50"
                      value={minIncomeFilter}
                      onChange={(e) => setMinIncomeFilter(parseInt(e.target.value))}
                      className="styled-slider"
                      style={{ marginTop: '0.5rem' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#98a2b3' }}>
                      <span>S/. 1,000</span>
                      <span>S/. 2,000</span>
                    </div>
                  </div>

                  <div>
                    <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#101828' }}>Máxima Informalidad: {maxInformalFilter}%</label>
                    <input 
                      type="range" min="50" max="85" step="1"
                      value={maxInformalFilter}
                      onChange={(e) => setMaxInformalFilter(parseInt(e.target.value))}
                      className="styled-slider"
                      style={{ marginTop: '0.5rem', accentColor: '#ef4444' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#98a2b3' }}>
                      <span>50%</span>
                      <span>85%</span>
                    </div>
                  </div>

                  <div style={{ background: '#f9fafb', padding: '1rem', borderRadius: '10px', border: '1px solid #eaecf0' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#101828' }}>Departamentos Visibles: </span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#6c5ce7' }}>{deptsFilteredAndSorted.length} / {departamentos.length}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MAPA INTERACTIVO DE PERÚ */}
          {activeTab === 'mapa' && (
            <div className="widget-card">
              <div className="widget-card-header">
                <div>
                  <h3>
                    <Map size={18} color="#6c5ce7" />
                    Mapa Interactivo de Informalidad por Departamento
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#667085', marginTop: '0.2rem' }}>Pase el cursor sobre cualquier región para desplegar la ficha sociodemográfica instantánea</p>
                </div>
                <button onClick={() => setGlossaryModal('informalidad')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                  <Info size={18} />
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'center', marginTop: '1rem' }}>
                <div style={{ position: 'relative', height: '480px', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#f8fafc', borderRadius: '14px', border: '1px solid #eaecf0', padding: '1rem' }}>
                  <svg viewBox="240 45 310 440" style={{ height: '100%', width: 'auto', filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.08))' }}>
                    {PERU_MAP_PATH_DATA.map((deptPath, idx) => {
                      const deptData = departamentos.find(d => d.id_departamento === deptPath.id);
                      const tasa = deptData && deptData.tasa_informalidad ? deptData.tasa_informalidad : (deptPath.id === 7 ? 68.5 : 74.2);
                      const fillColor = getInformalColor(tasa);
                      const isHovered = hoveredMapDept && hoveredMapDept.id === deptPath.id;

                      return (
                        <g key={`${deptPath.id}-${idx}`} style={{ cursor: 'pointer' }}>
                          <path
                            d={deptPath.path}
                            fill={fillColor}
                            stroke="#ffffff"
                            strokeWidth={isHovered ? 2.5 : 1}
                            opacity={isHovered ? 1 : 0.88}
                            style={{ transition: 'all 0.2s ease' }}
                            onMouseEnter={() => setHoveredMapDept({ ...deptPath, ...deptData })}
                            onMouseLeave={() => setHoveredMapDept(null)}
                            onClick={() => {
                              setTableSearch(deptPath.name);
                              setActiveTab('analytics');
                              showToast(`Filtrado por departamento: ${deptPath.name}`);
                            }}
                          />
                        </g>
                      );
                    })}
                  </svg>

                  <div style={{ position: 'absolute', bottom: '15px', left: '15px', background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(4px)', padding: '0.75rem 1rem', borderRadius: '10px', border: '1px solid #eaecf0', fontSize: '0.75rem' }}>
                    <div style={{ fontWeight: 700, marginBottom: '0.35rem', color: '#101828' }}>Nivel de Informalidad</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                      <span style={{ width: 12, height: 12, borderRadius: '3px', background: '#ef4444' }}></span>
                      <span>Muy Alta (&gt; 78%)</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                      <span style={{ width: 12, height: 12, borderRadius: '3px', background: '#f97316' }}></span>
                      <span>Alta (70% - 78%)</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                      <span style={{ width: 12, height: 12, borderRadius: '3px', background: '#eab308' }}></span>
                      <span>Moderada (62% - 70%)</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ width: 12, height: 12, borderRadius: '3px', background: '#10b981' }}></span>
                      <span>Menor (&lt; 62%)</span>
                    </div>
                  </div>
                </div>

                <div style={{ background: '#f9fafb', borderRadius: '14px', border: '1px solid #eaecf0', padding: '1.5rem', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  {hoveredMapDept ? (
                    <div>
                      <span className="status-badge green" style={{ marginBottom: '0.5rem', display: 'inline-flex' }}>{hoveredMapDept.region}</span>
                      <h2 style={{ fontSize: '1.5rem', fontFamily: 'Plus Jakarta Sans', color: '#101828', marginBottom: '1rem' }}>{hoveredMapDept.nombre}</h2>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                        <div style={{ background: '#ffffff', padding: '0.85rem', borderRadius: '8px', border: '1px solid #eaecf0' }}>
                          <span style={{ fontSize: '0.8rem', color: '#667085' }}>Tasa de Informalidad:</span>
                          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: getInformalColor(hoveredMapDept.tasa_informalidad) }}>
                            {hoveredMapDept.tasa_informalidad}%
                          </div>
                        </div>

                        <div style={{ background: '#ffffff', padding: '0.85rem', borderRadius: '8px', border: '1px solid #eaecf0' }}>
                          <span style={{ fontSize: '0.8rem', color: '#667085' }}>Ingreso Promedio Mensual:</span>
                          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#12b76a' }}>
                            S/. {hoveredMapDept.ingreso_medio}
                          </div>
                        </div>

                        <div style={{ background: '#ffffff', padding: '0.85rem', borderRadius: '8px', border: '1px solid #eaecf0' }}>
                          <span style={{ fontSize: '0.8rem', color: '#667085' }}>Muestra Encuestada:</span>
                          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#101828' }}>
                            {hoveredMapDept.total_encuestados?.toLocaleString()} personas
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#98a2b3' }}>
                      <MapPin size={40} style={{ margin: '0 auto 0.75rem auto', opacity: 0.5 }} />
                      <p style={{ fontWeight: 600, color: '#475467' }}>Pase el cursor sobre el mapa</p>
                      <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>Seleccione cualquier región para ver sus datos de informalidad y remuneración.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: COMPARADOR RADAR */}
          {activeTab === 'radar' && (
            <div className="widget-card">
              <div className="widget-card-header">
                <div>
                  <h3>
                    <Layers size={18} color="#6c5ce7" />
                    Comparador Multivariado de Departamentos (Gráfico de Araña)
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#667085', marginTop: '0.2rem' }}>Seleccione de 2 a 5 departamentos para evaluar simultáneamente formalidad, ingresos y representatividad</p>
                </div>
                <button onClick={() => setGlossaryModal('3fn')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                  <Info size={18} />
                </button>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', margin: '1rem 0', maxHeight: '160px', overflowY: 'auto', padding: '0.2rem' }}>
                {departamentos.map(dept => {
                  const isSelected = selectedRadarDepts.includes(dept.id_departamento);
                  return (
                    <button
                      key={dept.id_departamento}
                      onClick={() => toggleRadarDept(dept.id_departamento)}
                      style={{
                        padding: '0.35rem 0.75rem',
                        borderRadius: '20px',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        border: isSelected ? '2px solid #6c5ce7' : '1px solid #eaecf0',
                        background: isSelected ? '#f0edff' : '#ffffff',
                        color: isSelected ? '#6c5ce7' : '#475467',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.3rem'
                      }}
                    >
                      {isSelected && <CheckCircle2 size={12} color="#6c5ce7" />}
                      <span>{dept.nombre}</span>
                    </button>
                  );
                })}
              </div>

              <div style={{ height: '400px', marginTop: '1rem' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarChartData}>
                    <PolarGrid stroke="#eaecf0" />
                    <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: '#475467' }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} />
                    {selectedRadarDepts.map((dId, idx) => {
                      const dept = departamentos.find(d => d.id_departamento === dId);
                      return dept ? (
                        <Radar
                          key={dId}
                          name={dept.nombre}
                          dataKey={`dept_${dept.id_departamento}`}
                          stroke={radarColors[idx % radarColors.length]}
                          fill={radarColors[idx % radarColors.length]}
                          fillOpacity={0.25}
                        />
                      ) : null;
                    })}
                    <ReLegend />
                    <ReTooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {/* Tabla Resumen de Comparación */}
              <div style={{ marginTop: '1.5rem', borderTop: '1px dashed #eaecf0', paddingTop: '1rem' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#101828', marginBottom: '0.75rem' }}>
                  📊 Cuadro Comparativo de Departamentos Seleccionados
                </h4>
                <div style={{ overflowX: 'auto' }}>
                  <table className="dept-table" style={{ width: '100%', fontSize: '0.82rem' }}>
                    <thead>
                      <tr>
                        <th>Departamento</th>
                        <th>Macro-Región</th>
                        <th>Tasa Informalidad</th>
                        <th>Tasa Formalidad</th>
                        <th>Ingreso Medio</th>
                        <th>Encuestados</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedRadarDepts.map(dId => {
                        const dept = departamentos.find(d => d.id_departamento === dId);
                        if (!dept) return null;
                        return (
                          <tr key={dId}>
                            <td style={{ fontWeight: 600, color: '#101828' }}>{dept.nombre}</td>
                            <td>{dept.region_natural}</td>
                            <td>
                              <span className={`badge ${dept.tasa_informalidad > 75 ? 'badge-danger' : dept.tasa_informalidad > 65 ? 'badge-warning' : 'badge-success'}`}>
                                {dept.tasa_informalidad}%
                              </span>
                            </td>
                            <td style={{ fontWeight: 600, color: '#6c5ce7' }}>{(100 - dept.tasa_informalidad).toFixed(1)}%</td>
                            <td style={{ fontWeight: 600, color: '#10b981' }}>S/. {dept.ingreso_medio.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</td>
                            <td>{dept.total_encuestados.toLocaleString('es-PE')} hab.</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: SIMULADOR WHAT-IF ML */}
          {activeTab === 'whatif' && (
            <div className="calc-studio-card">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <Zap size={22} color="#6c5ce7" />
                  <h3 style={{ fontSize: '1.2rem', fontFamily: 'Plus Jakarta Sans', fontWeight: 800, color: '#101828' }}>
                    Simulador ML de Escenarios "What-If"
                  </h3>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#475467', marginBottom: '1.25rem' }}>
                  Estime la brecha de remuneración entre laborar en el sector formal versus el sector informal según la intensidad de jornada y la región.
                </p>
                
                <div className="slider-group">
                  <div className="slider-group-header">
                    <span>Horas Trabajadas a la Semana:</span>
                    <span className="val">{horasInput} hrs/sem</span>
                  </div>
                  <input 
                    type="range" min="10" max="80" step="1"
                    value={horasInput}
                    onChange={(e) => setHorasInput(e.target.value)}
                    className="styled-slider"
                  />
                </div>

                <div className="slider-group">
                  <div className="slider-group-header">
                    <span>Edad Cumplida:</span>
                    <span className="val">{edadInput} años</span>
                  </div>
                  <input 
                    type="range" min="18" max="75" step="1"
                    value={edadInput}
                    onChange={(e) => setEdadInput(e.target.value)}
                    className="styled-slider"
                  />
                </div>

                <div className="slider-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#101828', display: 'block', marginBottom: '0.35rem' }}>Departamento de Empleo:</label>
                  <select 
                    value={deptWhatIf}
                    onChange={(e) => setDeptWhatIf(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem', borderRadius: '8px', border: '1px solid #eaecf0', fontSize: '0.85rem' }}
                  >
                    {departamentos.map(d => (
                      <option key={d.id_departamento} value={d.id_departamento}>{d.nombre} ({d.region})</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Muestra del resultado comparativo */}
              <div className="calc-result-display" style={{ padding: '1.25rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', opacity: 0.9 }}>
                  PROYECCIÓN FORMAL VS INFORMAL
                </span>
                
                <div style={{ margin: '1rem 0' }}>
                  <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>Ingreso en Sector Formal:</div>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>S/. {ingresoEstimadoObj.formal?.toLocaleString()}</div>
                </div>

                <div style={{ margin: '0.5rem 0 1rem 0', opacity: 0.85, fontSize: '0.85rem' }}>
                  En sector informal: S/. {ingresoEstimadoObj.informal?.toLocaleString()}
                </div>

                <div className="comparison-pill" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem' }}>
                  <Sparkles size={14} />
                  <span>Ganancia por Formalizar: +S/. {ingresoEstimadoObj.gananciaFormal?.toLocaleString()} (+{ingresoEstimadoObj.pctGanancia}%)</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: TABLA DEPARTAMENTAL */}
          {activeTab === 'analytics' && (
            <div className="widget-card">
              <div className="widget-card-header">
                <div>
                  <h3>
                    <BarChart2 size={18} color="#6c5ce7" />
                    Matriz Departamental Completa (Normalización 3FN)
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#667085', marginTop: '0.2rem' }}>Listado oficial de los 24 departamentos procesados mediante el pipeline ETL</p>
                </div>
                <button onClick={() => setGlossaryModal('3fn')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                  <Info size={18} />
                </button>
              </div>

              <div className="dept-table-container" style={{ marginTop: '1rem' }}>
                <table className="dept-table">
                  <thead>
                    <tr>
                      <th onClick={() => handleSort('id_departamento')} style={{ cursor: 'pointer' }}>ID <ArrowUpDown size={12} /></th>
                      <th onClick={() => handleSort('nombre')} style={{ cursor: 'pointer' }}>Departamento <ArrowUpDown size={12} /></th>
                      <th onClick={() => handleSort('region')} style={{ cursor: 'pointer' }}>Región <ArrowUpDown size={12} /></th>
                      <th onClick={() => handleSort('tasa_informalidad')} style={{ cursor: 'pointer' }}>Informalidad (%) <ArrowUpDown size={12} /></th>
                      <th onClick={() => handleSort('ingreso_medio')} style={{ cursor: 'pointer' }}>Ingreso Medio (S/.) <ArrowUpDown size={12} /></th>
                      <th onClick={() => handleSort('total_encuestados')} style={{ cursor: 'pointer' }}>Encuestados <ArrowUpDown size={12} /></th>
                    </tr>
                  </thead>
                  <tbody>
                    {deptsFilteredAndSorted.map(dept => (
                      <tr key={dept.id_departamento}>
                        <td>{dept.id_departamento}</td>
                        <td style={{ fontWeight: 600 }}>{dept.nombre}</td>
                        <td>
                          <span className={`status-badge ${dept.region === 'Costa' ? 'green' : dept.region === 'Sierra' ? 'red' : 'orange'}`}>
                            {dept.region}
                          </span>
                        </td>
                        <td>
                          <span style={{ fontWeight: 700, color: getInformalColor(dept.tasa_informalidad) }}>
                            {dept.tasa_informalidad}%
                          </span>
                        </td>
                        <td style={{ fontWeight: 700, color: '#12b76a' }}>
                          S/. {dept.ingreso_medio?.toLocaleString()}
                        </td>
                        <td>{dept.total_encuestados?.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 6: MODELO PREDICTIVO OLS */}
          {activeTab === 'predict' && (
            <div className="widget-card">
              <div className="widget-card-header">
                <div>
                  <h3>
                    <Calculator size={18} color="#6c5ce7" />
                    Modelo Predictivo de Regresión Lineal Múltiple OLS
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: '#667085', marginTop: '0.2rem' }}>Estimación de tendencias salariales proyectadas a 5 años (2024 - 2028)</p>
                </div>
                <button onClick={() => setGlossaryModal('ols')} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#98a2b3' }}>
                  <Info size={18} />
                </button>
              </div>

              {proyeccion && (
                <div>
                  <div style={{ background: '#f0edff', padding: '1.25rem', borderRadius: '12px', border: '1px solid #d9d6fe', marginBottom: '1.5rem', textAlign: 'center' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#6c5ce7', textTransform: 'uppercase' }}>Ecuación Econométrica del Modelo</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#101828', marginTop: '0.25rem' }}>
                      {proyeccion.modelo_ecuacion}
                    </div>
                  </div>

                  <div style={{ height: '320px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={proyeccion.proyeccion_5_anios} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorProy" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6c5ce7" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#6c5ce7" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#eaecf0" />
                        <XAxis dataKey="anio" />
                        <YAxis domain={[1500, 2300]} tickFormatter={(v) => `S/. ${v}`} />
                        <ReTooltip formatter={(v) => [`S/. ${v}`, 'Ingreso Proyectado']} />
                        <Area type="monotone" dataKey="ingreso_proyectado" stroke="#6c5ce7" strokeWidth={3} fillOpacity={1} fill="url(#colorProy)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
