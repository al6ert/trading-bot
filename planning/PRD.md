# Documento de Requisitos Técnicos (PRD) - Hyperliquid Trading Bot

## 1. Introducción
Este documento define los requisitos funcionales y técnicos para el desarrollo de un bot de trading automatizado en Hyperliquid Spot (Testnet). El sistema está diseñado para ser modular, seguro y no custodio.

## 2. Objetivos del Negocio
* **Preservación de Capital:** Priorizar la gestión de riesgo sobre el beneficio explosivo.
* **Automatización:** Eliminar la intervención manual en la ejecución de estrategias.
* **Transparencia Narrativa:** Proveer al usuario de un dashboard que explique el "por qué" de las operaciones (Narrative Cockpit).

## 3. Requisitos Funcionales

### 3.1. Gestión de Datos (Data Ingestor)
**[OWNER: API_SPEC & ARCHITECT]**
* **FR-01:** El sistema debe conectarse a la API de Hyperliquid (WebSocket preferible, REST fallback).
* **FR-02:** Debe procesar datos de mercado (Book, Trades) para generar velas (OHLCV) en tiempo real.
* **FR-03:** Debe soportar múltiples timeframes (15m como principal, soporte para 4h/1d).

### 3.2. Motor de Estrategia (Strategy Engine)
**[OWNER: ARCHITECT & API_SPEC]**
* **FR-04:** Implementar estrategia "Single-Core" (Bolsa Única):
    * El bot gestiona el capital asignado en una sola "bolsa" operativa.
    * Entradas y salidas unificadas (sin escalado complejo por ahora).
* **FR-05:** El sistema debe ser determinista.
    * **Timeframe Maestro (Ejecución):** 15 Minutos (M15). Las señales se evalúan al cierre de vela.

### 3.3. Gestión de Riesgo (Risk Manager)
**[OWNER: QA_SEC & ARCHITECT]**
* **FR-06:** **Restricción Crítica:** Apalancamiento (Leverage) siempre = 1x (Spot).
* **FR-07:** Mantener una reserva de liquidez configurable ("Soft Locking").
    * **FR-07-A:** Slider de Reserva USDC (Cash intocable).
    * **FR-07-B:** Slider de Reserva BTC (Vault/HODL intocable).
* **FR-08:** Validar "Max Drawdown" diario. Si se alcanza, detener trading por 24h.

### 3.4. Ejecución y Seguridad (Web3)
**[OWNER: QA_SEC & FRONTEND]**
* **FR-09:** Operaciones firmadas mediante "API Agent" autorizado por la wallet del usuario.
* **FR-10:** La clave privada maestra NUNCA toca el backend. Solo se usa la clave del API Agent (limitada a trading).

### 3.5. Dashboard de Usuario (The Narrative Cockpit)
**[OWNER: FRONTEND & UX_DESIGNER]**
* **FR-11:** **Narrative Line Chart:** Visualización del precio mediante una línea continua que cambia de color según el estado interno del bot (Verde/Naranja/Gris/Rojo), eliminando las velas japonesas tradicionales.
* **FR-12:** **Capital Allocation Bar:** Visualización de fondos con manejadores (sliders) integrados para gestionar las reservas de seguridad (FR-07).
* **FR-13:** **Benchmarks:** Comparativa de rendimiento relativo ("Alpha Cluster") contra estrategias pasivas (Buy & Hold, DCA).
* **FR-14:** **Session Health:** Métricas rápidas de la sesión actual (Win Rate, Drawdown).

## 4. Requisitos No Funcionales
* **NFR-01 (Seguridad):** No almacenar claves privadas de usuario en disco persistente sin encriptación.
* **NFR-02 (Rendimiento):** Latencia de procesamiento de señal < 200ms.
* **NFR-03 (Fiabilidad):** Recuperación automática ante desconexiones de WebSocket.

## 5. Stack Tecnológico Sugerido
* **Backend:** Python (FastAPI, Pandas, CCXT/Hyperliquid-SDK).
* **Frontend:** Next.js, Tailwind CSS, RainbowKit, Recharts (o Lightweight-charts con customización).
* **Infraestructura:** Docker (opcional para despliegue), ejecución local inicial.