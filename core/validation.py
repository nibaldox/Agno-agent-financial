"""
Validation Handler - Centralized validation logic

Handles:
- Micro-cap validation
- Position sizing checks
- Live vs dry-run modes
- Validation result formatting
"""

from typing import Optional, Dict, Any


class ValidationHandler:
    """
    Handles all trade validation logic with intelligent dry-run support.
    
    Features:
    - Micro-cap validation
    - Position sizing validation
    - Sector exposure checks
    - Cash reserve validation
    - Mode-aware validation (dry-run vs live)
    
    Example:
        >>> handler = ValidationHandler()
        >>> result = handler.validate_stock("ABEO", dry_run=True)
        >>> if result['valid'] or result['can_continue']:
        >>>     # Proceed with analysis
        >>>     pass
    """
    
    def __init__(self, validators_available: bool = True):
        """
        Initialize validation handler.
        
        Args:
            validators_available: Whether critical validators are loaded
        """
        self.validators_available = validators_available
        self.validator = None
        
        if validators_available:
            try:
                from validators import TradeValidator
                self.validator = TradeValidator()
            except ImportError:
                self.validators_available = False
    
    def validate_stock(
        self, 
        ticker: str, 
        dry_run: bool = True,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Validate stock for trading with mode-aware logic.
        
        Args:
            ticker: Stock symbol to validate
            dry_run: If True, shows warnings but allows continuation
            verbose: If True, prints validation messages
            
        Returns:
            dict: Validation result with keys:
                - valid: bool - Full validation passed
                - can_continue: bool - Can proceed (warning in dry-run, or full pass)
                - reason: str - Validation message
                - mode: str - 'DRY-RUN' or 'LIVE'
        """
        if not self.validators_available:
            return {
                'valid': False,
                'can_continue': dry_run,  # Allow in dry-run only
                'reason': "⚠️ Validators not available",
                'mode': 'DRY-RUN' if dry_run else 'LIVE'
            }
        
        # Run micro-cap validation
        micro_cap_result = self.validator.micro_cap.validate(ticker)
        
        if not micro_cap_result.valid:
            # Validation failed
            if dry_run:
                # Dry-run mode: Show warning but allow continuation
                if verbose:
                    print(f"\n⚠️ WARNING (DRY-RUN): {micro_cap_result.reason}")
                    if micro_cap_result.alternative:
                        print(f"💡 Alternativa: {micro_cap_result.alternative}")
                    print("🧪 Continuando análisis en modo simulación...\n")
                
                return {
                    'valid': False,
                    'can_continue': True,
                    'reason': micro_cap_result.reason,
                    'alternative': micro_cap_result.alternative,
                    'mode': 'DRY-RUN'
                }
            else:
                # Live mode: Block operation
                if verbose:
                    print(f"\n❌ VALIDACIÓN FALLIDA: {micro_cap_result.reason}")
                    if micro_cap_result.alternative:
                        print(f"💡 Alternativa: {micro_cap_result.alternative}")
                
                return {
                    'valid': False,
                    'can_continue': False,
                    'reason': micro_cap_result.reason,
                    'alternative': micro_cap_result.alternative,
                    'mode': 'LIVE'
                }
        else:
            # Validation passed
            if verbose:
                print(f"✅ Validación micro-cap: {ticker} aprobado\n")
            
            return {
                'valid': True,
                'can_continue': True,
                'reason': f"{ticker} passed micro-cap validation",
                'mode': 'DRY-RUN' if dry_run else 'LIVE'
            }
    
    def validate_position_size(
        self,
        ticker: str,
        position_value: float,
        total_equity: float,
        max_position_pct: float = 0.30
    ) -> Dict[str, Any]:
        """
        Validate position size doesn't exceed limits.
        
        Args:
            ticker: Stock symbol
            position_value: Proposed position value in dollars
            total_equity: Total portfolio equity
            max_position_pct: Maximum position as % of equity (default: 30%)
            
        Returns:
            dict: Validation result
        """
        if not self.validators_available or not self.validator:
            return {'valid': True, 'reason': 'Validator not available'}
        
        result = self.validator.position_sizing.validate_position_size(
            ticker, position_value, total_equity
        )
        
        return {
            'valid': result.valid,
            'reason': result.reason,
            'alternative': result.alternative if hasattr(result, 'alternative') else None
        }
    
    def validate_cash_reserve(
        self,
        cash_after_trade: float,
        total_equity: float,
        min_reserve_pct: float = 0.20
    ) -> Dict[str, Any]:
        """
        Validate minimum cash reserve is maintained.
        
        Args:
            cash_after_trade: Cash remaining after proposed trade
            total_equity: Total portfolio equity
            min_reserve_pct: Minimum cash as % of equity (default: 20%)
            
        Returns:
            dict: Validation result
        """
        if not self.validators_available or not self.validator:
            return {'valid': True, 'reason': 'Validator not available'}
        
        result = self.validator.position_sizing.validate_cash_reserve(
            cash_after_trade, total_equity
        )
        
        return {
            'valid': result.valid,
            'reason': result.reason,
            'alternative': result.alternative if hasattr(result, 'alternative') else None
        }
    
    def validate_full_trade(
        self,
        ticker: str,
        position_value: float,
        cash: float,
        portfolio_df,
        total_equity: float,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete trade validation suite.
        
        Args:
            ticker: Stock symbol
            position_value: Proposed position value
            cash: Available cash
            portfolio_df: Current portfolio DataFrame
            total_equity: Total portfolio equity
            dry_run: Dry-run mode flag
            
        Returns:
            dict: Comprehensive validation results
        """
        if not self.validators_available or not self.validator:
            return {
                'valid': False,
                'can_continue': dry_run,
                'reason': 'Validators not available',
                'mode': 'DRY-RUN' if dry_run else 'LIVE'
            }
        
        # Run full validation
        results = self.validator.validate_trade(
            ticker=ticker,
            position_value=position_value,
            cash=cash,
            portfolio=portfolio_df,
            total_equity=total_equity
        )
        
        # Check overall result
        overall = results.get('overall')
        
        if overall and overall.valid:
            return {
                'valid': True,
                'can_continue': True,
                'reason': overall.reason,
                'details': results,
                'mode': 'DRY-RUN' if dry_run else 'LIVE'
            }
        else:
            # Some validations failed
            if dry_run:
                return {
                    'valid': False,
                    'can_continue': True,
                    'reason': overall.reason if overall else 'Validation failed',
                    'details': results,
                    'mode': 'DRY-RUN'
                }
            else:
                return {
                    'valid': False,
                    'can_continue': False,
                    'reason': overall.reason if overall else 'Validation failed',
                    'details': results,
                    'mode': 'LIVE'
                }
