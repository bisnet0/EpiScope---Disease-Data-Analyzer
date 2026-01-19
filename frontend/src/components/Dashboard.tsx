import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area,
} from "recharts";
import api from "../services/api";
import {
  Activity,
  Bug,
  Eye,
  Cpu,
  Trophy,
  ClipboardData,
  Filter,
  ArrowRepeat,
} from "react-bootstrap-icons";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];
const DARK_BG = "#1e1e1e";
const ACCENT_COLOR = "#646cff";

const selectStyle: React.CSSProperties = {
  background: "#333",
  color: "#fff",
  border: "1px solid #555",
  padding: "8px 12px",
  borderRadius: "6px",
  cursor: "pointer",
  outline: "none",
  fontSize: "0.9rem",
};

const StatCard = ({ title, value, icon, color, sub }: any) => (
  <div
    style={{
      background: "#1e1e1e",
      padding: "20px",
      borderRadius: "10px",
      borderLeft: `4px solid ${color}`,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      boxShadow: "0 4px 6px rgba(0,0,0,0.2)",
    }}
  >
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "start",
        marginBottom: "10px",
      }}
    >
      <span
        style={{
          color: "#aaa",
          fontSize: "0.85rem",
          fontWeight: "bold",
          textTransform: "uppercase",
        }}
      >
        {title}
      </span>
      <span style={{ color: color }}>{icon}</span>
    </div>
    <div style={{ fontSize: "1.8rem", fontWeight: "bold", color: "#fff" }}>
      {value}
    </div>
    {sub && (
      <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "5px" }}>
        {sub}
      </div>
    )}
  </div>
);

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const [periodFilter, setPeriodFilter] = useState("all");
  const [modelFilter, setModelFilter] = useState("all");

  useEffect(() => {
    fetchStats();
  }, [periodFilter, modelFilter]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await api.get("/dashboard/stats", {
        params: {
          period: periodFilter,
          model: modelFilter,
        },
      });
      setStats(response.data);
    } catch (error) {
      console.error("Erro carregando dashboard", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDateBR = (iso: string) => {
        if (!iso) return "--/--";
        
        const date = new Date(iso);
        if (isNaN(date.getTime())) return iso; 

        // --- CORREÇÃO DE FUSO ---
        // Se mostra 21h e era 18h, temos que tirar 3 horas
        date.setHours(date.getHours() - 3);

        const day = date.toLocaleString("pt-BR", { day: "2-digit" });
        const month = date.toLocaleString("pt-BR", { month: "2-digit" });
        
        // hour12: false garante formato 24h (18:51 e não 06:51 PM)
        const hour = date.toLocaleString("pt-BR", { hour: "2-digit", hour12: false });
        const minute = date.toLocaleString("pt-BR", { minute: "2-digit" });

        return `${day}/${month} — ${hour}h${minute}m`;
    };

  if (!stats && loading)
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
        Carregando Centro de Comando...
      </div>
    );
  if (!stats) return null;

  const { kpis, charts } = stats;

  const diagnosisData = [
    { name: "Arboviroses", value: kpis.arbovirus_count },
    { name: "Glaucoma", value: kpis.glaucoma_count },
  ];

  const learningCurveData = charts.learning_curve.map((item: any) => ({
    ...item,
    dateLabel: formatDateBR(item.date),
  }));

  return (
    <div className="container fade-in" style={{ paddingBottom: "50px" }}>
      {/* --- CABEÇALHO E BARRA DE FILTROS --- */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
          flexWrap: "wrap",
          gap: "15px",
        }}
      >
        <h2
          style={{
            margin: 0,
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <Activity color={ACCENT_COLOR} /> Analytics em Tempo Real
        </h2>

        <div
          style={{
            display: "flex",
            gap: "10px",
            background: "#252525",
            padding: "10px",
            borderRadius: "8px",
            border: "1px solid #333",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "5px",
              color: "#aaa",
              fontSize: "0.9rem",
              marginRight: "10px",
            }}
          >
            <Filter /> Filtros:
          </div>

          {/* Filtro de Período */}
          <select
            value={periodFilter}
            onChange={(e) => setPeriodFilter(e.target.value)}
            style={selectStyle}
          >
            <option value="all">📅 Todo o Período</option>
            <option value="24h">🕒 Últimas 24 Horas</option>
            <option value="7d">📅 Últimos 7 Dias</option>
            <option value="30d">📅 Últimos 30 Dias</option>
          </select>

          {/* Filtro de Modelo */}
          <select
            value={modelFilter}
            onChange={(e) => setModelFilter(e.target.value)}
            style={selectStyle}
          >
            <option value="all">🤖 Todos os Modelos</option>
            <option value="xgboost">🚀 XGBoost</option>
            <option value="random_forest">🌲 Random Forest</option>
            <option value="decision_tree">🌳 Decision Tree</option>
            <option value="glaucoma">🚀🌲Híbrido</option>
          </select>

          <button
            onClick={fetchStats}
            title="Atualizar Agora"
            style={{
              background: "transparent",
              border: "none",
              color: "#fff",
              cursor: "pointer",
              padding: "0 5px",
            }}
          >
            <ArrowRepeat size={20} className={loading ? "spin" : ""} />
          </button>
        </div>
      </div>

      {/* --- LINHA 1: KPIS (Cards) --- */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "20px",
          marginBottom: "30px",
        }}
      >
        <StatCard
          title="Diagnósticos (Filtrado)"
          value={kpis.total_diagnoses}
          icon={<ClipboardData size={24} />}
          color="#3498db"
        />
        <StatCard
          title="Melhor Acurácia (Neste Filtro)"
          value={`${kpis.best_ai_accuracy}%`}
          icon={<Trophy size={24} />}
          color="#f1c40f"
        />
        <StatCard
          title="Treinamentos Realizados"
          value={kpis.total_trainings}
          icon={<Cpu size={24} />}
          color="#9b59b6"
        />
        <StatCard
          title="Status Blockchain"
          value="Ativo"
          sub="Consenso Local"
          icon={
            <div
              style={{
                width: 10,
                height: 10,
                background: "#2ecc71",
                borderRadius: "50%",
              }}
            />
          }
          color="#2ecc71"
        />
      </div>

      {/* --- LINHA 2: GRÁFICOS PRINCIPAIS --- */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))",
          gap: "20px",
        }}
      >
        {/* 1. Curva de Aprendizado */}
        <div
          className="chart-card"
          style={{
            background: DARK_BG,
            padding: "20px",
            borderRadius: "10px",
            boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
          }}
        >
          <h4
            style={{
              marginBottom: "20px",
              borderBottom: "1px solid #333",
              paddingBottom: "10px",
            }}
          >
            📈 Evolução da Inteligência Artificial
          </h4>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={learningCurveData}>
                <defs>
                  <linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor={ACCENT_COLOR}
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor={ACCENT_COLOR}
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis
                  dataKey="dateLabel"
                  stroke="#666"
                  style={{ fontSize: "0.8rem" }}
                />
                <YAxis
                  domain={[50, 100]}
                  stroke="#666"
                  unit="%"
                  style={{ fontSize: "0.8rem" }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#252525",
                    border: "1px solid #444",
                    borderRadius: "5px",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="accuracy"
                  name="Acurácia"
                  stroke={ACCENT_COLOR}
                  fillOpacity={1}
                  fill="url(#colorAcc)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p
            style={{
              fontSize: "0.8rem",
              color: "#666",
              textAlign: "center",
              marginTop: "10px",
            }}
          >
            Mostrando os últimos treinos correspondentes aos filtros
            selecionados.
          </p>
        </div>

        {/* 2. Batalha de Algoritmos */}
        <div
          className="chart-card"
          style={{
            background: DARK_BG,
            padding: "20px",
            borderRadius: "10px",
            boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
          }}
        >
          <h4
            style={{
              marginBottom: "20px",
              borderBottom: "1px solid #333",
              paddingBottom: "10px",
            }}
          >
            ⚔️ Performance Média por Algoritmo
          </h4>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={charts.model_performance}
                layout="vertical"
                margin={{ left: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis type="number" domain={[0, 100]} stroke="#666" unit="%" />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={100}
                  stroke="#aaa"
                  fontSize={12}
                  tick={{ fill: "#eee" }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#252525",
                    border: "1px solid #444",
                    borderRadius: "5px",
                  }}
                  cursor={{ fill: "rgba(255,255,255,0.05)" }}
                />
                <Bar
                  dataKey="accuracy"
                  name="Acurácia Média"
                  fill="#82ca9d"
                  barSize={25}
                  radius={[0, 4, 4, 0]}
                >
                  {charts.model_performance.map((entry: any, index: number) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* --- LINHA 3: DISTRIBUIÇÃO --- */}
      <div
        style={{
          marginTop: "20px",
          display: "flex",
          gap: "20px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            flex: 1,
            background: DARK_BG,
            padding: "20px",
            borderRadius: "10px",
            minWidth: "300px",
          }}
        >
          <h4 style={{ textAlign: "center", marginBottom: "20px" }}>
            Distribuição de Patologias
          </h4>
          <div
            style={{
              height: 250,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={diagnosisData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  <Cell fill="#3498db" /> {/* Arbovirose */}
                  <Cell fill="#e91e63" /> {/* Glaucoma */}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#252525",
                    border: "1px solid #444",
                  }}
                />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* --- SEÇÃO GENÉTICA (Renderiza apenas se houver dados) --- */}
      {charts.ga_analysis &&
        charts.ga_analysis.mutation &&
        charts.ga_analysis.mutation.length > 0 && (
          <div
            style={{
              marginTop: "40px",
              borderTop: "1px solid #333",
              paddingTop: "20px",
            }}
          >
            <h3
              style={{
                marginBottom: "20px",
                display: "flex",
                alignItems: "center",
                gap: "10px",
              }}
            >
              🧬 Teoria Evolutiva: Análise de Hiperparâmetros
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: "20px",
              }}
            >
              {/* 1. MUTAÇÃO (Scatter) */}
              <div
                className="chart-card"
                style={{
                  background: DARK_BG,
                  padding: "20px",
                  borderRadius: "10px",
                }}
              >
                <h4
                  style={{
                    fontSize: "0.9rem",
                    color: "#aaa",
                    marginBottom: "15px",
                  }}
                >
                  ⚡ Taxa de Mutação vs Acurácia
                </h4>
                <div style={{ height: 200 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={charts.ga_analysis.mutation}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis
                        dataKey="x"
                        type="number"
                        domain={[0, "dataMax"]}
                        name="Mutação"
                        stroke="#666"
                        tickFormatter={(v) => `${v * 100}%`}
                      />
                      <YAxis domain={["auto", "auto"]} stroke="#666" hide />
                      <Tooltip
                        contentStyle={{ background: "#252525" }}
                        formatter={(val: number) => `${val}%`}
                        labelFormatter={(l) => `Mutação: ${l * 100}%`}
                      />
                      <Line
                        type="monotone"
                        dataKey="y"
                        stroke="#FF8042"
                        dot={{ r: 3 }}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <small style={{ color: "#666" }}>
                  Mostra o impacto da aleatoriedade na solução final.
                </small>
              </div>

              {/* 2. POPULAÇÃO (Barra) */}
              <div
                className="chart-card"
                style={{
                  background: DARK_BG,
                  padding: "20px",
                  borderRadius: "10px",
                }}
              >
                <h4
                  style={{
                    fontSize: "0.9rem",
                    color: "#aaa",
                    marginBottom: "15px",
                  }}
                >
                  👥 Tamanho da População
                </h4>
                <div style={{ height: 200 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={charts.ga_analysis.population}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="x" stroke="#666" name="População" />
                      <YAxis domain={[0, 100]} stroke="#666" hide />
                      <Tooltip
                        contentStyle={{ background: "#252525" }}
                        cursor={{ fill: "transparent" }}
                      />
                      <Bar
                        dataKey="y"
                        fill="#00C49F"
                        name="Acurácia"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <small style={{ color: "#666" }}>
                  Populações maiores garantem diversidade genética?
                </small>
              </div>

              {/* 3. CROSSOVER (Linha) */}
              <div
                className="chart-card"
                style={{
                  background: DARK_BG,
                  padding: "20px",
                  borderRadius: "10px",
                }}
              >
                <h4
                  style={{
                    fontSize: "0.9rem",
                    color: "#aaa",
                    marginBottom: "15px",
                  }}
                >
                  🧬 Taxa de Crossover (Recombinação)
                </h4>
                <div style={{ height: 200 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={charts.ga_analysis.crossover}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis
                        dataKey="x"
                        stroke="#666"
                        tickFormatter={(v) => `${v * 100}%`}
                      />
                      <YAxis domain={["auto", "auto"]} stroke="#666" hide />
                      <Tooltip
                        contentStyle={{ background: "#252525" }}
                        labelFormatter={(l) => `Crossover: ${l * 100}%`}
                      />
                      <Area
                        type="monotone"
                        dataKey="y"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <small style={{ color: "#666" }}>
                  Impacto de misturar genes de "pais" diferentes.
                </small>
              </div>

              {/* 4. GERAÇÕES (Area) */}
              <div
                className="chart-card"
                style={{
                  background: DARK_BG,
                  padding: "20px",
                  borderRadius: "10px",
                  
                }}
              >
                <h4
                  style={{
                    fontSize: "0.9rem",
                    color: "#aaa",
                    marginBottom: "15px",
                  }}
                >
                  ⏳ Gerações vs Convergência
                </h4>
                <div style={{ height: 200}}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={charts.ga_analysis.generations}>
                      <defs>
                        <linearGradient
                          id="colorGen"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor="#0088FE"
                            stopOpacity={0.3}
                          />
                          <stop
                            offset="95%"
                            stopColor="#0088FE"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="x" stroke="#666" />
                      <YAxis domain={["auto", "auto"]} stroke="#666" hide />
                      <Tooltip contentStyle={{ background: "#252525" }} />
                      <Area
                        type="monotone"
                        dataKey="y"
                        stroke="#0088FE"
                        fill="url(#colorGen)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                <small style={{ color: "#666" }}>
                  A inteligência para de crescer após X gerações?
                </small>
              </div>
            </div>
          </div>
        )}
    </div>
  );
};
