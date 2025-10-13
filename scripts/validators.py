"""
Validadores Críticos para Sistema Multi-Agente
Inspirados en las reglas probadas del sistema original (trading_script.py)

CRITICAL VALIDATORS:
1. Micro-Cap Validation (<$300M market cap)
2. Position Sizing Rules (max 20% per stock, 40% per sector)
3. Cash Reserve Requirements (min 20%)
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from agno.tools.yfinance import YFinanceTools


@dataclass
class ValidationResult:
    """Resultado de validación"""
    valid: bool
    reason: str
    alternative: Optional[str] = None
    severity: str = "ERROR"  # ERROR, WARNING, INFO


class MicroCapValidator:
    """
    Valida que los tickers cumplan con la regla micro-cap (<$300M)
    
    REGLA ORIGINAL (Prompts.md):
    "U.S. micro-cap stocks (market cap under $300M)"
    
    EJEMPLO VIOLACIÓN:
    - NVDA = $4.46 TRILLONES → RECHAZADO ❌
    - ABEO = $50M → ACEPTADO ✅
    """
    
    MICRO_CAP_LIMIT = 300_000_000  # $300 millones
    
    def __init__(self):
        self.yfinance = YFinanceTools()
    
    def validate(self, ticker: str) -> ValidationResult:
        """
        Valida si el ticker es micro-cap
        
        Returns:
            ValidationResult con valid=True si market cap < $300M
        """
        try:
            # Obtener info de la empresa (puede venir como dict o string)
            info_raw = self.yfinance.get_company_info(ticker)
            
            # Si viene como string, parsear como texto
            if isinstance(info_raw, str):
                # Buscar market cap en el texto
                market_cap = self._extract_market_cap_from_text(info_raw)
            else:
                # Si es dict, obtener directamente
                market_cap_str = info_raw.get("market_cap", "")
                market_cap = self._parse_market_cap(market_cap_str)
            
            if market_cap is None:
                return ValidationResult(
                    valid=False,
                    reason=f"No se pudo obtener market cap para {ticker}",
                    severity="ERROR"
                )
            
            # Validar límite
            if market_cap > self.MICRO_CAP_LIMIT:
                market_cap_display = self._format_market_cap(market_cap)
                
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"❌ RECHAZADO: {ticker} tiene market cap de {market_cap_display}, "
                        f"excede el límite de $300M para micro-cap. "
                        f"Este ticker NO cumple con las reglas del experimento."
                    ),
                    alternative=f"Buscar alternativas micro-cap en el mismo sector",
                    severity="ERROR"
                )
            
            # ACEPTADO
            market_cap_display = self._format_market_cap(market_cap)
            return ValidationResult(
                valid=True,
                reason=f"✅ VÁLIDO: {ticker} market cap {market_cap_display} < $300M",
                severity="INFO"
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                reason=f"Error al validar {ticker}: {str(e)}",
                severity="ERROR"
            )
    
    def _parse_market_cap(self, market_cap_str: str) -> Optional[float]:
        """
        Parsea market cap de diferentes formatos:
        - "$4.46T" → 4_460_000_000_000
        - "300M" → 300_000_000
        - "1.5B" → 1_500_000_000
        """
        if not market_cap_str or market_cap_str == "N/A":
            return None
        
        # Remover $, espacios, comas
        clean = str(market_cap_str).replace("$", "").replace(",", "").replace(" ", "").upper()
        
        # Extraer número y sufijo
        multipliers = {
            "T": 1_000_000_000_000,  # Trillion
            "B": 1_000_000_000,       # Billion
            "M": 1_000_000,           # Million
            "K": 1_000                # Thousand
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in clean:
                number_str = clean.replace(suffix, "")
                try:
                    number = float(number_str)
                    return number * multiplier
                except ValueError:
                    continue
        
        # Si no hay sufijo, intentar parsear directamente
        try:
            return float(clean)
        except ValueError:
            return None
    
    def _format_market_cap(self, market_cap: float) -> str:
        """Formatea market cap para display"""
        if market_cap >= 1_000_000_000_000:
            return f"${market_cap / 1_000_000_000_000:.2f}T"
        elif market_cap >= 1_000_000_000:
            return f"${market_cap / 1_000_000_000:.2f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap / 1_000_000:.2f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def _extract_market_cap_from_text(self, text: str) -> Optional[float]:
        """
        Extrae market cap de texto descriptivo de YFinance
        
        Busca patrones como:
        - "Market Cap: $4.46T"
        - "marketCap: 300000000"
        - etc.
        """
        import re
        
        # Buscar patrón "Market Cap: $X.XXT"
        pattern1 = r'[Mm]arket\s*[Cc]ap[:\s]+\$?([\d.]+)\s*([TBMK])?'
        match = re.search(pattern1, text)
        
        if match:
            number = float(match.group(1))
            suffix = match.group(2)
            
            if suffix:
                multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
                return number * multipliers.get(suffix.upper(), 1)
            return number
        
        # Buscar patrón numérico directo "marketCap: 123456789"
        pattern2 = r'[Mm]arket[Cc]ap[:\s]+(\d+)'
        match = re.search(pattern2, text)
        
        if match:
            return float(match.group(1))
        
        return None


class PositionSizingValidator:
    """
    Valida reglas de position sizing del sistema original
    
    REGLAS ORIGINALES:
    1. Max 20-30% en single stock
    2. Max 40% en single sector
    3. Min 20% cash reserve
    
    FUENTE: trading_script.py + Prompts.md
    """
    
    MAX_SINGLE_POSITION_PCT = 0.20  # 20% max
    MAX_SECTOR_EXPOSURE_PCT = 0.40  # 40% max
    MIN_CASH_RESERVE_PCT = 0.20     # 20% min
    
    def __init__(self):
        self.yfinance = YFinanceTools()
    
    def _extract_sector_from_text(self, text: str) -> str:
        """
        Extrae sector de texto descriptivo de YFinance
        
        Busca patrones como:
        - "Sector: Technology"
        - "sector: Healthcare"
        """
        import re
        
        pattern = r'[Ss]ector[:\s]+([A-Za-z\s]+)'
        match = re.search(pattern, text)
        
        if match:
            return match.group(1).strip()
        
        return "Unknown"
    
    def validate_position_size(
        self,
        ticker: str,
        position_value: float,
        total_equity: float
    ) -> ValidationResult:
        """
        Valida que la posición no exceda 20% del portfolio
        
        Args:
            ticker: Ticker a comprar
            position_value: Valor de la posición propuesta
            total_equity: Equity total del portfolio
        
        Returns:
            ValidationResult
        """
        position_pct = position_value / total_equity if total_equity > 0 else 0
        
        if position_pct > self.MAX_SINGLE_POSITION_PCT:
            max_allowed = total_equity * self.MAX_SINGLE_POSITION_PCT
            
            return ValidationResult(
                valid=False,
                reason=(
                    f"❌ POSICIÓN EXCESIVA: {ticker} = {position_pct*100:.1f}% del portfolio "
                    f"(máximo {self.MAX_SINGLE_POSITION_PCT*100:.0f}%). "
                    f"Valor máximo permitido: ${max_allowed:.2f}"
                ),
                alternative=f"Reducir posición a ${max_allowed:.2f}",
                severity="ERROR"
            )
        
        return ValidationResult(
            valid=True,
            reason=f"✅ Posición {ticker} = {position_pct*100:.1f}% (dentro del límite)",
            severity="INFO"
        )
    
    def validate_sector_exposure(
        self,
        ticker: str,
        position_value: float,
        current_portfolio: pd.DataFrame,
        total_equity: float
    ) -> ValidationResult:
        """
        Valida que el sector no exceda 40% del portfolio
        
        Args:
            ticker: Nuevo ticker a comprar
            position_value: Valor de nueva posición
            current_portfolio: Portfolio actual (DataFrame)
            total_equity: Equity total
        
        Returns:
            ValidationResult
        """
        try:
            # Obtener sector del nuevo ticker
            new_ticker_info = self.yfinance.get_company_info(ticker)
            
            # Parsear sector (puede ser dict o string)
            if isinstance(new_ticker_info, str):
                new_sector = self._extract_sector_from_text(new_ticker_info)
            else:
                new_sector = new_ticker_info.get("sector", "Unknown")
            
            # Calcular exposición actual del sector
            sector_exposure = position_value  # Nueva posición
            
            if not current_portfolio.empty:
                for _, position in current_portfolio.iterrows():
                    pos_ticker = position.get("ticker", position.get("Ticker", ""))
                    pos_value = position.get("total_value", position.get("Total Value", 0))
                    
                    if pos_ticker:
                        pos_info = self.yfinance.get_company_info(pos_ticker)
                        
                        # Parsear sector
                        if isinstance(pos_info, str):
                            pos_sector = self._extract_sector_from_text(pos_info)
                        else:
                            pos_sector = pos_info.get("sector", "Unknown")
                        
                        if pos_sector == new_sector:
                            sector_exposure += float(pos_value)
            
            sector_pct = sector_exposure / total_equity if total_equity > 0 else 0
            
            if sector_pct > self.MAX_SECTOR_EXPOSURE_PCT:
                max_allowed = total_equity * self.MAX_SECTOR_EXPOSURE_PCT
                
                return ValidationResult(
                    valid=False,
                    reason=(
                        f"❌ CONCENTRACIÓN SECTORIAL: Sector '{new_sector}' = "
                        f"{sector_pct*100:.1f}% del portfolio "
                        f"(máximo {self.MAX_SECTOR_EXPOSURE_PCT*100:.0f}%). "
                        f"Valor máximo permitido: ${max_allowed:.2f}"
                    ),
                    alternative=f"Diversificar en otros sectores o reducir posición",
                    severity="ERROR"
                )
            
            return ValidationResult(
                valid=True,
                reason=f"✅ Sector '{new_sector}' = {sector_pct*100:.1f}% (dentro del límite)",
                severity="INFO"
            )
            
        except Exception as e:
            # Si no se puede validar sector, permitir pero advertir
            return ValidationResult(
                valid=True,
                reason=f"⚠️ No se pudo validar sector: {str(e)}",
                severity="WARNING"
            )
    
    def validate_cash_reserve(
        self,
        cash_after_trade: float,
        total_equity: float
    ) -> ValidationResult:
        """
        Valida que quede al menos 20% cash después del trade
        
        Args:
            cash_after_trade: Cash disponible después de ejecutar trade
            total_equity: Equity total del portfolio
        
        Returns:
            ValidationResult
        """
        cash_pct = cash_after_trade / total_equity if total_equity > 0 else 0
        
        if cash_pct < self.MIN_CASH_RESERVE_PCT:
            min_required = total_equity * self.MIN_CASH_RESERVE_PCT
            
            return ValidationResult(
                valid=False,
                reason=(
                    f"❌ CASH RESERVE INSUFICIENTE: Quedaría {cash_pct*100:.1f}% cash "
                    f"(mínimo {self.MIN_CASH_RESERVE_PCT*100:.0f}%). "
                    f"Se requieren al menos ${min_required:.2f} en cash."
                ),
                alternative=f"Reducir tamaño de posición para mantener ${min_required:.2f} cash",
                severity="ERROR"
            )
        
        return ValidationResult(
            valid=True,
            reason=f"✅ Cash reserve {cash_pct*100:.1f}% (suficiente)",
            severity="INFO"
        )


class TradeValidator:
    """
    Validador completo que combina todas las reglas críticas
    
    USO:
        validator = TradeValidator()
        result = validator.validate_trade(
            ticker="NVDA",
            position_value=15.0,
            cash=100.0,
            portfolio=pd.DataFrame(),
            total_equity=100.0
        )
        
        if not result.valid:
            print(result.reason)
            print(result.alternative)
    """
    
    def __init__(self):
        self.micro_cap = MicroCapValidator()
        self.position_sizing = PositionSizingValidator()
    
    def validate_trade(
        self,
        ticker: str,
        position_value: float,
        cash: float,
        portfolio: pd.DataFrame,
        total_equity: float
    ) -> Dict[str, ValidationResult]:
        """
        Ejecuta TODAS las validaciones críticas
        
        Returns:
            Dict con resultados de cada validación:
            {
                "micro_cap": ValidationResult,
                "position_size": ValidationResult,
                "sector_exposure": ValidationResult,
                "cash_reserve": ValidationResult,
                "overall": ValidationResult  # Resultado final
            }
        """
        results = {}
        
        # 1. Validar micro-cap
        results["micro_cap"] = self.micro_cap.validate(ticker)
        
        # 2. Validar tamaño de posición
        results["position_size"] = self.position_sizing.validate_position_size(
            ticker, position_value, total_equity
        )
        
        # 3. Validar exposición sectorial
        results["sector_exposure"] = self.position_sizing.validate_sector_exposure(
            ticker, position_value, portfolio, total_equity
        )
        
        # 4. Validar cash reserve
        cash_after = cash - position_value
        results["cash_reserve"] = self.position_sizing.validate_cash_reserve(
            cash_after, total_equity
        )
        
        # 5. Resultado general
        all_valid = all(r.valid for r in results.values())
        errors = [r.reason for r in results.values() if not r.valid]
        warnings = [r.reason for r in results.values() if r.valid and r.severity == "WARNING"]
        
        if all_valid:
            results["overall"] = ValidationResult(
                valid=True,
                reason="✅ TODAS LAS VALIDACIONES PASARON",
                severity="INFO"
            )
        else:
            results["overall"] = ValidationResult(
                valid=False,
                reason=f"❌ VALIDACIÓN FALLÓ:\n" + "\n".join(errors),
                alternative="Revisar reglas de position sizing y micro-cap",
                severity="ERROR"
            )
        
        return results
    
    def format_validation_report(self, results: Dict[str, ValidationResult]) -> str:
        """
        Formatea resultados de validación para display
        
        Returns:
            String con reporte formateado
        """
        report = []
        report.append("\n" + "="*70)
        report.append("VALIDACIÓN DE TRADE - REGLAS CRÍTICAS")
        report.append("="*70)
        
        # Mostrar cada validación
        for name, result in results.items():
            if name == "overall":
                continue
            
            icon = "✅" if result.valid else "❌"
            severity_icon = {
                "ERROR": "🔴",
                "WARNING": "⚠️",
                "INFO": "ℹ️"
            }.get(result.severity, "")
            
            report.append(f"\n{icon} {severity_icon} {name.upper().replace('_', ' ')}:")
            report.append(f"   {result.reason}")
            
            if result.alternative:
                report.append(f"   💡 Alternativa: {result.alternative}")
        
        # Resultado final
        report.append("\n" + "-"*70)
        overall = results.get("overall")
        if overall:
            report.append(overall.reason)
        
        report.append("="*70 + "\n")
        
        return "\n".join(report)


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Test de validadores con casos del sistema original
    """
    
    print("\n🧪 TESTING VALIDATORS\n")
    
    validator = TradeValidator()
    
    # TEST 1: NVDA (VIOLACIÓN MICRO-CAP)
    print("\n📊 TEST 1: NVDA (Large Cap - Debe RECHAZAR)")
    print("-" * 70)
    results = validator.validate_trade(
        ticker="NVDA",
        position_value=15.0,
        cash=100.0,
        portfolio=pd.DataFrame(),
        total_equity=100.0
    )
    print(validator.format_validation_report(results))
    
    # TEST 2: ABEO (MICRO-CAP VÁLIDO del portfolio original)
    print("\n📊 TEST 2: ABEO (Micro Cap - Debe ACEPTAR)")
    print("-" * 70)
    results = validator.validate_trade(
        ticker="ABEO",
        position_value=20.0,
        cash=100.0,
        portfolio=pd.DataFrame(),
        total_equity=100.0
    )
    print(validator.format_validation_report(results))
    
    # TEST 3: Posición muy grande (>20%)
    print("\n📊 TEST 3: Posición 90% del portfolio (Debe RECHAZAR)")
    print("-" * 70)
    results = validator.validate_trade(
        ticker="ABEO",
        position_value=90.0,
        cash=100.0,
        portfolio=pd.DataFrame(),
        total_equity=100.0
    )
    print(validator.format_validation_report(results))
    
    # TEST 4: Cash reserve insuficiente
    print("\n📊 TEST 4: Cash reserve <20% (Debe RECHAZAR)")
    print("-" * 70)
    results = validator.validate_trade(
        ticker="ABEO",
        position_value=85.0,  # Dejaría solo $15 cash = 15%
        cash=100.0,
        portfolio=pd.DataFrame(),
        total_equity=100.0
    )
    print(validator.format_validation_report(results))
    
    print("\n✅ Tests completados!\n")
