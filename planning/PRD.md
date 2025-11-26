# Documento de Requisitos Técnicos (PRD) - Hyperliquid Trading Bot

## 1. Introducción
Este documento define los requisitos funcionales y técnicos para el desarrollo de un bot de trading automatizado en Hyperliquid Spot (Testnet). El sistema está diseñado para ser modular, seguro y no custodio.

## 2. Objetivos del Negocio
*   **Preservación de Capital:** Priorizar la gestión de riesgo sobre el beneficio explosivo.
*   **Automatización:** Eliminar la intervención manual en la ejecución de estrategias.
*   **Transparencia:** Proveer al usuario de un dashboard claro sobre el estado de sus fondos y operaciones.

## 3. Requisitos Funcionales

### 3.1. Gestión de Datos (Data Ingestor)
**[OWNER: API_SPEC & ARCHITECT]**
*   **FR-01:** El sistema debe conectarse a la API de Hyperliquid (WebSocket preferible, REST fallback).
*   **FR-02:** Debe procesar datos de mercado (Book, Trades) para generar velas (OHLCV) en tiempo real.
*   **FR-03:** Debe soportar múltiples timeframes (1m, 5m, 15m, 1h, 4h).

### 3.2. Motor de Estrategia (Strategy Engine)
**[OWNER: ARCHITECT & API_SPEC]**
*   **FR-04:** Implementar estrategia "Single-Core" (Bolsa Única):
    *   El bot gestiona el 100% del capital disponible en la cuenta.
    *   No hay separación entre "Long Term" y "Short Term".
*   **FR-05:** El sistema debe ser determinista.
    *   **Timeframe Maestro (Ejecución):** 15 Minutos (M15). Las señales se evalúan al cierre de vela.

### 3.3. Gestión de Riesgo (Risk Manager)
**[OWNER: QA_SEC & ARCHITECT]**
*   **FR-06:** **Restricción Crítica:** Apalancamiento (Leverage) siempre = 1x.
*   **FR-07:** Mantener una reserva de liquidez configurable (ej. 20% en USDC).
*   **FR-08:** Validar "Max Drawdown" diario. Si se alcanza, detener trading por 24h.

### 3.4. Ejecución y Seguridad (Web3)
**[OWNER: QA_SEC & FRONTEND]**
*   **FR-09:** Operaciones firmadas mediante "API Agent" autorizado por la wallet del usuario.
*   **FR-10:** La clave privada maestra NUNCA toca el backend. Solo se usa la clave del API Agent (limitada a trading).

### 3.5. Dashboard de Usuario
**[OWNER: FRONTEND]**
*   **FR-11:** Autenticación vía Web3 (Connect Wallet).
*   **FR-12:** Visualización de saldo total, distribución de activos y PnL (Profit and Loss).
*   **FR-13:** Logs de actividad en tiempo real ("Comprando ETH...", "Esperando señal...").

## 4. Requisitos No Funcionales
*   **NFR-01 (Seguridad):** No almacenar claves privadas de usuario en disco persistente sin encriptación.
*   **NFR-02 (Rendimiento):** Latencia de procesamiento de señal < 200ms.
*   **NFR-03 (Fiabilidad):** Recuperación automática ante desconexiones de WebSocket.

## 5. Stack Tecnológico Sugerido
*   **Backend:** Python (FastAPI, Pandas, CCXT/Hyperliquid-SDK).
*   **Frontend:** Next.js, Tailwind CSS, RainbowKit.
*   **Infraestructura:** Docker (opcional para despliegue), ejecución local inicial.
