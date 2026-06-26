import React, { useEffect, useState, useRef } from 'react';
import { Camera, AlertTriangle, Shield, Volume2, VolumeX } from 'lucide-react';

const CameraGrid = ({ cameras, selectedCameraId, setSelectedCameraId }) => {
  const [streamData, setStreamData] = useState(null);
  const [wsStatus, setWsStatus] = useState('disconnected');
  const wsRef = useRef(null);
  const [muteAlarm, setMuteAlarm] = useState(true);
  const audioContextRef = useRef(null);

  // Play synthetic alarm sound on high risk if not muted
  const playAlarmSound = (frequency = 880, duration = 0.15) => {
    if (muteAlarm) return;
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      const ctx = audioContextRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(frequency, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime); // low volume
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {
      console.warn("Audio playback error:", e);
    }
  };

  const activeCamera = cameras.find(c => c.id === selectedCameraId) || cameras[0];

  useEffect(() => {
    if (!activeCamera) return;

    setWsStatus('connecting');
    setStreamData(null);

    // Close existing socket
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Connect to WebSocket stream
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/stream/${activeCamera.id}`;
    
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus('connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStreamData(data);
      if (data.risk_score >= 70.0) {
        playAlarmSound(980, 0.2);
      }
    };

    ws.onerror = (err) => {
      setWsStatus('error');
      console.error("WS stream error:", err);
    };

    ws.onclose = () => {
      setWsStatus('disconnected');
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [activeCamera, muteAlarm]);

  const riskScore = streamData?.risk_score || 0;
  const isHighRisk = riskScore >= 70.0;
  const alerts = streamData?.alerts || [];

  return (
    <div className="camera-section" style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
      {/* HUD Header */}
      <div className="hud-header glass-panel" style={{ padding: '12px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="live-indicator"></div>
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '1.1rem', letterSpacing: '0.5px' }}>
            FEED: {activeCamera?.name || "NO ACTIVE CAMERA"}
          </span>
          <span style={{ fontSize: '0.8rem', color: wsStatus === 'connected' ? 'var(--accent-green)' : 'var(--accent-red)', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
            {wsStatus.toUpperCase()}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button 
            onClick={() => setMuteAlarm(!muteAlarm)} 
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '6px', borderRadius: '6px', transition: 'var(--transition-smooth)' }}
            className="hud-button"
            title={muteAlarm ? "Unmute Alarm Sound" : "Mute Alarm Sound"}
          >
            {muteAlarm ? <VolumeX size={18} /> : <Volume2 size={18} style={{ color: 'var(--primary)' }} />}
          </button>
        </div>
      </div>

      {/* Main Viewscreen */}
      <div 
        className={`viewscreen glass-panel ${isHighRisk ? 'red-alert-pulse' : ''}`} 
        style={{ position: 'relative', flexGrow: 1, minHeight: '400px', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden', border: isHighRisk ? '1px solid var(--accent-red)' : '1px solid var(--border-glow)' }}
      >
        {streamData?.frame ? (
          <img 
            src={streamData.frame} 
            alt="Safety Feed" 
            style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
          />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', color: 'var(--text-muted)' }}>
            <Camera size={48} className="glow-text" style={{ animation: 'pulse-glow 2s infinite', color: 'var(--primary)' }} />
            <p style={{ fontSize: '0.9rem', letterSpacing: '1px' }}>WAITING FOR VIDEO TRANSMISSION...</p>
          </div>
        )}

        {/* HUD Crosshairs Overlay */}
        <div className="hud-crosshair" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', border: '1px dashed rgba(255,255,255,0.03)' }}>
          {/* Corner brackets */}
          <div style={{ position: 'absolute', top: '15px', left: '15px', width: '20px', height: '20px', borderTop: '2px solid rgba(255,255,255,0.2)', borderLeft: '2px solid rgba(255,255,255,0.2)' }}></div>
          <div style={{ position: 'absolute', top: '15px', right: '15px', width: '20px', height: '20px', borderTop: '2px solid rgba(255,255,255,0.2)', borderRight: '2px solid rgba(255,255,255,0.2)' }}></div>
          <div style={{ position: 'absolute', bottom: '15px', left: '15px', width: '20px', height: '20px', borderBottom: '2px solid rgba(255,255,255,0.2)', borderLeft: '2px solid rgba(255,255,255,0.2)' }}></div>
          <div style={{ position: 'absolute', bottom: '15px', right: '15px', width: '20px', height: '20px', borderBottom: '2px solid rgba(255,255,255,0.2)', borderRight: '2px solid rgba(255,255,255,0.2)' }}></div>
        </div>

        {/* Telemetry Panels overlay */}
        <div style={{ position: 'absolute', top: '20px', right: '20px', display: 'flex', flexDirection: 'column', gap: '8px', pointerEvents: 'none' }}>
          <div style={{ background: 'rgba(6, 7, 13, 0.85)', backdropFilter: 'blur(4px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '10px 14px', textAlign: 'right' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Threat Index</span>
            <span style={{ fontSize: '1.8rem', fontWeight: 800, fontFamily: 'var(--font-display)', color: isHighRisk ? 'var(--accent-red)' : 'var(--primary)' }}>
              {riskScore.toFixed(1)}%
            </span>
          </div>
          {isHighRisk && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255, 51, 102, 0.2)', border: '1px solid var(--accent-red)', borderRadius: '6px', padding: '6px 12px', color: 'var(--accent-red)', fontSize: '0.8rem', fontWeight: 600, animation: 'pulse-glow 1s infinite' }}>
              <AlertTriangle size={14} />
              SYSTEM CRITICAL
            </div>
          )}
        </div>

        {/* Bottom HUD HUD info */}
        <div style={{ position: 'absolute', bottom: '20px', left: '20px', display: 'flex', gap: '10px', pointerEvents: 'none' }}>
          <div style={{ background: 'rgba(6, 7, 13, 0.85)', backdropFilter: 'blur(4px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '6px', padding: '8px 12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={14} style={{ color: 'var(--accent-green)' }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 500 }}>AI GUARD ACTIVE</span>
          </div>
        </div>
      </div>

      {/* Grid selector / Cam Select List */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '10px' }}>
        {cameras.map(cam => (
          <button
            key={cam.id}
            onClick={() => setSelectedCameraId(cam.id)}
            style={{
              padding: '10px',
              background: cam.id === selectedCameraId ? 'rgba(0, 229, 255, 0.15)' : 'rgba(255, 255, 255, 0.02)',
              border: cam.id === selectedCameraId ? '1px solid var(--primary)' : '1px solid var(--border-glow)',
              borderRadius: '8px',
              color: cam.id === selectedCameraId ? 'var(--primary)' : 'var(--text-main)',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              transition: 'var(--transition-smooth)'
            }}
          >
            <Camera size={16} />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {cam.name}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CameraGrid;
