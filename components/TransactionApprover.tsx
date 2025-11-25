'use client';

import { useEffect, useState } from 'react';
import { useAccount, useSignTypedData } from 'wagmi';
import { toast } from 'react-hot-toast';

// Tipo de dato para la orden (Acordar con Architect)
type OrderPayload = {
  id: string;
  type: 'LIMIT' | 'MARKET';
  coin: string;
  is_buy: boolean;
  sz: number;
  limit_px: number;
  timestamp: number;
  // Estructura EIP-712 específica de Hyperliquid
  domain: any;
  types: any;
  message: any;
};

export const TransactionApprover = () => {
  const { isConnected } = useAccount();
  const { signTypedDataAsync } = useSignTypedData();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [pendingOrder, setPendingOrder] = useState<OrderPayload | null>(null);

  useEffect(() => {
    // Connect to the same WS feed as the LogPanel
    const ws = new WebSocket('ws://localhost:8000/api/v2/ws/feed');
    
    ws.onopen = () => {
        console.log('TransactionApprover: WS Connected');
    };

    ws.onmessage = (event) => {
      try {
          const data = JSON.parse(event.data);
          if (data.type === 'ORDER_REQUEST') {
            console.log('TransactionApprover: Order Request Received', data.data);
            setPendingOrder(data.data);
            triggerToast(data.data);
          }
      } catch (e) {
          console.error('TransactionApprover: Failed to parse WS message', e);
      }
    };

    ws.onerror = (e) => {
        console.error('TransactionApprover: WS Error', e);
    };

    return () => ws.close();
  }, []);

  const triggerToast = (order: OrderPayload) => {
    toast.custom((t) => (
      <div className={`bg-base-100 border border-warning p-4 rounded-lg shadow-xl flex flex-col gap-3 ${t.visible ? 'animate-enter' : 'animate-leave'}`}>
        <div className="flex items-center gap-2">
          <span className="loading loading-ring loading-sm text-warning"></span>
          <h3 className="font-bold text-sm">Firma Requerida</h3>
        </div>
        <div className="text-xs font-mono opacity-80">
          <p className="font-bold text-lg">{order.is_buy ? 'COMPRAR' : 'VENDER'} {order.sz} {order.coin}</p>
          <p>Precio: <span className="text-warning">${order.limit_px}</span></p>
        </div>
        <div className="flex gap-2 mt-2">
          <button 
            onClick={() => handleSign(order, t.id)}
            className="btn btn-xs btn-primary font-bold"
          >
            Firmar Transacción
          </button>
          <button 
            onClick={() => toast.dismiss(t.id)}
            className="btn btn-xs btn-ghost"
          >
            Rechazar
          </button>
        </div>
      </div>
    ), { duration: 30000, id: `order-${order.id}` }); 
  };

  const handleSign = async (order: OrderPayload, toastId: string) => {
    if (!isConnected) {
      toast.error("⚠️ Conecta tu wallet primero");
      return;
    }

    const toastLoading = toast.loading("Firmando...", { id: toastId });

    try {
      // 1. Firmar el mensaje EIP-712
      // Nota: Hyperliquid usa un dominio y tipos específicos. 
      // El backend debe proveerlos correctamente en el payload.
      const signature = await signTypedDataAsync({
        domain: order.domain,
        types: order.types,
        primaryType: 'Agent', // O 'Exchange' dependiendo de la acción
        message: order.message,
      });

      // 2. Enviar firma al backend
      const res = await fetch('http://localhost:8000/api/v2/order/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: order.id,
          signature: signature
        })
      });

      if (res.ok) {
          toast.success("✅ Orden enviada a la red", { id: toastLoading });
          setPendingOrder(null);
      } else {
          throw new Error("Backend rejected signature");
      }

    } catch (error) {
      console.error("Error firmando:", error);
      toast.error("❌ Error al firmar", { id: toastLoading });
    }
  };

  return null; 
};
