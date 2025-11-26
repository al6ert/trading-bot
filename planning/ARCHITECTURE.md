# Arquitectura y Estructura de Ficheros

## 1. Diagrama de Arquitectura (Conceptual)

```mermaid
graph TD
    User[Usuario (Inversor)] -->|Conecta Wallet| Frontend[Dashboard Next.js]
    Frontend -->|Consulta Estado| BackendAPI[FastAPI Backend]
    
    subgraph "Backend Core (Python)"
        BackendAPI --> Controller
        Controller --> StrategyEngine[Motor de Estrategia]
        Controller --> RiskManager[Gestor de Riesgo]
        
        DataIngestor[Recolector de Datos] -->|OHLCV| StrategyEngine
        DataIngestor -->|Market Data| Hyperliquid[Hyperliquid API]
        
        StrategyEngine -->|Señal| RiskManager
        RiskManager -->|Orden Aprobada| Executor[Ejecutor de Órdenes]
        Executor -->|Firma (API Agent)| Hyperliquid
    end
    
    subgraph "Persistencia"
        DB[(SQLite/JSON Logs)]
        BackendAPI -.-> DB
    end
```

## 2. Estructura de Directorios

```text
/trader-bot
├── /planning                   # Documentación del proyecto
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── ACTION_PLAN.md
│
├── /backend                    # Código fuente del Bot (Python)
│   ├── /app
│   │   ├── __init__.py
│   │   ├── main.py             # Entrypoint FastAPI
│   │   ├── config.py           # Configuración global (Vars de entorno)
│   │   │
│   │   ├── /api                # API Routes
│   │   │   └── routes.py
│   │   │
│   │   ├── /core               # Lógica central
│   │   │   ├── engine.py       # Loop principal del bot
│   │   │   └── events.py       # Sistema de eventos interno
│   │   │
│   │   ├── /domain             # Reglas de negocio
│   │   │   ├── /strategies     # Implementación de estrategias
│   │   │   │   ├── base.py
│   │   │   │   ├── strategy.py
│   │   │   │   └── indicators.py
│   │   │   └── risk.py         # The Sentinel (Risk Manager)
│   │   │
│   │   └── /infrastructure     # Adaptadores externos
│   │       ├── connector.py    # Cliente Hyperliquid
│   │       └── store.py        # Gestión de datos/logs
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── /frontend                   # Código fuente del Dashboard (Next.js)
│   ├── /src
│   │   ├── /app                # Next.js App Router
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── /components         # Componentes React
│   │   │   ├── /dashboard
│   │   │   └── /shared
│   │   └── /lib                # Utilidades Web3/API
│   │
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
└── README.md
```
