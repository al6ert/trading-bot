# Dashboard UX Specification: "The Cockpit"

## 1. Philosophy: Operational Transparency
The user is a pilot, not an analyst. They need to know:
1.  **Status:** Is the bot running? Is it safe?
2.  **Context:** What is the market doing? (Trend vs Range)
3.  **Action:** What is the bot doing about it?

## 2. Layout: Single Page Grid (Desktop First)
Eliminate navigation between "Dashboard" and "Analytics". Everything important fits on one screen.

```mermaid
graph TD
    Header[Header: Wallet | Bot Status (On/Off) | Panic Button]
    KPIs[KPI Row: Equity | PnL 24h | Active Strategy | Risk Level]
    Chart[Main Chart: Price + EMA + Trades]
    Indicators[Sub-Chart: ADX / Regime Strength]
    Positions[Active Positions Table]
    Logs[Narrative Log Feed]

    Header --> KPIs
    KPIs --> Chart
    Chart --> Indicators
    KPIs --> Positions
    Positions --> Logs
```

## 3. Component Specifications

### A. KPI Header (The Vitals)
- **Total Equity:** Big, bold.
- **24h PnL:** Color-coded (Green/Red).
- **Active Strategy:**
    - **Visual:** Icon changing based on regime (e.g., 📈 for Trend, ↔️ for Range).
    - **Text:** "Single-Core: Bull Trend" or "Single-Core: Sideways".
- **Risk/Exposure:** "100% Invested" or "Cash Heavy".

### B. Main Chart (The Battlefield)
- **Overlay:** EMA 200 (or relevant trend filter).
- **Markers:** Buy/Sell arrows (already exists).
- **Interactivity:** Infinite scroll (already exists).

### C. Indicator Panel (The Brain) - **NEW**
- **Visual:** A small chart below the main price chart.
- **Data:** ADX (Average Directional Index).
- **Story:**
    - ADX > 25: Background highlights GREEN (Trending).
    - ADX < 25: Background highlights GRAY (Choppy).
- **Why:** Explains *why* the bot is buying or holding.

### D. Positions Table (The Bag)
- **Columns:** Symbol | Size | Entry | Current Price | PnL (USD/%) | Action (Close Button).
- **Style:** Compact.

### E. Narrative Logs (The Voice)
- Filter logs to show "Decisions" vs "System".
- **Format:** Time | Icon | Message.
- **Example:** "10:00 | 🧠 | ADX is 30. Market is Trending. Looking for Longs."

## 4. Refactoring Plan (Frontend)
1.  **Delete:** `app/analytics` (Dead code).
2.  **Modify:** `app/dashboard/page.tsx` to implement the Grid layout.
3.  **Enhance:** `TradingViewChart.tsx` to support a secondary series (Histogram or Line) for ADX if possible, or create a separate `IndicatorChart` component.
