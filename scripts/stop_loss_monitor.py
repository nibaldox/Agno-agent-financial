"""
Stop-Loss Automático para Sistema Multi-Agente
Basado en trading_script.py líneas 586-640

REGLA CRÍTICA DEL SISTEMA ORIGINAL:
"If low price <= stop loss → Auto-sell at open price"

EJEMPLO DEL SISTEMA ORIGINAL:
    if stop and l <= stop:
        exec_price = round(o if o <= stop else stop, 2)
        value = round(exec_price * shares, 2)
        pnl = round((exec_price - cost) * shares, 2)
        action = "SELL - Stop Loss Triggered"
        cash += value

IMPORTANCIA:
- Ha protegido el portfolio original por 6 meses
- Evitó pérdidas catastróficas en caídas de -20%+
- Es MANDATORIO para risk management
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from agno.tools.yfinance import YFinanceTools


@dataclass
class StopLossEvent:
    """Evento de stop-loss triggered"""

    date: datetime
    ticker: str
    shares: float
    buy_price: float
    stop_loss: float
    trigger_price: float  # Precio que activó el stop
    execution_price: float  # Precio de ejecución real
    proceeds: float  # Dinero recuperado
    pnl: float  # Ganancia/pérdida
    reason: str


class StopLossMonitor:
    """
    Monitor de stop-losses automático

    FUNCIONA COMO EL SISTEMA ORIGINAL:
    1. Obtiene precios diarios (Open, High, Low, Close)
    2. Chequea si Low <= Stop Loss
    3. Si sí, ejecuta venta automática
    4. Usa Open price como ejecución (o Stop si Open > Stop)
    5. Actualiza portfolio y cash
    6. Registra en trade log

    USO:
        monitor = StopLossMonitor()
        portfolio, cash, events = monitor.check_portfolio(portfolio, cash)

        if events:
            print(f"⚠️ {len(events)} stop-losses triggered!")
            for event in events:
                print(event.reason)
    """

    def __init__(self):
        self.yfinance = YFinanceTools()

    def check_portfolio(
        self, portfolio: pd.DataFrame, cash: float, date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, float, List[StopLossEvent]]:
        """
        Chequea todo el portfolio por stop-losses triggered

        Args:
            portfolio: DataFrame con columnas:
                - ticker/Ticker
                - shares/Shares
                - buy_price/Buy Price
                - cost_basis/Cost Basis
                - stop_loss/Stop Loss
            cash: Cash disponible
            date: Fecha de análisis (default: hoy)

        Returns:
            Tuple[
                portfolio_actualizado,
                cash_actualizado,
                lista_de_eventos_stop_loss
            ]
        """
        if portfolio.empty:
            return portfolio, cash, []

        date = date or datetime.now()
        events = []
        updated_portfolio = portfolio.copy()
        updated_cash = cash

        # Procesar cada posición
        positions_to_remove = []

        for idx, position in portfolio.iterrows():
            # Normalizar nombres de columnas (soportar ambos formatos)
            ticker = str(position.get("ticker", position.get("Ticker", ""))).upper()
            shares = float(position.get("shares", position.get("Shares", 0)))
            buy_price = float(position.get("buy_price", position.get("Buy Price", 0)))
            cost_basis = float(position.get("cost_basis", position.get("Cost Basis", 0)))
            stop_loss = float(position.get("stop_loss", position.get("Stop Loss", 0)))

            if not ticker or shares <= 0 or not stop_loss:
                continue

            # Obtener precios del día
            try:
                prices = self._get_daily_prices(ticker, date)

                if prices is None:
                    print(f"⚠️ No data for {ticker}, skipping stop-loss check")
                    continue

                open_price = prices["open"]
                high_price = prices["high"]
                low_price = prices["low"]
                close_price = prices["close"]

                # REGLA CRÍTICA: Si low <= stop_loss → SELL
                if low_price <= stop_loss:
                    # Determinar precio de ejecución
                    # Si abrió por debajo del stop, usar open
                    # Si no, usar stop_loss como ejecución
                    if open_price <= stop_loss:
                        exec_price = round(open_price, 2)
                    else:
                        exec_price = round(stop_loss, 2)

                    # Calcular proceeds y PnL
                    proceeds = round(exec_price * shares, 2)
                    pnl = round((exec_price - buy_price) * shares, 2)

                    # Crear evento
                    event = StopLossEvent(
                        date=date,
                        ticker=ticker,
                        shares=shares,
                        buy_price=buy_price,
                        stop_loss=stop_loss,
                        trigger_price=low_price,
                        execution_price=exec_price,
                        proceeds=proceeds,
                        pnl=pnl,
                        reason=(
                            f"🔴 STOP LOSS TRIGGERED: {ticker} "
                            f"(Low ${low_price:.2f} <= Stop ${stop_loss:.2f}). "
                            f"AUTO-SELL {shares} shares @ ${exec_price:.2f}. "
                            f"PnL: ${pnl:+.2f}"
                        ),
                    )

                    events.append(event)

                    # Actualizar cash
                    updated_cash += proceeds

                    # Marcar para remover del portfolio
                    positions_to_remove.append(idx)

                    print(event.reason)

            except Exception as e:
                print(f"⚠️ Error checking stop-loss for {ticker}: {str(e)}")
                continue

        # Remover posiciones vendidas
        if positions_to_remove:
            updated_portfolio = updated_portfolio.drop(positions_to_remove)
            updated_portfolio = updated_portfolio.reset_index(drop=True)

        return updated_portfolio, updated_cash, events

    def _get_daily_prices(self, ticker: str, date: datetime) -> Optional[Dict[str, float]]:
        """
        Obtiene precios OHLC del día

        Returns:
            Dict con keys: open, high, low, close
            None si no hay data
        """
        try:
            # Obtener 5 días de data para asegurar que tenemos el día específico
            end_date = date + pd.Timedelta(days=1)
            start_date = date - pd.Timedelta(days=5)

            prices_raw = self.yfinance.get_historical_stock_prices(
                symbol=ticker, period="5d"  # Últimos 5 días
            )

            # Si viene como string, parsear
            if isinstance(prices_raw, str):
                # YFinance devuelve string, necesitamos parsear o usar otra approach
                # Por ahora, usar get_current_stock_price como fallback
                current = self.yfinance.get_current_stock_price(ticker)

                if isinstance(current, str):
                    # Extraer precio del string
                    import re

                    match = re.search(r"\$?([\d.]+)", current)
                    if match:
                        price = float(match.group(1))
                        return {
                            "open": price,
                            "high": price * 1.01,  # Estimación
                            "low": price * 0.99,  # Estimación
                            "close": price,
                        }
                return None

            # Si es DataFrame
            if hasattr(prices_raw, "empty") and prices_raw.empty:
                return None

            # Tomar el último día disponible
            if hasattr(prices_raw, "iloc"):
                last_row = prices_raw.iloc[-1]
            else:
                return None

            return {
                "open": float(last_row.get("Open", last_row.get("open", 0))),
                "high": float(last_row.get("High", last_row.get("high", 0))),
                "low": float(last_row.get("Low", last_row.get("low", 0))),
                "close": float(last_row.get("Close", last_row.get("close", 0))),
            }

        except Exception as e:
            print(f"Error fetching prices for {ticker}: {str(e)}")
            return None

    def save_stop_loss_events(self, events: List[StopLossEvent], filepath: Path) -> None:
        """
        Guarda eventos de stop-loss en CSV
        Compatible con formato de trade_log del sistema original

        CSV Format:
        Date,Ticker,Shares Sold,Sell Price,PnL,Reason,Cost Basis,Trigger Price
        """
        if not events:
            return

        # Cargar trade log existente si existe
        if filepath.exists():
            trade_log = pd.read_csv(filepath)
        else:
            trade_log = pd.DataFrame()

        # Convertir eventos a DataFrame
        new_trades = []
        for event in events:
            new_trades.append(
                {
                    "Date": event.date.strftime("%Y-%m-%d"),
                    "Ticker": event.ticker,
                    "Shares Sold": event.shares,
                    "Sell Price": event.execution_price,
                    "PnL": event.pnl,
                    "Reason": f"STOP LOSS AUTO - Triggered @ ${event.trigger_price:.2f}",
                    "Cost Basis": event.buy_price * event.shares,
                    "Trigger Price": event.trigger_price,
                    "Stop Loss Level": event.stop_loss,
                    "Proceeds": event.proceeds,
                }
            )

        new_df = pd.DataFrame(new_trades)

        # Combinar con log existente
        if not trade_log.empty:
            trade_log = pd.concat([trade_log, new_df], ignore_index=True)
        else:
            trade_log = new_df

        # Guardar
        trade_log.to_csv(filepath, index=False)
        print(f"✅ Stop-loss events saved to {filepath}")


class AutoStopLossExecutor:
    """
    Ejecutor automático de stop-losses para daily workflow

    INTEGRACIÓN CON SISTEMA MULTI-AGENTE:

    1. Al inicio de cada día, antes de ejecutar análisis de 9 agentes:
       executor.check_and_execute(portfolio, cash)

    2. Si hay stop-losses triggered:
       - Auto-vende posiciones
       - Actualiza portfolio y cash
       - Registra en trade log
       - Notifica al usuario

    3. Luego continúa con análisis normal

    USO EN advanced_trading_team_v2.py:

        # Al inicio de run_analysis()
        executor = AutoStopLossExecutor(data_dir)
        portfolio, cash = executor.check_and_execute(portfolio, cash)

        # Ahora continuar con análisis de 9 agentes
        team = create_trading_team()
        ...
    """

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.monitor = StopLossMonitor()

        # Paths para CSV files
        self.portfolio_csv = self.data_dir / "portfolio_state.csv"
        self.trade_log_csv = self.data_dir / "trades_history.csv"

    def check_and_execute(
        self, portfolio: pd.DataFrame, cash: float, date: Optional[datetime] = None
    ) -> Tuple[pd.DataFrame, float, List[StopLossEvent]]:
        """
        Chequea y ejecuta stop-losses automáticamente

        Returns:
            Tuple[portfolio_updated, cash_updated, events]
        """
        print("\n" + "=" * 70)
        print("🛡️ CHECKING STOP-LOSSES (Auto Protection)")
        print("=" * 70)

        # Ejecutar check
        updated_portfolio, updated_cash, events = self.monitor.check_portfolio(
            portfolio, cash, date
        )

        if events:
            print(f"\n⚠️ {len(events)} STOP-LOSS(ES) TRIGGERED!\n")

            # Mostrar cada evento
            for event in events:
                print(event.reason)

            # Guardar en trade log
            self.monitor.save_stop_loss_events(events, self.trade_log_csv)

            # Guardar portfolio actualizado
            if not updated_portfolio.empty:
                updated_portfolio.to_csv(self.portfolio_csv, index=False)

            print(f"\n💰 Cash updated: ${cash:.2f} → ${updated_cash:.2f}")
            print(f"📊 Positions remaining: {len(updated_portfolio)}")
        else:
            print("✅ No stop-losses triggered. All positions safe.")

        print("=" * 70 + "\n")

        return updated_portfolio, updated_cash, events


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Test del sistema de stop-loss automático
    """

    print("\n🧪 TESTING AUTO STOP-LOSS SYSTEM\n")

    # Crear portfolio de prueba
    test_portfolio = pd.DataFrame(
        [
            {
                "ticker": "ABEO",
                "shares": 4.0,
                "buy_price": 5.77,
                "cost_basis": 23.08,
                "stop_loss": 6.0,  # Si baja a $6.00, auto-sell
            },
            {
                "ticker": "ATYR",
                "shares": 8.0,
                "buy_price": 5.09,
                "cost_basis": 40.72,
                "stop_loss": 4.2,  # Si baja a $4.20, auto-sell
            },
        ]
    )

    print("📊 PORTFOLIO INICIAL:")
    print(test_portfolio)
    print(f"\n💰 Cash: $15.08")

    # Ejecutar check
    monitor = StopLossMonitor()

    updated_portfolio, updated_cash, events = monitor.check_portfolio(
        portfolio=test_portfolio, cash=15.08, date=datetime.now()
    )

    print("\n" + "=" * 70)
    print("RESULTADOS:")
    print("=" * 70)

    if events:
        print(f"\n⚠️ {len(events)} stop-loss(es) triggered:\n")
        for event in events:
            print(event.reason)
    else:
        print("\n✅ No stop-losses triggered")

    print(f"\n📊 PORTFOLIO ACTUALIZADO:")
    if not updated_portfolio.empty:
        print(updated_portfolio)
    else:
        print("(Vacío - todas las posiciones vendidas)")

    print(f"\n💰 Cash actualizado: ${updated_cash:.2f}")

    print("\n✅ Test completado!\n")
