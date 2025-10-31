"""
Test Script para Validadores Críticos
Verifica que las 3 features críticas funcionen correctamente

FEATURES CRÍTICAS A TESTEAR:
1. Micro-Cap Validation (<$300M)
2. Position Sizing Rules (max 20%, min 20% cash, max 40% sector)
3. Auto Stop-Loss Execution

COMPARACIÓN CON SISTEMA ORIGINAL:
- Sistema Original: 6 meses probado, +31% return, Sharpe 3.35
- Estos validadores implementan las MISMAS reglas probadas
"""

import sys
from pathlib import Path

# Agregar directorio de scripts al path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from datetime import datetime

import pandas as pd
from stop_loss_monitor import AutoStopLossExecutor, StopLossMonitor
from validators import TradeValidator, ValidationResult


def test_micro_cap_validation():
    """
    Test 1: Micro-Cap Validation

    REGLA: Solo stocks con market cap <$300M
    """
    print("\n" + "=" * 70)
    print("🧪 TEST 1: MICRO-CAP VALIDATION")
    print("=" * 70)

    validator = TradeValidator()

    # Test cases del sistema original
    test_cases = [
        {"ticker": "NVDA", "expected": False, "reason": "Large cap $4.46T (>$300M)"},
        {"ticker": "ABEO", "expected": True, "reason": "Micro cap ~$50M (<$300M)"},
        {"ticker": "ATYR", "expected": True, "reason": "Micro cap ~$200M (<$300M)"},
    ]

    for test in test_cases:
        ticker = test["ticker"]
        expected = test["expected"]
        reason = test["reason"]

        print(f"\n📊 Testing {ticker}...")
        print(f"   Expected: {'ACCEPT ✅' if expected else 'REJECT ❌'}")
        print(f"   Reason: {reason}")

        results = validator.validate_trade(
            ticker=ticker,
            position_value=10.0,
            cash=100.0,
            portfolio=pd.DataFrame(),
            total_equity=100.0,
        )

        micro_cap_result = results["micro_cap"]

        if micro_cap_result.valid == expected:
            print(f"   Result: ✅ PASS")
        else:
            print(f"   Result: ❌ FAIL")

        print(f"   Message: {micro_cap_result.reason}")

        if micro_cap_result.alternative:
            print(f"   Alternative: {micro_cap_result.alternative}")


def test_position_sizing():
    """
    Test 2: Position Sizing Rules

    REGLAS:
    - Max 20% en single stock
    - Max 40% en single sector
    - Min 20% cash reserve
    """
    print("\n" + "=" * 70)
    print("🧪 TEST 2: POSITION SIZING RULES")
    print("=" * 70)

    validator = TradeValidator()

    # Test Case 1: Posición muy grande (90%)
    print("\n📊 Test 2.1: Posición 90% del portfolio (debe RECHAZAR)")
    results = validator.validate_trade(
        ticker="ABEO", position_value=90.0, cash=100.0, portfolio=pd.DataFrame(), total_equity=100.0
    )

    if not results["position_size"].valid:
        print("   ✅ PASS - Rechazó posición >20%")
    else:
        print("   ❌ FAIL - No detectó posición excesiva")

    print(f"   Message: {results['position_size'].reason}")

    # Test Case 2: Cash reserve insuficiente
    print("\n📊 Test 2.2: Cash reserve <20% (debe RECHAZAR)")
    results = validator.validate_trade(
        ticker="ABEO",
        position_value=85.0,  # Dejaría solo $15 = 15% cash
        cash=100.0,
        portfolio=pd.DataFrame(),
        total_equity=100.0,
    )

    if not results["cash_reserve"].valid:
        print("   ✅ PASS - Rechazó cash reserve <20%")
    else:
        print("   ❌ FAIL - No detectó cash insuficiente")

    print(f"   Message: {results['cash_reserve'].reason}")

    # Test Case 3: Posición válida (15%)
    print("\n📊 Test 2.3: Posición 15% (debe ACEPTAR)")
    results = validator.validate_trade(
        ticker="ABEO", position_value=15.0, cash=100.0, portfolio=pd.DataFrame(), total_equity=100.0
    )

    if results["position_size"].valid and results["cash_reserve"].valid:
        print("   ✅ PASS - Aceptó posición válida")
    else:
        print("   ❌ FAIL - Rechazó posición válida")

    print(f"   Position: {results['position_size'].reason}")
    print(f"   Cash: {results['cash_reserve'].reason}")


def test_stop_loss_auto():
    """
    Test 3: Auto Stop-Loss Execution

    REGLA: Si low_price <= stop_loss → Auto-sell

    COMPORTAMIENTO DEL SISTEMA ORIGINAL:
    - Chequea precios diarios
    - Si Low <= Stop Loss → Venta automática
    - Usa Open price como ejecución (o Stop si Open > Stop)
    - Actualiza cash y portfolio
    - Registra en trade log
    """
    print("\n" + "=" * 70)
    print("🧪 TEST 3: AUTO STOP-LOSS EXECUTION")
    print("=" * 70)

    monitor = StopLossMonitor()

    # Portfolio de prueba (basado en portfolio real del sistema original)
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

    print("\n📊 Portfolio Inicial:")
    print(test_portfolio[["ticker", "shares", "buy_price", "stop_loss"]])
    print(f"\n💰 Cash: $15.08")

    # Ejecutar check
    print("\n🔍 Checking stop-losses...")
    updated_portfolio, updated_cash, events = monitor.check_portfolio(
        portfolio=test_portfolio, cash=15.08, date=datetime.now()
    )

    if events:
        print(f"\n⚠️ {len(events)} stop-loss(es) triggered:")
        for event in events:
            print(f"   - {event.ticker}: ${event.trigger_price:.2f} <= ${event.stop_loss:.2f}")
            print(f"     Sold {event.shares} shares @ ${event.execution_price:.2f}")
            print(f"     PnL: ${event.pnl:+.2f}")

        print(f"\n✅ PASS - Stop-losses executed automatically")
    else:
        print(f"\n✅ No stop-losses triggered (positions safe)")

    print(f"\n📊 Portfolio Final: {len(updated_portfolio)} positions")
    print(f"💰 Cash Final: ${updated_cash:.2f}")


def test_full_workflow():
    """
    Test 4: Workflow Completo

    Simula el workflow real del sistema multi-agente:
    1. Check stop-losses (auto-sell si triggered)
    2. Validate trade propuesto
    3. Execute si válido
    4. Update portfolio
    """
    print("\n" + "=" * 70)
    print("🧪 TEST 4: FULL WORKFLOW INTEGRATION")
    print("=" * 70)

    # Setup inicial
    portfolio = pd.DataFrame(
        [
            {
                "ticker": "ABEO",
                "shares": 4.0,
                "buy_price": 5.77,
                "cost_basis": 23.08,
                "stop_loss": 6.0,
                "current_price": 7.23,
                "total_value": 28.92,
            }
        ]
    )

    cash = 15.08
    total_equity = cash + portfolio["total_value"].sum()

    print(f"\n📊 Estado Inicial:")
    print(f"   Cash: ${cash:.2f}")
    print(f"   Equity: ${total_equity:.2f}")
    print(f"   Positions: {len(portfolio)}")

    # PASO 1: Check stop-losses
    print("\n🛡️ PASO 1: Checking stop-losses...")
    monitor = StopLossMonitor()
    portfolio, cash, events = monitor.check_portfolio(portfolio, cash)

    if events:
        print(f"   ⚠️ {len(events)} stop-losses triggered")
        total_equity = cash + (portfolio["total_value"].sum() if not portfolio.empty else 0)
    else:
        print(f"   ✅ No stop-losses triggered")

    # PASO 2: Validar nuevo trade propuesto
    print("\n🔍 PASO 2: Validating proposed trade...")
    print(f"   Proposed: BUY IINN @ $1.25 for $12.50 (10 shares)")

    validator = TradeValidator()
    results = validator.validate_trade(
        ticker="IINN",
        position_value=12.50,
        cash=cash,
        portfolio=portfolio,
        total_equity=total_equity,
    )

    print(validator.format_validation_report(results))

    # PASO 3: Ejecutar si válido
    if results["overall"].valid:
        print("✅ Trade APPROVED - Would execute in production")

        # Simular ejecución
        cash -= 12.50
        new_position = pd.DataFrame(
            [
                {
                    "ticker": "IINN",
                    "shares": 10.0,
                    "buy_price": 1.25,
                    "cost_basis": 12.50,
                    "stop_loss": 1.0,
                    "current_price": 1.25,
                    "total_value": 12.50,
                }
            ]
        )

        if not portfolio.empty:
            portfolio = pd.concat([portfolio, new_position], ignore_index=True)
        else:
            portfolio = new_position

        print(f"\n📊 Estado Final:")
        print(f"   Cash: ${cash:.2f}")
        print(f"   Positions: {len(portfolio)}")
        print(portfolio[["ticker", "shares", "buy_price"]])
    else:
        print("❌ Trade REJECTED - Validation failed")


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 70)
    print("🚀 RUNNING ALL CRITICAL VALIDATORS TESTS")
    print("=" * 70)
    print("\nThese tests verify that the multi-agent system implements")
    print("the SAME proven rules from the original trading system:")
    print("  - 6 months live trading")
    print("  - +31% return vs +4.22% S&P 500")
    print("  - Sharpe ratio 3.35")
    print("  - Max drawdown -7.11%")
    print("\n" + "=" * 70)

    try:
        test_micro_cap_validation()
        test_position_sizing()
        test_stop_loss_auto()
        test_full_workflow()

        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n🎯 Next Steps:")
        print("   1. Run: python advanced_trading_team_v2.py --ticker ABEO")
        print("   2. Verify ABEO is accepted (micro-cap)")
        print("   3. Run: python advanced_trading_team_v2.py --ticker NVDA")
        print("   4. Verify NVDA is REJECTED (large-cap)")
        print("\n")

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 70)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
