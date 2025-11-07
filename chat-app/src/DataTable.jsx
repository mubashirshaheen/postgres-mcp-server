import React from 'react';
import './DataTable.css';

const DataTable = ({ data }) => {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <p className="text-slate-500">No data available</p>;
  }

  const columns = Object.keys(data[0]);

  const formatValue = (key, value) => {
    if (value === null || value === undefined) return 'N/A';

    // Check if value is link then style it as link
    if (typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))) {
        return (
            <a href
                   ={value} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
                {value}
            </a>
        );
    }
    // Format dates
    if (typeof value === 'string' && (key.includes('date') || key.includes('_at') || key.includes('time'))) {
      try {

        const date = new Date(value);
        if (!Number.isNaN(date.getTime())) {
          return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });
        }
      } catch {
        return value;
      }
    }

    // Format booleans
    if (typeof value === 'boolean') {

      return <span className="master">{value ? 'True' : 'False'}</span>;
    }

    // Format arrays (recursive, robust)
    if (Array.isArray(value)) {

      return (
        <span className="master">
          {value.map((item, index) => (
            <span className="master" key={index}>
              {typeof item === 'object' && item !== null ? JSON.stringify(item) : String(item)}
              {index < value.length - 1 && ', '}
            </span>
          ))}
        </span>
      );
    }

    // Format objects (robust, shallow pretty)
    if (typeof value === 'object' && value !== null) {

      return (
        <span>
          {Object.entries(value).map(([k, v], idx) => (
            <span key={k}>
              <strong>{k}:</strong> {typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v)}
              {idx < Object.entries(value).length - 1 && ', '}
            </span>
          ))}
        </span>
      );
    }

    // Numbers, strings, etc
    return value;
  };

  return (
    <div className="simple-table-container">
      <div className="table-wrapper">
        <table className="simple-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={item.id || index}>
                {columns.map((column) => (
                  <td key={column} className="master">
                    {formatValue(column, item[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DataTable;