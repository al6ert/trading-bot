# Plan de Acción Inicial (Sprints)

## Resumen de Fases
El desarrollo se dividirá en 4 Sprints de corta duración para asegurar entregas incrementales y funcionales.

---

### Sprint 1: Infraestructura y Conectividad ("Hello World")
**Objetivo:** Establecer los cimientos y verificar que podemos "hablar" con Hyperliquid Testnet.

* **Tareas:**
    - [x] 1. Configurar repositorio y estructura de carpetas (Backend/Frontend).
    - [x] 2. Obtener credenciales de Testnet (API Wallet).
    - [x] 3. Crear script Python básico (`test_connection.py`) que:
        * Se conecte a Hyperliquid.
        * Obtenga el saldo de la cuenta.
        * Obtenga el precio actual de un activo BTC/USDC.
    - [x] 4. Levantar servidor FastAPI básico ("Health Check").

* **Entregable:** Un script que corre y muestra datos reales de la Testnet en consola.

---

### Sprint 2: El Cerebro (Data & Strategy)
**Objetivo:** Que el bot pueda "ver" el mercado y "pensar" (generar señales).

* **Tareas:**
    - [x] 1. Implementar `DataIngestor`: Suscripción a WebSocket para velas en tiempo real.
    - [x] 2. Implementar librería de indicadores (Pandas-TA): Calcular RSI, EMA, ADX.
    - [x] 3. Codificar la lógica "Single-Core":
        * Estrategia unificada sobre el 100% del capital (Sin escalado complejo).
        * Lógica de señales básica (EMA + ADX).
    - [x] 4. Logging de señales: El bot debe imprimir "SEÑAL DE COMPRA DETECTADA" en el log.

* **Entregable:** Logs del sistema mostrando análisis técnico en tiempo real y señales teóricas.

---

### Sprint 3: El Centinela y Ejecución (Trading Real)
**Objetivo:** Ejecutar operaciones de forma segura en Testnet.

* **Tareas:**
    - [x] 1. Implementar `RiskManager`:
        * Verificar saldo disponible.
        * Calcular tamaño de posición (1x Leverage).
        * Verificar límites de pérdida diaria.
    - [x] 2. Implementar `OrderExecutor`:
        * Firmar transacciones con la clave del API Agent.
        * Enviar órdenes LIMIT/MARKET a Hyperliquid.
    - [x] 3. Manejo de errores de ejecución.

* **Entregable:** El bot opera autónomamente en Testnet. Compra y vende según las señales.

---

### Sprint 4: The Narrative Cockpit (Frontend)
**Objetivo:** Interfaz visual avanzada centrada en la narrativa y la seguridad.

* **Tareas:**
    - [x] 1. Setup de Next.js + RainbowKit.
    - [x] 2. Conectar Frontend al Backend (FastAPI).
    - [ ] 3. **Implementar "Capital Allocation Bar":**
        * Integrar componente Slider Doble para "Safety Locks" (USDC/BTC).
        * Conectar a endpoint de configuración de reservas.
    - [ ] 4. **Implementar "Narrative Line Chart":**
        * Gráfico de línea con 4 colores semánticos (Verde, Naranja, Gris, Rojo).
        * Visualización de marcadores de compra/venta sobre la línea.
    - [ ] 5. **Widgets de Inteligencia:**
        * Alpha Cluster (Benchmarks vs Hold/DCA).
        * Session Health (Win Rate, Drawdown).
    - [ ] 6. Botón de Pánico: "Detener Bot" y "Cerrar Todo".

* **Entregable:** Aplicación web funcional con "Narrative Line" y controles de seguridad avanzados.

---

### Sprint 5: Validación y Ajustes (Refinamiento)
**Objetivo:** Asegurar que todo funciona integrado y el código es robusto.

* **Tareas:**
    - [ ] 1. Ejecutar Test E2E (Backend + Frontend).
    - [ ] 2. Verificar flujo de "Safety Locks": Asegurar que el backend respeta las reservas.
    - [ ] 3. Refactorizar `OrderExecutor`.

* **Entregable:** Sistema validado y listo para operar en Testnet sin errores críticos.
