import React from 'react';
import { Camera, AlertTriangle, Shield, BarChart3, Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import StatsCard from '../StatsCard';

const OverviewTab = ({ stats, cameras, events }) => {
  // 1. Process recent events for Timeline Chart (last 12 events, chronological order)
  const timelineData = [...events]
    .slice(0, 12)
    .reverse()
    .map(e => ({
      time: new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      score: e.score,
      camera: e.camera_name || 'Camera'
    }));

  // 2. Process events for Camera Incident Comparison Chart
  const cameraCounts = {};
  cameras.forEach(c => {
    cameraCounts[c.name] = 0;
  });
  events.forEach(e => {
    const camName = e.camera_name || 'Unknown';
    if (cameraCounts[camName] !== undefined) {
      cameraCounts[camName] += 1;
    } else {
      cameraCounts[camName] = (cameraCounts[camName] || 0) + 1;
    }
  });
  const distributionData = Object.keys(cameraCounts).map(name => ({
    name: name.length > 18 ? name.substring(0, 15) + '...' : name,
    alerts: cameraCounts[name]
  }));

  const activeCamerasCount = cameras.filter(c => c.is_active).length;

  return (
    <div className="overview-layout">
      {/* Metrics Row */}
      <div className="stats-grid">
        <StatsCard 
          label="Operational Nodes" 
          value={`${activeCamerasCount} / ${cameras.length}`}
          icon={Camera}
        />
        <StatsCard 
          label="Active Threats Flagged" 
          value={stats.total_events}
          icon={AlertTriangle}
          className={stats.total_events > 0 && stats.safety_status === 'CRITICAL' ? 'critical' : ''}
        />
        <StatsCard 
          label="Average Threat Index" 
          value={`${stats.avg_risk}%`}
          icon={Activity}
        />
        <StatsCard 
          label="Safety Severity Status" 
          value={stats.safety_status}
          icon={Shield}
          className={stats.safety_status === 'CRITICAL' ? 'critical' : ''}
        />
      </div>

      {/* Analytics Charts */}
      <div className="charts-grid">
        {/* Chart 1: Recent Threat Timeline */}
        <div className="chart-panel">
          <h3 className="chart-title">
            <Activity size={18} style={{ color: 'var(--primary-light)' }} />
            Safety Threat Level Trend (Recent Incidents)
          </h3>
          <div style={{ width: '100%', height: 250 }}>
            {timelineData.length > 0 ? (
              <ResponsiveContainer>
                <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-red)" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="var(--accent-red)" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={10} domain={[40, 100]} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#f8fafc' }}
                    labelStyle={{ color: 'var(--text-muted)', fontSize: 11 }}
                    itemStyle={{ color: 'var(--accent-red)', fontSize: 12 }}
                  />
                  <Area type="monotone" dataKey="score" stroke="var(--accent-red)" strokeWidth={2} fillOpacity={1} fill="url(#colorScore)" name="Threat Score" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No events recorded. Waiting for incoming telemetry...
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Incidents Distribution by Camera */}
        <div className="chart-panel">
          <h3 className="chart-title">
            <BarChart3 size={18} style={{ color: 'var(--primary-light)' }} />
            Threat Event Frequency by Camera Node
          </h3>
          <div style={{ width: '100%', height: 250 }}>
            {cameras.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={distributionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={9} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={10} allowDecimals={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#f8fafc' }}
                    labelStyle={{ color: 'var(--text-muted)', fontSize: 11 }}
                    itemStyle={{ color: 'var(--primary-light)', fontSize: 12 }}
                  />
                  <Bar dataKey="alerts" fill="var(--primary)" radius={[4, 4, 0, 0]} name="Incidents Count" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No cameras registered.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Nodes Status Listing */}
      <div className="overview-nodes-section">
        <h3 className="section-title">Operational Cameras Status</h3>
        <div className="node-status-grid">
          {cameras.map(cam => (
            <div key={cam.id} className="node-status-card">
              <div className="node-status-header">
                <span className="node-status-name" title={cam.name}>{cam.name}</span>
                <span className={`node-status-badge ${cam.is_active ? 'active' : 'inactive'}`}>
                  {cam.is_active ? 'Online' : 'Offline'}
                </span>
              </div>
              <div className="node-status-details">
                <div className="node-detail-row">
                  <span>Stream Source:</span>
                  <span className="node-detail-value">{cam.source}</span>
                </div>
                <div className="node-detail-row">
                  <span>Alarm Trigger Threshold:</span>
                  <span className="node-detail-value">{cam.threshold || 70}%</span>
                </div>
                <div className="node-detail-row">
                  <span>Detection Zone limits:</span>
                  <span className="node-detail-value">
                    [{cam.zone_min_x.toFixed(1)}, {cam.zone_min_y.toFixed(1)}] to [{cam.zone_max_x.toFixed(1)}, {cam.zone_max_y.toFixed(1)}]
                  </span>
                </div>
              </div>
            </div>
          ))}
          {cameras.length === 0 && (
            <div className="glass-panel" style={{ gridColumn: '1 / -1', padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No cameras configured. Please go to Node Settings to register camera streams.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OverviewTab;
