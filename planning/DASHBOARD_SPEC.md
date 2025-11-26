# Dashboard UX Specification: "The Narrative Cockpit"

## 1. Philosophy: Operational Transparency
The user is a pilot, not an analyst. We replace technical noise (candles, complex indicators) with a narrative story:
1.  **Context over Data:** Don't show "RSI is 70", show "Market is Overheated".
2.  **State over Price:** The price line color matters more than the candle shape.
3.  **Alpha over Profit:** Show performance relative to the market (BTC), not just USD.

## 2. Layout: Single Page Grid (No Tabs)

```mermaid
graph TD
    Header[Header: Capital Bar with Safety Locks | Panic Button]
    Main[Main Section]
    
    subgraph "Main Section"
        Chart[Narrative Line Chart (The Story)]
        Intelligence[Intelligence Panel]
    end

    subgraph "Intelligence Panel (Bottom/Side)"
        Alpha[Alpha Cluster: Bot vs B&H vs DCA]
        Health[Session Health: WinRate/DD]
        Holdings[Active Holdings Table]
    end

    Header --> Main
```

## 3. Component Specifications

### A. Header: Capital Allocation & Safety Locks (FR-07, FR-12)

  - **Component:** `DoubleRangeSlider` overlaid on a Progress Bar.
  - **Visual:**
      - `[ 🔒 USDC Reserve ]` <--- `[ Active Bot Capital ]` ---> `[ 🔒 BTC Vault ]`
  - **Interactivity:**
      - Dragging left handle locks USDC (Dry Powder).
      - Dragging right handle locks BTC (HODL Mode).
      - **Warning:** Tooltip on BTC lock: "⚠️ Stopping sales here assumes HODL risk."

### B. Main Chart: "The Narrative Line" (FR-11)

  - **Type:** Continuous Line Chart (No Candles).
  - **The Palette (Semantic States):**
      - 🟢 **Electric Green:** Bull Trend (Attack Mode).
      - 🟠 **Amber/Safety Orange:** Bear Trend (Defense/Cash Mode).
      - 🔵 **Cool Gray:** Sideways/Chop (Wait Mode).
      - 🔴 **Crimson Red:** Panic/Error (Stopped).
  - **Markers:**
      - `Ghost Icon`: Potential Pivot detected (Warning).
      - `Rocket 🚀`: Confirmed Buy.
      - `Skull 💀`: Confirmed Sell / Stop Loss.

### C. Intelligence Panel

#### 1. Alpha Cluster (Benchmarks) (FR-13)

  - **Type:** Race Bars (Horizontal).
  - **Data:**
      - 🤖 **BOT:** Current PnL %.
      - 💰 **B&H:** BTC price change since start.
      - 📅 **DCA:** Simulated daily buy since start.
  - **Goal:** Answer "Am I beating the market?".

#### 2. Session Health (FR-14)

  - **Layout:** Compact Grid (3x1).
  - **Metrics:**
      - **Win Rate:** (e.g., "65%").
      - **Max DD:** Session Drawdown (e.g., "-1.2%").
      - **Profit Factor:** Gross Win / Gross Loss.

#### 3. Active Holdings

  - **Columns:** Asset | Size | Avg Entry | Current Price | PnL (USD/%) | Value.
  - **Note:** In Spot, this tracks the "Virtual Position" performance.

## 4. Implementation Notes

  - **Frontend:** Use a charting library that supports gradient/segment coloring based on data attributes (e.g., Recharts `stops` or Canvas API).
  - **Backend:** Needs to send `strategy_state` along with `price` and `time` in the historical data endpoint.
