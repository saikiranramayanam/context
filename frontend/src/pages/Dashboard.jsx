import React, { useEffect, useState } from 'react';
import { LayoutDashboard, Video, Database, Settings, RefreshCw, Shield, AlertTriangle } from 'lucide-react';
import OverviewTab from '../components/dashboard/OverviewTab';
import LiveMonitorTab from '../components/dashboard/LiveMonitorTab';
import IncidentHistoryTab from '../components/dashboard/IncidentHistoryTab';
import SystemSettingsTab from '../components/dashboard/SystemSettingsTab';
import '../styles/dashboard.css';

const API_BASE = `http://${window.location.hostname}:8000/api`;

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [cameras, setCameras] = useState([]);
  const [selectedCameraId, setSelectedCameraId] = useState(null);
  const [stats, setStats] = useState({
    total_events: 0,
    active_cameras: 0,
    avg_risk: 0.0,
    safety_status: 'SAFE',
  });
  const [events, setEvents] = useState([]);

  // Fetch all cameras
  const fetchCameras = async () => {
    try {
      const res = await fetch(`${API_BASE}/cameras`);
      if (res.ok) {
        const data = await res.json();
        setCameras(data);
        if (data.length > 0 && selectedCameraId === null) {
          const active = data.find(c => c.is_active);
          setSelectedCameraId(active ? active.id : data[0].id);
        }
      }
    } catch (e) {
      console.error('Error fetching cameras:', e);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/events/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Error fetching stats:', e);
    }
  };

  // Fetch events
  const fetchEvents = async () => {
    try {
      const res = await fetch(`${API_BASE}/events`);
      if (res.ok) {
        const data = await res.json();
        setEvents(data);
      }
    } catch (e) {
      console.error('Error fetching events:', e);
    }
  };

  // Refresh dashboard data
  const refreshData = () => {
    fetchCameras();
    fetchStats();
    fetchEvents();
  };

  // Initial load and periodic polling for real-time telemetry
  useEffect(() => {
    refreshData();

    // Poll stats and events every 2.5 seconds
    const interval = setInterval(() => {
      fetchStats();
      fetchEvents();
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  // Delete camera
  const handleDeleteCamera = async (id) => {
    if (!window.confirm('Are you sure you want to delete this camera feed?')) return;
    try {
      const res = await fetch(`${API_BASE}/cameras/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        if (selectedCameraId === id) {
          setSelectedCameraId(null);
        }
        fetchCameras();
        fetchStats();
      }
    } catch (e) {
      console.error('Error deleting camera:', e);
    }
  };

  // Toggle active status
  const handleToggleCameraActive = async (camera) => {
    const updatedPayload = {
      name: camera.name,
      source: camera.source,
      is_active: !camera.is_active,
      threshold: camera.threshold,
      zone_min_x: camera.zone_min_x,
      zone_min_y: camera.zone_min_y,
      zone_max_x: camera.zone_max_x,
      zone_max_y: camera.zone_max_y
    };

    try {
      const res = await fetch(`${API_BASE}/cameras/${camera.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedPayload),
      });
      if (res.ok) {
        fetchCameras();
        fetchStats();
      }
    } catch (e) {
      console.error('Error toggling camera active state:', e);
    }
  };

  // Delete individual incident alert
  const handleDeleteAlert = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/events/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        fetchEvents();
        fetchStats();
      }
    } catch (e) {
      console.error('Error deleting alert:', e);
    }
  };

  // Clear all alerts
  const handleClearAllAlerts = async () => {
    if (!window.confirm('Are you sure you want to permanently clear the entire incident history?')) return;
    try {
      const res = await fetch(`${API_BASE}/events`, {
        method: 'DELETE',
      });
      if (res.ok) {
        fetchEvents();
        fetchStats();
      }
    } catch (e) {
      console.error('Error clearing alerts:', e);
    }
  };

  // Determine status color class
  const getStatusClass = (status) => {
    switch (status) {
      case 'CRITICAL':
        return 'status-critical';
      case 'WARNING':
        return 'status-warning';
      default:
        return 'status-safe';
    }
  };

  const getTabTitle = () => {
    switch (activeTab) {
      case 'overview': return 'Operations Dashboard';
      case 'live': return 'Live Monitor Feed';
      case 'audit': return 'Incident Audit Logs';
      case 'settings': return 'System Settings';
      default: return 'Aegis Sentinel';
    }
  };

  const getTabSubtitle = () => {
    switch (activeTab) {
      case 'overview': return 'High-level real-time safety stats and threat distribution analytics.';
      case 'live': return 'Observe active AI detection feeds, camera feeds, and real-time alert logs.';
      case 'audit': return 'Search, review, inspect snapshots, and download historical threat alerts.';
      case 'settings': return 'Register and calibrate cameras, alert thresholds, and hot zone boundaries.';
      default: return '';
    }
  };

  return (
    <div className="dashboard-layout">
      {/* Left Sidebar Navigation */}
      <aside className="sidebar">
        <div>
          {/* Brand/Logo */}
          <div className="sidebar-brand">
            <Shield className="sidebar-logo" size={24} />
            <h1 className="sidebar-title">Aegis Sentinel</h1>
          </div>

          {/* Navigation Links */}
          <nav className="sidebar-menu">
            <button 
              className={`sidebar-item ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              <LayoutDashboard size={18} />
              Overview
            </button>
            <button 
              className={`sidebar-item ${activeTab === 'live' ? 'active' : ''}`}
              onClick={() => setActiveTab('live')}
            >
              <Video size={18} />
              Live Monitor
            </button>
            <button 
              className={`sidebar-item ${activeTab === 'audit' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit')}
            >
              <Database size={18} />
              Incident Log
            </button>
            <button 
              className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              <Settings size={18} />
              Node Settings
            </button>
          </nav>
        </div>

        {/* Sidebar Footer Indicators */}
        <div className="sidebar-footer">
          <div className={`system-status-indicator ${getStatusClass(stats.safety_status)}`} style={{ justifyContent: 'center' }}>
            {stats.safety_status === 'SAFE' && 'SYSTEM CLEAR'}
            {stats.safety_status === 'WARNING' && 'ANOMALY DETECTED'}
            {stats.safety_status === 'CRITICAL' && 'CRITICAL ALARM'}
          </div>
          
          <button 
            className="btn-cyber" 
            style={{ width: '100%', padding: '8px', fontSize: '0.8rem' }}
            onClick={refreshData}
            title="Refresh database records"
          >
            <RefreshCw size={14} />
            Force Refresh
          </button>
        </div>
      </aside>

      {/* Main Workspace Area */}
      <main className="main-content">
        {/* Content Header */}
        <header className="content-header">
          <div className="header-title-group">
            <h2 className="header-title">{getTabTitle()}</h2>
            <span className="header-subtitle">{getTabSubtitle()}</span>
          </div>

          <div className="header-actions">
            {stats.safety_status !== 'SAFE' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-red)', animation: 'pulse-glow 1.5s infinite', fontSize: '0.8rem', fontWeight: 700 }}>
                <AlertTriangle size={16} />
                SAFETY EXCEPTION ACTIVE
              </div>
            )}
          </div>
        </header>

        {/* Scrollable Subpage Body */}
        <div className="content-body">
          {activeTab === 'overview' && (
            <OverviewTab 
              stats={stats} 
              cameras={cameras} 
              events={events} 
            />
          )}

          {activeTab === 'live' && (
            <LiveMonitorTab 
              cameras={cameras} 
              selectedCameraId={selectedCameraId}
              setSelectedCameraId={setSelectedCameraId}
              events={events} 
            />
          )}

          {activeTab === 'audit' && (
            <IncidentHistoryTab 
              events={events} 
              onDeleteAlert={handleDeleteAlert}
              onClearAll={handleClearAllAlerts}
            />
          )}

          {activeTab === 'settings' && (
            <SystemSettingsTab 
              cameras={cameras}
              fetchCameras={fetchCameras}
              fetchStats={fetchStats}
              onToggleActive={handleToggleCameraActive}
              onDeleteCamera={handleDeleteCamera}
            />
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
