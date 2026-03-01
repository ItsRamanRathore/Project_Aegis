import { useState, useEffect, useRef, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import 'leaflet/dist/leaflet.css';

// ─── CONFIG ───────────────────────────────────────────────────────────────────
const EDGE_NODES = [
  { id: "Node-01", name: "Connaught Place (Primary)", lat: 28.6304, lng: 77.2177 },
  { id: "Node-02", name: "India Gate (Backup)", lat: 28.6129, lng: 77.2295 }
];

// ─── BOOT SCREEN ──────────────────────────────────────────────────────────────
const BootScreen = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [lines, setLines] = useState([]);
  const bootLines = [
    "Initializing Project AEGIS kernel...",
    "Loading AMD XDNA NPU drivers...",
    "Mounting encrypted file vaults...",
    "Starting watchdog observers...",
    "Connecting to Edge Nodes...",
    "Arming honeypot traps...",
    "System LOCKED. Shield ACTIVE.",
  ];

  useEffect(() => {
    let lineIdx = 0;
    const lineTimer = setInterval(() => {
      if (lineIdx < bootLines.length) {
        setLines(prev => [...prev, bootLines[lineIdx]]);
        setProgress(Math.round(((lineIdx + 1) / bootLines.length) * 100));
        lineIdx++;
      } else {
        clearInterval(lineTimer);
        setTimeout(onComplete, 500);
      }
    }, 250);
    return () => clearInterval(lineTimer);
  }, []);

  return (
    <div className="fixed inset-0 bg-black z-[9999] flex flex-col items-center justify-center font-mono">
      <div className="w-full max-w-2xl px-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-2">
            <div className="w-10 h-10 border-2 border-green-500 rounded flex items-center justify-center">
              <span className="text-green-500 text-xl font-bold">Λ</span>
            </div>
            <h1 className="text-4xl font-black tracking-[0.2em] text-white">
              AEGIS<span className="text-green-500">.</span>
            </h1>
          </div>
          <p className="text-gray-600 text-xs tracking-widest uppercase">Advanced Edge Guard & Intelligence System</p>
        </div>

        {/* Terminal lines */}
        <div className="border border-gray-800 rounded-lg bg-gray-950 p-4 mb-4 h-48 overflow-hidden">
          {lines.map((line, i) => (
            <div key={i} className="flex items-start gap-2 text-xs mb-1.5">
              <span className="text-green-500 shrink-0">[OK]</span>
              <span className="text-gray-300">{line}</span>
            </div>
          ))}
          <span className="text-green-500 animate-pulse text-xs">█</span>
        </div>

        {/* Progress bar */}
        <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-600 to-green-400 transition-all duration-300 rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-[10px] text-gray-600">SYSTEM BOOT</span>
          <span className="text-[10px] text-green-500 font-bold">{progress}%</span>
        </div>
      </div>
    </div>
  );
};

// ─── PASSWORD MODAL ───────────────────────────────────────────────────────────
const AdminModal = ({ onClose, onSuccess }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [shake, setShake] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('http://127.0.0.1:8000/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });
      if (res.ok) {
        const data = await res.json();
        onSuccess(data.token);
      } else {
        setError('INVALID CREDENTIALS — ACCESS DENIED');
        setShake(true);
        setTimeout(() => setShake(false), 600);
      }
    } catch (e) {
      setError('CANNOT REACH AEGIS BACKEND');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleLogin();
    if (e.key === 'Escape') onClose();
  };

  return (
    <div className="fixed inset-0 z-[1000] bg-black/80 backdrop-blur-sm flex items-center justify-center" onClick={onClose}>
      <div
        className={`relative bg-gray-950 border border-green-800/60 rounded-2xl p-8 w-full max-w-md shadow-2xl shadow-green-900/20 ${shake ? 'animate-shake' : ''}`}
        onClick={e => e.stopPropagation()}
      >
        {/* Glow */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-green-900/10 to-transparent pointer-events-none" />

        {/* Icon */}
        <div className="flex flex-col items-center mb-6">
          <div className="w-16 h-16 rounded-full border-2 border-green-600/50 flex items-center justify-center mb-3 bg-green-900/20">
            <span className="text-3xl">🛡️</span>
          </div>
          <h2 className="text-xl font-black text-white tracking-wider">ADMIN UNLOCK</h2>
          <p className="text-xs text-gray-500 mt-1 tracking-widest">AEGIS PROTECTED SYSTEM</p>
        </div>

        {/* Warning banner */}
        <div className="bg-yellow-900/20 border border-yellow-800/40 rounded-lg p-2 mb-5 text-center">
          <p className="text-yellow-400 text-[10px] font-bold tracking-widest">⚠ AUTHORIZED PERSONNEL ONLY</p>
        </div>

        {/* Password input */}
        <div className="mb-4">
          <label className="text-[10px] text-gray-500 uppercase tracking-widest block mb-2">SECURITY PASSPHRASE</label>
          <input
            autoFocus
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter admin password..."
            className="w-full bg-black border border-gray-700 text-green-400 rounded-lg px-4 py-3 font-mono text-sm focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/30 placeholder:text-gray-700 transition-all"
          />
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-2 mb-4">
            <p className="text-red-400 text-[10px] font-bold text-center tracking-wider animate-pulse">{error}</p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-lg border border-gray-700 text-gray-400 text-xs font-bold tracking-widest hover:border-gray-500 hover:text-gray-300 transition-all"
          >
            CANCEL
          </button>
          <button
            onClick={handleLogin}
            disabled={loading || !password}
            className="flex-1 py-2.5 rounded-lg bg-green-700 hover:bg-green-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-black tracking-widest transition-all shadow-lg shadow-green-900/30"
          >
            {loading ? '...' : 'AUTHENTICATE'}
          </button>
        </div>
      </div>
    </div>
  );
};

// ─── THREAT CARD ──────────────────────────────────────────────────────────────
const ThreatCard = ({ alert }) => {
  const isUnauthorized = alert.action === 'UNAUTHORIZED ACCESS';
  const isNetBan = alert.action === 'NETWORK BAN';
  const isTcpHarden = alert.action === 'TCP HARDENING';
  const isApiRateLimit = alert.action === 'API RATE LIMIT';
  const isApiGlobalThrottle = alert.action === 'API GLOBAL THROTTLE';
  const isMalware = alert.classification === 'MALWARE_PAYLOAD' || (alert.action && alert.action.includes('PAYLOAD'));

  const confidenceMatch = alert.classification?.match(/(\d+\.?\d*)%/);
  const confidence = confidenceMatch ? parseFloat(confidenceMatch[1]) : 100;

  let borderColor = 'border-red-500';
  let labelColor = 'text-red-400';
  let dotBg = 'bg-red-500';
  let tagColor = 'text-purple-300 border-purple-800/50 bg-purple-900/10';
  let barColor = 'bg-purple-500';

  if (isUnauthorized) {
    borderColor = 'border-orange-500'; labelColor = 'text-orange-400'; dotBg = 'bg-orange-500';
    tagColor = 'text-orange-300 border-orange-800/50 bg-orange-900/10'; barColor = 'bg-orange-500';
  } else if (isNetBan) {
    borderColor = 'border-cyan-500'; labelColor = 'text-cyan-400'; dotBg = 'bg-cyan-500';
    tagColor = 'text-cyan-300 border-cyan-800/50 bg-cyan-900/10'; barColor = 'bg-cyan-500';
  } else if (isTcpHarden) {
    borderColor = 'border-pink-500'; labelColor = 'text-pink-400'; dotBg = 'bg-pink-500';
    tagColor = 'text-pink-300 border-pink-800/50 bg-pink-900/10'; barColor = 'bg-pink-500';
  } else if (isApiRateLimit) {
    borderColor = 'border-yellow-500'; labelColor = 'text-yellow-400'; dotBg = 'bg-yellow-500';
    tagColor = 'text-yellow-300 border-yellow-800/50 bg-yellow-900/10'; barColor = 'bg-yellow-500';
  } else if (isApiGlobalThrottle) {
    borderColor = 'border-fuchsia-500'; labelColor = 'text-fuchsia-400'; dotBg = 'bg-fuchsia-500';
    tagColor = 'text-fuchsia-300 border-fuchsia-800/50 bg-fuchsia-900/10'; barColor = 'bg-fuchsia-500';
  } else if (isMalware) {
    borderColor = 'border-purple-500'; labelColor = 'text-purple-400'; dotBg = 'bg-purple-500';
    tagColor = 'text-purple-300 border-purple-800/50 bg-purple-900/10'; barColor = 'bg-purple-500';
  }

  return (
    <div className={`group relative mb-3 p-3 bg-[#020302] border border-gray-800/80 rounded-sm shadow-[inset_0_0_20px_rgba(0,0,0,1)] hover:border-gray-600 transition-all duration-300 overflow-hidden`}>
      {/* Side Accent Line */}
      <div className={`absolute top-0 left-0 w-[3px] h-full ${dotBg} opacity-80`} />

      {/* Animated Targeting Reticle shown on hover */}
      <div className="absolute top-3 right-3 w-8 h-8 rounded-full border border-gray-700/50 opacity-0 group-hover:opacity-50 transition-opacity flex items-center justify-center animate-spin pointer-events-none">
        <div className="w-[1px] h-full bg-gray-700/50 absolute" />
        <div className="h-[1px] w-full bg-gray-700/50 absolute" />
      </div>

      <div className="absolute inset-0 bg-gradient-to-r from-red-900/0 via-red-900/5 to-red-900/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 pointer-events-none rounded-r" />

      <div className="flex justify-between items-start mb-2 border-b border-gray-800/80 pb-2 pl-2">
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center w-3 h-3">
            <span className={`absolute w-full h-full rounded-sm ${dotBg} opacity-30 animate-ping`} />
            <span className={`relative w-1.5 h-1.5 bg-white shadow-[0_0_5px_currentColor] ${labelColor} rounded-full`} />
          </div>
          <span className={`font-black text-[10px] tracking-[0.2em] uppercase ${labelColor} drop-shadow-md`}>
            {(isUnauthorized || isNetBan || isTcpHarden || isApiRateLimit || isApiGlobalThrottle || isMalware) && '⚠ '}{alert.action}
          </span>
        </div>
        <span className="text-[9px] text-green-500 font-mono shrink-0 ml-2 pt-0.5">{alert.timestamp}</span>
      </div>

      <div className="grid grid-cols-2 gap-x-4 text-[10px] font-mono mb-3 pl-2 relative z-10">
        <div className="bg-white/[0.02] p-1.5 rounded border border-white/[0.02]">
          <span className="text-gray-600 block uppercase text-[8px] tracking-widest mb-0.5">Target</span>
          <span className="text-gray-300 truncate block font-bold">{(alert.target || '').substring(0, 22)}</span>
        </div>
        <div className="bg-white/[0.02] p-1.5 rounded border border-white/[0.02]">
          <span className="text-gray-600 block uppercase text-[8px] tracking-widest mb-0.5">Origin Node</span>
          <span className="text-orange-400/80 tracking-wider block truncate font-bold">{(alert.node || '').replace('Node-01: ', '')}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pl-2">
        <span className={`text-[8px] font-black tracking-widest uppercase px-2 py-1 rounded-sm border ${tagColor} shadow-[0_0_10px_currentColor] opacity-90`}>
          {alert.status || 'LOGGED'}
        </span>
        <div className="flex items-center gap-2">
          <div className="w-16 h-1.5 bg-gray-900 border border-gray-800 rounded-full overflow-hidden relative">
            {/* Segmentation markers */}
            <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent_2px,rgba(0,0,0,0.8)_2px)] bg-[length:4px_100%] z-10" />
            <div className={`h-full ${barColor} shadow-[0_0_5px_currentColor] transition-all duration-700`} style={{ width: `${confidence}%` }} />
          </div>
          <span className={`text-[10px] font-black ${labelColor}`}>{confidence}%</span>
        </div>
      </div>
    </div>
  );
};

// ─── AI ANALYST PANEL ─────────────────────────────────────────────────────────
const AIAnalystPanel = ({ report }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [mockProgress, setMockProgress] = useState(0);

  useEffect(() => {
    if (!report) return;
    setMockProgress(0);
    const textTimer = setInterval(() => {
      setDisplayedText(current => {
        if (current.length >= report.length) { clearInterval(textTimer); return current; }
        return report.slice(0, current.length + 1);
      });
    }, 18);
    const progTimer = setInterval(() => {
      setMockProgress(p => p >= 100 ? 100 : p + 5);
    }, 50);
    return () => { clearInterval(textTimer); clearInterval(progTimer); };
  }, [report]);

  return (
    <div className="w-full bg-[#050806] border border-green-900/40 p-3 rounded-sm mb-3 font-mono text-xs shadow-[inset_0_0_30px_rgba(0,0,0,1)] relative overflow-hidden h-32 shrink-0 group hover:border-green-700/50 transition-colors flex flex-col">
      <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-green-500/60 to-transparent animate-scan" />
      <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.5)_50%)] bg-[length:100%_4px] pointer-events-none opacity-40 z-0" />

      {/* Header */}
      <div className="relative flex items-center justify-between mb-2 pb-1 border-b border-green-900/50 z-10 shrink-0">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-sm animate-pulse shadow-[0_0_8px_#10b981]" />
          <span className="text-green-500/90 font-black tracking-[0.25em] text-[10px] drop-shadow-md">AEGIS OVERWATCH AI</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[8px] text-green-600 uppercase tracking-widest">Neural Link Active</span>
          <div className="flex gap-1">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="w-1.5 h-1.5 bg-green-500/80 rounded-sm" style={{ animation: `pulse 1.5s infinite ${i * 0.2}s` }} />
            ))}
          </div>
        </div>
      </div>

      {/* Body Layout */}
      <div className="relative flex-1 flex gap-4 overflow-hidden z-10">
        {/* Left: Text Stream */}
        <div className="flex-1 relative text-green-400/90 leading-relaxed whitespace-pre-wrap text-[10px] border-l-2 border-green-500/30 pl-2 overflow-y-auto pr-2 custom-scrollbar">
          {displayedText}
          <span className="animate-pulse text-green-400 shadow-[0_0_8px_#4ade80] ml-1">█</span>
        </div>

        {/* Right: Mock Processing Details */}
        <div className="w-48 shrink-0 flex flex-col gap-2 border-l border-green-900/30 pl-4 py-1">
          <div>
            <div className="text-[7px] text-gray-500 uppercase tracking-widest mb-1">Pattern Analysis</div>
            <div className="w-full h-1.5 bg-gray-900 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-500 shadow-[0_0_5px_#06b6d4] transition-all duration-300" style={{ width: `${mockProgress}%` }} />
            </div>
          </div>
          <div className="text-[8px] text-green-600/60 break-all leading-tight">
            HASH: {Math.random().toString(36).substring(2, 10).toUpperCase()}-{Math.random().toString(36).substring(2, 10).toUpperCase()}
            <br />
            SIG: {report ? 'ANALYZED' : 'AWAITING'}
          </div>
          {report && (
            <div className="mt-auto flex justify-end">
              <span className="border border-green-500/50 text-green-400 px-2 py-0.5 text-[8px] tracking-widest rounded bg-green-900/20">CONFIRMED</span>
            </div>
          )}
        </div>
      </div>

      <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-green-500/50 pointer-events-none z-20" />
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-green-500/50 pointer-events-none z-20" />
    </div>
  );
};

// ─── LIVE CHART ───────────────────────────────────────────────────────────────
const colorMap = { blue: '#3b82f6', green: '#10b981', purple: '#a855f7', orange: '#f97316' };
const LiveChart = ({ data, dataKey, color, label, value }) => {
  const hex = colorMap[color] || '#10b981';
  const isHigh = value > 70;
  return (
    <div className="flex flex-col h-full bg-[#030504] border border-white/[0.04] rounded-sm relative overflow-hidden group shadow-[inset_0_0_20px_rgba(0,0,0,1)] hover:border-white/[0.1] transition-colors">
      {/* Target Corners */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-gray-600/50 z-20 pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-gray-600/50 z-20 pointer-events-none" />

      <div className="flex justify-between items-end px-3 py-1.5 z-10 bg-gradient-to-b from-[#030504] to-transparent">
        <span className="text-[8px] font-black tracking-widest text-gray-500 uppercase">{label}</span>
        <span className="text-sm font-mono font-black drop-shadow-[0_0_8px_currentColor]" style={{ color: isHigh ? '#ef4444' : hex }}>{value}%</span>
      </div>
      <div className="absolute inset-0 opacity-70">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isHigh ? '#ef4444' : hex} stopOpacity={0.6} />
                <stop offset="95%" stopColor="#000" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey={dataKey} stroke={isHigh ? '#ef4444' : hex} strokeWidth={1.5} fill={`url(#grad-${dataKey})`} isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// ─── TELEMETRY BAR ────────────────────────────────────────────────────────────
const TelemetryPanel = ({ history, current }) => (
  <div className="grid grid-cols-3 gap-3 mb-4 h-20 shrink-0">
    <LiveChart data={history} dataKey="cpu" color="blue" label="Ryzen CPU" value={current.cpu} />
    <LiveChart data={history} dataKey="ram" color="green" label="RAM" value={current.ram} />
    <LiveChart data={history} dataKey="npu" color="purple" label="XDNA NPU" value={current.npu} />
  </div>
);

// ─── MAP ──────────────────────────────────────────────────────────────────────
const ThreatMap = ({ threatenedNode }) => (
  <div className="h-full w-full rounded-sm overflow-hidden border border-green-900/40 relative bg-[#020202] shadow-[inset_0_0_40px_rgba(0,0,0,1)]">
    {/* Grid overlay */}
    <div className="absolute inset-0 pointer-events-none z-[400] bg-[linear-gradient(rgba(16,185,129,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.05)_1px,transparent_1px)] bg-[length:30px_30px]" />

    {/* Animated Radar Sweep */}
    <div className="absolute top-1/2 left-1/2 w-[800px] h-[800px] -translate-x-1/2 -translate-y-1/2 pointer-events-none z-[450] bg-[conic-gradient(from_0deg,transparent_0deg,rgba(16,185,129,0.15)_90deg,transparent_120deg)] animate-radar rounded-full mix-blend-screen" />

    {/* Center Map Crosshair */}
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full border border-green-500/30 z-[460] pointer-events-none flex items-center justify-center">
      <div className="w-1.5 h-1.5 bg-green-500/50 rounded-full animate-pulse" />
      <div className="w-[1px] h-[1000px] bg-green-500/20 absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2" />
      <div className="h-[1px] w-[1000px] bg-green-500/20 absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2" />
      <div className="absolute w-[300px] h-[300px] rounded-full border border-green-500/10" />
      <div className="absolute w-[600px] h-[600px] rounded-full border border-green-500/5" />
    </div>

    <MapContainer center={[28.62, 77.22]} zoom={13} scrollWheelZoom={false} style={{ height: "100%", width: "100%", background: "#020202" }}>
      <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
      {EDGE_NODES.map(node => {
        const isAttacked = threatenedNode && threatenedNode.includes(node.id.split("-")[1]);
        return (
          <CircleMarker
            key={node.id}
            center={[node.lat, node.lng]}
            pathOptions={{
              color: isAttacked ? '#ef4444' : '#10b981',
              fillColor: isAttacked ? '#ef4444' : '#10b981',
              fillOpacity: isAttacked ? 0.9 : 0.6,
              weight: isAttacked ? 3 : 1
            }}
            radius={isAttacked ? 20 : 6}
          >
            <Popup className="font-mono">{node.name}</Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>

    {/* Frame corners */}
    <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-green-500/50 z-[500] pointer-events-none" />
    <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-green-500/50 z-[500] pointer-events-none" />
    <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-green-500/50 z-[500] pointer-events-none" />
    <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-green-500/50 z-[500] pointer-events-none" />
  </div>
);

// ─── SYSTEM STATUS PANEL ──────────────────────────────────────────────────────
const SystemStatusPanel = ({ locked, maintenanceMode, authenticated, alertCount, edgeShieldActive, edgeShieldEnabled, edrActive }) => {
  const items = [
    { label: 'Core Integrity', value: 'SECURE', color: 'text-green-400', dot: 'bg-green-500' },
    { label: 'Edge Shield', value: edgeShieldActive ? 'ACTIVE 🛡️' : 'OFFLINE', color: edgeShieldActive ? 'text-cyan-400' : 'text-gray-500', dot: edgeShieldActive ? 'bg-cyan-500 shadow-[0_0_5px_#06b6d4]' : 'bg-gray-700' },
    { label: 'Shield Logic', value: edgeShieldEnabled ? 'ENABLED' : 'DISABLED', color: edgeShieldEnabled ? 'text-green-400' : 'text-gray-500', dot: edgeShieldEnabled ? 'bg-green-500 shadow-[0_0_5px_#10b981]' : 'bg-gray-700' },
    { label: 'EDR Agent', value: edrActive ? 'ONLINE 👁️' : 'OFFLINE', color: edrActive ? 'text-purple-400' : 'text-gray-500', dot: edrActive ? 'bg-purple-500 shadow-[0_0_5px_#a855f7]' : 'bg-gray-700' },
    { label: 'File Protection', value: locked ? 'LOCKED 🔒' : 'UNLOCKED 🔓', color: locked ? 'text-green-400' : 'text-yellow-400', dot: locked ? 'bg-green-500' : 'bg-yellow-500 animate-pulse shadow-[0_0_5px_#eab308]' },
    { label: 'Admin Session', value: authenticated ? 'AUTHED' : 'LOCKED', color: authenticated ? 'text-blue-400' : 'text-gray-500', dot: authenticated ? 'bg-blue-500 shadow-[0_0_5px_#3b82f6]' : 'bg-gray-700' },
    { label: 'Threats Blocked', value: alertCount, color: 'text-red-400', dot: 'bg-red-500 shadow-[0_0_5px_#ef4444]' },
  ];

  return (
    <div className="bg-[#0f1512] border border-green-900/30 p-4 shrink-0 relative overflow-hidden group shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/5 blur-3xl rounded-full" />

      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-green-900/50">
        <div className="w-2 h-2 bg-green-500 rounded-sm" />
        <span className="text-[10px] font-black tracking-[0.2em] text-green-500/70 uppercase">Subsystem Diagnostics</span>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-4">
        {items.map(({ label, value, color, dot }) => (
          <div key={label} className="flex flex-col justify-center p-2 border border-white/[0.03] bg-white/[0.01] rounded hover:bg-white/[0.03] transition-colors">
            <div className="flex items-center gap-1.5 mb-1 text-gray-400">
              <span className={`w-1.5 h-1.5 rounded-full ${dot} shrink-0`} />
              <span className="text-[7px] uppercase tracking-widest">{label}</span>
            </div>
            <span className={`text-[10px] font-black tracking-wider pl-3 ${color} drop-shadow-md`}>{value}</span>
          </div>
        ))}
      </div>

      <div className="pt-3 border-t border-green-900/40">
        <div className="text-[8px] text-gray-500 uppercase tracking-widest mb-2 font-black">Active Features</div>
        <div className="flex flex-wrap gap-2 text-[9px] font-mono text-green-400/80">
          <span className="px-2 py-1 bg-green-900/20 border border-green-800/50 rounded-sm">HTTP Rate Limiter</span>
          <span className="px-2 py-1 bg-cyan-900/20 border border-cyan-800/50 rounded-sm text-cyan-400/80">DDoS Edge Shield</span>
          <span className="px-2 py-1 bg-purple-900/20 border border-purple-800/50 rounded-sm text-purple-400/80">Memory Scanning EDR</span>
          <span className="px-2 py-1 bg-yellow-900/20 border border-yellow-800/50 rounded-sm text-yellow-400/80">HoneyPot Engine</span>
        </div>
      </div>
    </div>
  );
};

// ─── NAVIGATION ───────────────────────────────────────────────────────────────
const TopNav = () => {
  const location = useLocation();
  const links = [
    { path: '/', label: 'OVERVIEW' },
    { path: '/network', label: 'NETWORK SHIELD' },
    { path: '/endpoint', label: 'ENDPOINT EDR' }
  ];
  return (
    <div className="flex gap-4 ml-8 items-center border-l border-green-900/50 pl-8">
      {links.map(l => {
        const active = location.pathname === l.path;
        return (
          <Link key={l.path} to={l.path} className={`text-[10px] font-black tracking-widest px-4 py-2 border rounded-sm transition-all duration-300 ${active ? 'border-green-500 text-green-400 bg-green-500/10 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'border-transparent text-gray-500 hover:text-green-500 hover:border-green-900/50 hover:bg-green-900/10'}`}>
            {l.label}
          </Link>
        )
      })}
    </div>
  );
};

// ─── VIEWS ────────────────────────────────────────────────────────────────────
const OverviewView = ({ threatenedNode, isLocked, maintenanceMode, authenticated, alerts, edgeShieldActive, edgeShieldEnabled, edrActive, latestReport }) => (
  <div className="flex-1 grid grid-cols-12 gap-4 min-h-0 px-4 pb-4">
    <div className="col-span-4 flex flex-col h-full gap-3">
      <div className="flex-1 border border-green-900/30 rounded-sm bg-[#050806] p-1 relative flex flex-col overflow-hidden shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
        <div className="absolute top-2 left-2 z-[400] bg-[#000]/80 border border-green-900/50 px-2 py-0.5 text-[9px] text-green-500/70 rounded-xs tracking-[0.2em] shadow-[0_0_10px_rgba(16,185,129,0.1)]">
          LIVE GRID • DEPLOYMENT ZONE
        </div>
        <div className="flex-1 relative rounded overflow-hidden mt-1">
          <ThreatMap threatenedNode={threatenedNode} />
        </div>
      </div>
      <SystemStatusPanel
        locked={isLocked}
        maintenanceMode={maintenanceMode}
        authenticated={authenticated}
        alertCount={alerts.length}
        edgeShieldActive={edgeShieldActive}
        edgeShieldEnabled={edgeShieldEnabled}
        edrActive={edrActive}
      />
    </div>
    <div className="col-span-8 flex flex-col h-full min-h-0">
      <AIAnalystPanel key={latestReport} report={latestReport} />
      <div className="flex-1 flex flex-col bg-[#020503] border border-green-900/40 rounded-sm z-10 shadow-[inset_0_0_40px_rgba(0,0,0,1)] overflow-hidden">
        <div className="flex justify-between items-center p-3 border-b border-green-900/50 bg-[#000502]/80">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-sm bg-red-500 animate-pulse shadow-[0_0_5px_#ef4444]" />
            <h2 className="text-[10px] font-black tracking-[0.2em] text-white uppercase drop-shadow-md">THREAT VECTOR FEED</h2>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-3 scrollbar-thin relative">
          <div className="absolute inset-x-0 top-0 h-8 bg-gradient-to-b from-[#020503] to-transparent z-10 pointer-events-none" />
          {alerts.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-green-500/40 gap-3">
              <span className="text-3xl drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]">🛡️</span>
              <span className="text-[10px] tracking-[0.3em] font-black uppercase text-center border border-green-900/30 p-2 bg-[#000502]/50">Perimeter Secure<br /><span className="text-[8px] text-green-600/50">Awaiting Telemetry</span></span>
            </div>
          ) : (
            <div className="space-y-1">
              {alerts.map((alert, i) => <ThreatCard key={i} alert={alert} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  </div>
);

const NetworkView = ({ alerts, isLocked, maintenanceMode, authenticated, edgeShieldActive, edgeShieldEnabled }) => {
  const networkAlerts = alerts.filter(a => ['NETWORK BAN', 'TCP HARDENING', 'API RATE LIMIT', 'API GLOBAL THROTTLE'].includes(a.action));
  return (
    <div className="flex-1 grid grid-cols-12 gap-4 min-h-0 px-4 pb-4">
      <div className="col-span-4 flex flex-col h-full gap-3">
        <SystemStatusPanel locked={isLocked} maintenanceMode={maintenanceMode} authenticated={authenticated} alertCount={networkAlerts.length} edgeShieldActive={edgeShieldActive} edgeShieldEnabled={edgeShieldEnabled} />
      </div>
      <div className="col-span-8 flex flex-col h-full min-h-0 bg-[#020503] border border-cyan-900/40 rounded-sm shadow-[inset_0_0_40px_rgba(0,0,0,1)]">
        <div className="p-3 border-b border-cyan-900/50 bg-[#000502]/80">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-sm bg-cyan-500 animate-pulse shadow-[0_0_5px_#06b6d4]" />
            <h2 className="text-[10px] font-black tracking-[0.2em] text-cyan-400 uppercase drop-shadow-md">NETWORK INCIDENTS</h2>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-3 scrollbar-thin">
          {networkAlerts.length === 0 ? <div className="text-cyan-500/40 text-xs text-center mt-10 tracking-widest uppercase">No network anomalies detected.</div> : networkAlerts.map((a, i) => <ThreatCard key={i} alert={a} />)}
        </div>
      </div>
    </div>
  );
};

const EndpointView = ({ alerts, edrActive, latestReport }) => {
  const edrAlerts = alerts.filter(a => a.classification === 'MALWARE_PAYLOAD' || (a.action && a.action.includes('PAYLOAD')));
  return (
    <div className="flex-1 grid grid-cols-12 gap-4 min-h-0 px-4 pb-4">
      <div className="col-span-4 flex flex-col h-full gap-3">
        <div className="border border-purple-900/40 p-4 bg-[#0a0510] rounded-sm text-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-purple-500/5 to-transparent pointer-events-none" />
          <div className="text-purple-500 font-black tracking-widest text-lg mb-2">AMD RYZEN AI NPU</div>
          <div className="text-[10px] text-purple-400 mb-4 tracking-[0.2em]">BEHAVIORAL INFERENCE ENGINE</div>
          <div className={`text-xs px-3 py-1 inline-block rounded border font-black tracking-widest ${edrActive ? 'bg-purple-900/50 border-purple-500 text-purple-300 shadow-[0_0_10px_#a855f7]' : 'bg-gray-800 border-gray-600 text-gray-500'}`}>
            {edrActive ? 'ONLINE & SCANNING' : 'OFFLINE'}
          </div>
        </div>
      </div>
      <div className="col-span-8 flex flex-col h-full min-h-0 gap-3">
        <AIAnalystPanel report={latestReport} />
        <div className="flex-1 border border-purple-900/40 rounded-sm bg-[#0a0510] shadow-[inset_0_0_40px_rgba(0,0,0,1)] flex flex-col min-h-0">
          <div className="p-3 border-b border-purple-900/50 bg-[#000502]/80 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-sm bg-purple-500 animate-pulse shadow-[0_0_5px_#a855f7]" />
            <h2 className="text-[10px] font-black tracking-[0.2em] text-purple-400 uppercase drop-shadow-md">ENDPOINT THREATS (EDR_KILLS)</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-3 scrollbar-thin">
            {edrAlerts.length === 0 ? <div className="text-purple-500/40 text-xs text-center mt-6 tracking-widest uppercase">No endpoint payloads detected.</div> : edrAlerts.map((a, i) => <ThreatCard key={i} alert={a} />)}
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function App() {
  const [booting, setBooting] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const [status, setStatus] = useState('SHIELD ACTIVE');
  const [statusType, setStatusType] = useState('normal'); // 'normal' | 'threat' | 'unauthorized' | 'maintenance' | 'edr'
  const [threatenedNode, setThreatenedNode] = useState(null);
  const [latestReport, setLatestReport] = useState('System operational. All sentinels armed. Awaiting threat vectors...');
  const [telemetryHistory, setTelemetryHistory] = useState(Array(20).fill({ cpu: 0, ram: 0, npu: 0 }));
  const [currentTelemetry, setCurrentTelemetry] = useState({ cpu: 0, ram: 0, npu: 0 });

  // Admin auth state
  const [showModal, setShowModal] = useState(false);
  const [token, setToken] = useState(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [togglingMaintenance, setTogglingMaintenance] = useState(false);
  const [edgeShieldActive, setEdgeShieldActive] = useState(false);
  const [edgeShieldEnabled, setEdgeShieldEnabled] = useState(true);
  const [togglingShield, setTogglingShield] = useState(false);
  const [edrActive, setEdrActive] = useState(false);

  const wsAlertsRef = useRef(null);

  const handleLogin = useCallback((newToken) => {
    setToken(newToken);
    setAuthenticated(true);
    setShowModal(false);
  }, []);

  const handleLogout = useCallback(async () => {
    if (token) {
      try {
        await fetch('http://127.0.0.1:8000/api/admin/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (e) { }
    }
    setToken(null);
    setAuthenticated(false);
    setMaintenanceMode(false);
  }, [token]);

  const handleMaintenanceToggle = useCallback(async () => {
    if (!token) return;
    setTogglingMaintenance(true);
    const newState = !maintenanceMode;
    try {
      await fetch('http://127.0.0.1:8000/api/maintenance/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ enabled: newState }),
      });
      setMaintenanceMode(newState);
    } catch (e) { }
    setTogglingMaintenance(false);
  }, [token, maintenanceMode]);

  const handleEdgeShieldToggle = useCallback(async () => {
    if (!token) return;
    setTogglingShield(true);
    const newState = !edgeShieldEnabled;
    try {
      await fetch('http://127.0.0.1:8000/api/edge/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ enabled: newState }),
      });
      setEdgeShieldEnabled(newState);
    } catch (e) { }
    setTogglingShield(false);
  }, [token, edgeShieldEnabled]);

  // System state from websocket
  const handleSystemState = useCallback((data) => {
    if (data.maintenance_mode !== undefined) setMaintenanceMode(data.maintenance_mode);
    if (data.edge_shield_enabled !== undefined) setEdgeShieldEnabled(data.edge_shield_enabled);
  }, []);

  const handleNewAlert = useCallback((data) => {
    data.forensicId = Math.floor(Math.random() * 90000) + 10000;
    data.hash = Array(4).fill(0).map(() => Math.random().toString(36).substr(2, 4)).join('-').toUpperCase();

    setAlerts(prev => {
      if (data.id && prev.some(a => a.id === data.id)) return prev;
      if (!data.id && prev.some(a => a.timestamp === data.timestamp && a.action === data.action && a.node === data.node)) return prev;
      return [data, ...prev];
    });
    if (data.analysis) setLatestReport(data.analysis);

    if (data.action === 'UNAUTHORIZED ACCESS') {
      setStatus('⚠ UNAUTHORIZED ACCESS');
      setStatusType('unauthorized');
      setThreatenedNode(data.node);
    } else if (data.action === 'NETWORK BAN') {
      setStatus('🛡️ EDGE SHIELD: IP BANNED');
      setStatusType('netban');
      setThreatenedNode(data.node);
    } else if (data.action === 'TCP HARDENING') {
      setStatus('⚠️ DISTRIBUTED DDOS BLOCKED');
      setStatusType('tcpharden');
      setThreatenedNode(data.node);
    } else if (data.action === 'API RATE LIMIT') {
      setStatus('🛡️ RATE LIMIT ENFORCED');
      setStatusType('ratelimit');
      setThreatenedNode(data.node);
    } else if (data.action === 'API GLOBAL THROTTLE') {
      setStatus('⚠️ GLOBAL HTTP THROTTLE');
      setStatusType('throttle');
      setThreatenedNode(data.node);
    } else if (data.action && data.action.includes('PAYLOAD')) {
      setStatus('👁️ EDR PAYLOAD INTERCEPT');
      setStatusType('edr');
      setThreatenedNode(data.node);
    } else {
      setStatus('THREAT NEUTRALIZED');
      setStatusType('threat');
      setThreatenedNode(data.node);
    }
    setTimeout(() => { setStatus('SHIELD ACTIVE'); setStatusType('normal'); setThreatenedNode(null); }, 5000);
  }, []);

  useEffect(() => {
    // Poll system status for edge shield heartbeat
    const pollSystemStatus = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/system/status');
        const data = await res.json();
        setMaintenanceMode(data.maintenance_mode);
        setEdgeShieldActive(data.edge_shield_active);
        setEdrActive(data.edr_active);
        if (data.edge_shield_enabled !== undefined) setEdgeShieldEnabled(data.edge_shield_enabled);
      } catch (e) {
        setEdgeShieldActive(false);
        setEdrActive(false);
      }
    };

    pollSystemStatus();
    const statusInterval = setInterval(pollSystemStatus, 3000);

    fetch('http://127.0.0.1:8000/api/alerts-history')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setAlerts(prev => {
            const merged = [...prev];
            data.forEach(fetchedAlert => {
              const exists = merged.some(a =>
                (a.id && a.id === fetchedAlert.id) ||
                (a.timestamp === fetchedAlert.timestamp && a.action === fetchedAlert.action && a.node === fetchedAlert.node)
              );
              if (!exists) {
                merged.push({
                  ...fetchedAlert,
                  hash: fetchedAlert.hash || Array(4).fill(0).map(() => Math.random().toString(36).substr(2, 4)).join('-').toUpperCase()
                });
              }
            });
            // Try separating by ID mostly, fallback to keeping whatever order for no-IDs
            return merged.sort((a, b) => (b.id || 0) - (a.id || 0));
          });
        }
      }).catch(() => { });

    const wsAlerts = new WebSocket('ws://127.0.0.1:8000/ws/dashboard');
    wsAlertsRef.current = wsAlerts;
    wsAlerts.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'system_state') {
        handleSystemState(data);
      } else {
        handleNewAlert(data);
      }
    };

    const wsTelemetry = new WebSocket('ws://127.0.0.1:8000/ws/telemetry');
    wsTelemetry.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setCurrentTelemetry(data);
      setTelemetryHistory(prev => [...prev.slice(1), data]);
    };

    return () => {
      clearInterval(statusInterval);
      wsAlerts.close();
      wsTelemetry.close();
    };
  }, [handleSystemState, handleNewAlert]);

  // ── Status badge style ──
  const statusStyles = {
    normal: 'border-green-800/60 text-green-500 bg-green-900/20',
    threat: 'border-red-600 text-red-400 bg-red-900/20 animate-pulse',
    unauthorized: 'border-orange-500 text-orange-400 bg-orange-900/20 animate-pulse',
    maintenance: 'border-yellow-600 text-yellow-400 bg-yellow-900/20',
    netban: 'border-cyan-500 text-cyan-400 bg-cyan-900/20 animate-pulse',
    tcpharden: 'border-pink-500 text-pink-400 bg-pink-900/20 animate-pulse',
    ratelimit: 'border-yellow-500 text-yellow-400 bg-yellow-900/20 animate-pulse',
    throttle: 'border-fuchsia-500 text-fuchsia-400 bg-fuchsia-900/20 animate-pulse',
    edr: 'border-purple-500 text-purple-400 bg-purple-900/20 animate-pulse',
  };

  const statusClass = statusStyles[statusType] || statusStyles.normal;
  const isLocked = !maintenanceMode;

  if (booting) return <BootScreen onComplete={() => setBooting(false)} />;

  return (
    <Router>
      <div className={`h-screen w-screen flex flex-col font-sans transition-colors duration-500 overflow-hidden ${isLocked ? 'bg-[#0f1512] text-gray-300' : 'bg-[#151b18] text-gray-400'}`}>
        {/* Background patterns */}
        <div className={`absolute inset-0 z-0 pointer-events-none opacity-20 bg-[linear-gradient(rgba(16,185,129,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.1)_1px,transparent_1px)] bg-[length:40px_40px] animate-grid`} />

        {/* Scanline Effect across whole screen */}
        <div className="absolute inset-0 pointer-events-none z-[100] h-[10%] w-full bg-gradient-to-b from-transparent via-green-500/15 to-transparent animate-scan-line mix-blend-screen opacity-50" />

        {isLocked && <div className="absolute inset-0 bg-[#0f1512]/60 z-[40] pointer-events-none mix-blend-overlay transition-opacity duration-1000" />}

        {/* ── HEADER ── */}
        <header className="px-6 py-4 border-b border-green-900/40 bg-[#020503] shadow-[0_4px_30px_rgba(0,0,0,0.8)] z-[200] flex justify-between items-center relative shrink-0">
          <div className="absolute inset-0 bg-gradient-to-r from-green-500/5 to-transparent pointer-events-none" />

          <div className="flex items-center gap-4 relative">
            <div className="w-10 h-10 bg-[#000] border border-green-800 rounded-sm flex items-center justify-center relative overflow-hidden group shadow-[inset_0_0_15px_rgba(16,185,129,0.2)]">
              <div className="absolute inset-0 bg-green-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              <span className="text-green-500 text-lg font-black drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]">Λ</span>
            </div>
            <div>
              <h1 className="text-xl font-black tracking-[0.3em] text-green-500 drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">AEGIS</h1>
              <div className="text-[9px] font-mono tracking-[0.4em] text-green-500/60 uppercase">Advanced Threat Intelligence</div>
            </div>
            <TopNav />
          </div>

          {/* Right side controls */}
          <div className="flex items-center gap-4 relative">
            {/* Main Status Badge */}
            <div className={`px-4 py-2 border rounded-sm flex items-center gap-3 transition-colors ${statusClass} shadow-[0_0_10px_currentColor]`}>
              <span className="text-[10px] font-black tracking-widest uppercase">{status}</span>
              <div className={`w-2 h-2 rounded-sm ${statusClass.includes('green') ? 'bg-green-500' : 'bg-current'} shadow-[0_0_8px_currentColor]`} />
            </div>

            {/* Admin unlock / logout button */}
            {!authenticated ? (
              <button onClick={() => setShowModal(true)} className="px-4 py-2 bg-[#020403] border border-green-900/50 hover:border-green-500/50 rounded-sm text-xs font-black tracking-[0.2em] text-green-500/70 hover:text-green-400 transition-colors flex items-center gap-2 shadow-[inset_0_0_10px_rgba(16,185,129,0.1)]">
                🔓 ADMIN
              </button>
            ) : (
              <div className="flex items-center gap-3">
                <button
                  onClick={handleEdgeShieldToggle} disabled={togglingShield}
                  className={`px-4 py-2 border rounded-sm text-xs font-black tracking-[0.1em] transition-colors flex items-center gap-2 ${edgeShieldEnabled ? 'bg-cyan-900/30 border-cyan-700 text-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.2)]' : 'bg-gray-900/50 border-gray-700 text-gray-500 hover:text-cyan-600'}`}
                >
                  {togglingShield ? <span className="animate-spin w-3 h-3 block border-2 border-t-transparent rounded-full" /> : <span>🛡️</span>}
                  {edgeShieldEnabled ? 'SHIELD ON' : 'SHIELD OFF'}
                </button>
                <button
                  onClick={handleMaintenanceToggle} disabled={togglingMaintenance}
                  className={`px-4 py-2 border rounded-sm text-xs font-black tracking-[0.1em] transition-colors flex items-center gap-2 ${maintenanceMode ? 'bg-yellow-900/30 border-yellow-700 text-yellow-500 hover:bg-yellow-900/50 shadow-[0_0_10px_rgba(234,179,8,0.2)]' : 'bg-[#020403] border-green-900/50 text-green-500/60 hover:border-green-500/50 hover:text-green-400'}`}
                >
                  {togglingMaintenance ? <span className="animate-spin w-3 h-3 block border-2 border-t-transparent rounded-full" /> : <span>⚙️</span>}
                  {maintenanceMode ? 'DISABLE MAINT.' : 'MAINTENANCE'}
                </button>
                <button onClick={handleLogout} className="p-2 border border-red-900/50 text-red-500 hover:bg-red-900/20 hover:border-red-500/50 rounded-sm transition-colors shadow-[inset_0_0_10px_rgba(239,68,68,0.1)]">
                  ⏻
                </button>
              </div>
            )}
          </div>
        </header>

        {/* ── TELEMETRY BAR ── */}
        <div className="px-4 pt-4">
          <TelemetryPanel history={telemetryHistory} current={currentTelemetry} />
        </div>

        {/* ── MAIN CONTENT (ROUTED) ── */}
        <Routes>
          <Route path="/" element={<OverviewView threatenedNode={threatenedNode} isLocked={isLocked} maintenanceMode={maintenanceMode} authenticated={authenticated} alerts={alerts} edgeShieldActive={edgeShieldActive} edgeShieldEnabled={edgeShieldEnabled} edrActive={edrActive} latestReport={latestReport} />} />
          <Route path="/network" element={<NetworkView alerts={alerts} isLocked={isLocked} maintenanceMode={maintenanceMode} authenticated={authenticated} edgeShieldActive={edgeShieldActive} edgeShieldEnabled={edgeShieldEnabled} />} />
          <Route path="/endpoint" element={<EndpointView alerts={alerts} edrActive={edrActive} latestReport={latestReport} />} />
        </Routes>

        {/* ── ADMIN MODAL ── */}
        {showModal && <AdminModal onClose={() => setShowModal(false)} onSuccess={handleLogin} />}
      </div>
    </Router>
  );
}