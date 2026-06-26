import React, { useState } from 'react';
import { Search, Download, Trash2, Filter } from 'lucide-react';
import AlertPanel from '../AlertPanel';

const IncidentHistoryTab = ({ events, onDeleteAlert, onClearAll }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');

  // Filter events based on search query and severity
  const filteredEvents = events.filter(e => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = 
      (e.description && e.description.toLowerCase().includes(q)) ||
      (e.camera_name && e.camera_name.toLowerCase().includes(q));

    if (severityFilter === 'critical') {
      return matchesSearch && e.score >= 70.0;
    } else if (severityFilter === 'warning') {
      return matchesSearch && e.score < 70.0;
    }
    return matchesSearch;
  });

  // Export audit log data as CSV file
  const handleExportCSV = () => {
    if (filteredEvents.length === 0) return;
    
    const headers = ['ID', 'Timestamp', 'Camera ID', 'Camera Name', 'Threat Index (%)', 'Description'];
    const rows = filteredEvents.map(e => [
      e.id,
      new Date(e.timestamp).toLocaleString(),
      e.camera_id,
      e.camera_name || 'Unknown',
      e.score.toFixed(0),
      `"${(e.description || '').replace(/"/g, '""')}"`
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(r => r.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `aegis_sentinel_audit_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="history-layout">
      {/* Header controls for search, filter, and actions */}
      <div className="filter-bar">
        {/* Search */}
        <div className="search-input-wrapper">
          <Search size={16} style={{ color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            className="search-field" 
            placeholder="Search by description or camera name..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Severity filter buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Filter size={12} /> Filter:
          </span>
          <button 
            className={`btn-cyber`}
            style={{ 
              padding: '4px 10px', 
              fontSize: '0.75rem',
              backgroundColor: severityFilter === 'all' ? 'var(--primary)' : 'rgba(255, 255, 255, 0.02)',
              color: severityFilter === 'all' ? '#fff' : 'var(--text-muted)',
              borderColor: severityFilter === 'all' ? 'var(--primary)' : '#1e293b'
            }}
            onClick={() => setSeverityFilter('all')}
          >
            All
          </button>
          <button 
            className={`btn-cyber`}
            style={{ 
              padding: '4px 10px', 
              fontSize: '0.75rem',
              backgroundColor: severityFilter === 'critical' ? 'var(--accent-red)' : 'rgba(255, 255, 255, 0.02)',
              color: severityFilter === 'critical' ? '#fff' : 'var(--text-muted)',
              borderColor: severityFilter === 'critical' ? 'var(--accent-red)' : '#1e293b'
            }}
            onClick={() => setSeverityFilter('critical')}
          >
            Critical (≥70%)
          </button>
          <button 
            className={`btn-cyber`}
            style={{ 
              padding: '4px 10px', 
              fontSize: '0.75rem',
              backgroundColor: severityFilter === 'warning' ? 'var(--accent-yellow)' : 'rgba(255, 255, 255, 0.02)',
              color: severityFilter === 'warning' ? '#000' : 'var(--text-muted)',
              borderColor: severityFilter === 'warning' ? 'var(--accent-yellow)' : '#1e293b'
            }}
            onClick={() => setSeverityFilter('warning')}
          >
            Warnings (&lt;70%)
          </button>
        </div>

        {/* CSV export */}
        {filteredEvents.length > 0 && (
          <button 
            className="btn-cyber" 
            onClick={handleExportCSV}
            title="Download current filtered events as CSV"
          >
            <Download size={14} />
            Export CSV ({filteredEvents.length})
          </button>
        )}
      </div>

      {/* Main Alert Panel rendering history list */}
      <div style={{ flexGrow: 1, minHeight: 0 }}>
        <AlertPanel 
          events={filteredEvents}
          onDeleteAlert={onDeleteAlert}
          onClearAll={onClearAll}
        />
      </div>
    </div>
  );
};

export default IncidentHistoryTab;
