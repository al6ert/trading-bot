import React from 'react';
import { XCircle } from 'lucide-react';

interface Position {
  symbol: string;
  size: number;
  entry_price: number;
  value_usd: number;
  // Add other fields if available from backend, e.g., current_price, pnl
}

interface PositionsTableProps {
  positions: Position[];
}

export const PositionsTable: React.FC<PositionsTableProps> = ({ positions }) => {
  if (!positions || positions.length === 0) {
    return (
      <div className="text-center py-8 opacity-50 text-sm">
        No active positions
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="table table-sm w-full">
        <thead>
          <tr className="opacity-70">
            <th>Symbol</th>
            <th className="text-right">Size</th>
            <th className="text-right">Entry</th>
            <th className="text-right">Value</th>
            <th className="text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((pos, idx) => (
            <tr key={`${pos.symbol}-${idx}`} className="hover:bg-base-200/50">
              <td className="font-bold">{pos.symbol}</td>
              <td className="text-right font-mono">{pos.size}</td>
              <td className="text-right font-mono">${pos.entry_price.toLocaleString()}</td>
              <td className="text-right font-mono">${pos.value_usd.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
              <td className="text-right">
                <button className="btn btn-ghost btn-xs text-error" title="Close Position">
                    <XCircle className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
