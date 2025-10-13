"""
Professional HTML Report Generator

Generates comprehensive trading reports with:
- Executive summary
- Performance metrics (Sharpe, Sortino, Alpha, Beta)
- Embedded charts and visualizations
- Trade history tables
- Risk analysis
- Professional CSS styling

All charts are embedded as base64 images for standalone HTML files.
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import base64
import pandas as pd
import warnings


class HTMLReportGenerator:
    """
    Generate professional HTML reports with embedded charts.
    
    Features:
    - Executive summary with key metrics
    - Performance analysis section
    - Risk metrics dashboard
    - Trade history tables
    - Embedded charts (base64)
    - Responsive CSS styling
    - Print-friendly layout
    
    Example:
        >>> reporter = HTMLReportGenerator()
        >>> reporter.generate_full_report(
        ...     metrics=metrics_dict,
        ...     chart_paths={'perf': 'performance.png'},
        ...     output_path='report.html'
        ... )
    """
    
    def __init__(self):
        """Initialize HTML report generator."""
        self.css_style = self._get_css_styles()
    
    def _get_css_styles(self) -> str:
        """
        Get professional CSS styles for the report with dark mode support.
        
        Returns:
            str: CSS stylesheet
        """
        return """
        <style>
            :root {
                /* Light mode colors */
                --bg-primary: #f5f5f5;
                --bg-secondary: #ffffff;
                --bg-card: #f8f9fa;
                --text-primary: #333333;
                --text-secondary: #666666;
                --border-color: #ecf0f1;
                --accent-color: #1f77b4;
                --success-color: #2ca02c;
                --danger-color: #d62728;
                --warning-color: #ff9800;
                --shadow: rgba(0, 0, 0, 0.1);
                --shadow-hover: rgba(0, 0, 0, 0.15);
            }
            
            /* Dark mode via data-theme attribute (manual toggle) */
            [data-theme="dark"] {
                --bg-primary: #1a1a1a;
                --bg-secondary: #2d2d2d;
                --bg-card: #3a3a3a;
                --text-primary: #e0e0e0;
                --text-secondary: #b0b0b0;
                --border-color: #4a4a4a;
                --accent-color: #4a9eff;
                --success-color: #4ecb71;
                --danger-color: #ff6b6b;
                --warning-color: #ffa726;
                --shadow: rgba(0, 0, 0, 0.3);
                --shadow-hover: rgba(0, 0, 0, 0.5);
            }
            
            /* Fallback for system preference (when no manual selection) */
            @media (prefers-color-scheme: dark) {
                :root:not([data-theme]) {
                    --bg-primary: #1a1a1a;
                    --bg-secondary: #2d2d2d;
                    --bg-card: #3a3a3a;
                    --text-primary: #e0e0e0;
                    --text-secondary: #b0b0b0;
                    --border-color: #4a4a4a;
                    --accent-color: #4a9eff;
                    --success-color: #4ecb71;
                    --danger-color: #ff6b6b;
                    --warning-color: #ffa726;
                    --shadow: rgba(0, 0, 0, 0.3);
                    --shadow-hover: rgba(0, 0, 0, 0.5);
                }
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                line-height: 1.6;
                color: var(--text-primary);
                background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
                padding: 20px;
                transition: background-color 0.3s ease, color 0.3s ease;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background-color: var(--bg-secondary);
                padding: 40px;
                box-shadow: 0 8px 32px var(--shadow);
                border-radius: 16px;
                transition: all 0.3s ease;
                animation: fadeIn 0.5s ease-in;
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .header {
                border-bottom: 3px solid var(--accent-color);
                padding-bottom: 20px;
                margin-bottom: 30px;
                background: linear-gradient(90deg, var(--accent-color) 0%, transparent 100%);
                background-size: 100% 3px;
                background-repeat: no-repeat;
                background-position: bottom;
            }
            
            h1 {
                color: var(--text-primary);
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 700;
                letter-spacing: -0.5px;
                animation: slideInLeft 0.6s ease;
            }
            
            @keyframes slideInLeft {
                from {
                    opacity: 0;
                    transform: translateX(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            .subtitle {
                color: var(--text-secondary);
                font-size: 1rem;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .subtitle::before {
                content: "📅";
                font-size: 1.2rem;
            }
            
            .section {
                margin-bottom: 50px;
                animation: fadeInUp 0.6s ease;
                animation-fill-mode: both;
            }
            
            .section:nth-child(2) { animation-delay: 0.1s; }
            .section:nth-child(3) { animation-delay: 0.2s; }
            .section:nth-child(4) { animation-delay: 0.3s; }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            h2 {
                color: var(--text-primary);
                font-size: 1.8rem;
                margin-bottom: 24px;
                padding-bottom: 12px;
                border-bottom: 2px solid var(--border-color);
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: 600;
            }
            
            h3 {
                color: var(--text-primary);
                font-size: 1.3rem;
                margin-top: 28px;
                margin-bottom: 18px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 24px;
                margin-bottom: 30px;
            }
            
            .metric-card {
                background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
                padding: 24px;
                border-radius: 12px;
                border-left: 4px solid var(--accent-color);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, transparent 0%, var(--accent-color) 100%);
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-4px) scale(1.02);
                box-shadow: 0 12px 24px var(--shadow-hover);
            }
            
            .metric-card:hover::before {
                opacity: 0.05;
            }
            
            .metric-label {
                font-size: 0.85rem;
                color: var(--text-secondary);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
                font-weight: 600;
                position: relative;
                z-index: 1;
            }
            
            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                color: var(--accent-color);
                margin-bottom: 4px;
                position: relative;
                z-index: 1;
                font-variant-numeric: tabular-nums;
            }
            
            .metric-value.positive {
                color: var(--success-color);
            }
            
            .metric-value.negative {
                color: var(--danger-color);
            }
            
            .metric-change {
                font-size: 0.9rem;
                margin-top: 8px;
                color: var(--text-secondary);
                position: relative;
                z-index: 1;
            }
            
            .chart-container {
                margin: 40px 0;
                text-align: center;
                background: var(--bg-card);
                padding: 24px;
                border-radius: 12px;
                transition: all 0.3s ease;
            }
            
            .chart-container:hover {
                transform: scale(1.01);
                box-shadow: 0 8px 24px var(--shadow-hover);
            }
            
            .chart-container.interactive-chart {
                padding: 20px;
                background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
                border: 1px solid var(--border-color);
            }
            
            .chart-container.interactive-chart h3::before {
                content: '🎮 ';
                font-size: 0.9em;
            }
            
            .chart-container iframe {
                border-radius: 8px;
                box-shadow: 0 4px 16px var(--shadow);
            }
            
            .chart-container img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 4px 12px var(--shadow);
                transition: all 0.3s ease;
            }
            
            .chart-container img:hover {
                box-shadow: 0 8px 24px var(--shadow-hover);
            }
            
            table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin-top: 20px;
                font-size: 0.95rem;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 8px var(--shadow);
            }
            
            thead {
                background: linear-gradient(135deg, var(--accent-color) 0%, #1557a0 100%);
                color: white;
            }
            
            th {
                padding: 16px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 0.5px;
            }
            
            td {
                padding: 14px 16px;
                border-bottom: 1px solid var(--border-color);
                background-color: var(--bg-secondary);
                transition: all 0.2s ease;
            }
            
            tbody tr {
                transition: all 0.2s ease;
            }
            
            tbody tr:hover {
                background-color: var(--bg-card) !important;
                transform: scale(1.01);
                box-shadow: 0 2px 8px var(--shadow);
            }
            
            tbody tr:nth-child(even) {
                background-color: var(--bg-card);
            }
            
            .positive-value {
                color: var(--success-color);
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            
            .positive-value::before {
                content: "▲";
                font-size: 0.8em;
            }
            
            .negative-value {
                color: var(--danger-color);
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            
            .negative-value::before {
                content: "▼";
                font-size: 0.8em;
            }
            
            .alert {
                padding: 18px 24px;
                margin: 24px 0;
                border-radius: 12px;
                border-left: 4px solid;
                display: flex;
                align-items: center;
                gap: 12px;
                animation: slideInRight 0.5s ease;
            }
            
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            .alert-success {
                background-color: rgba(46, 160, 44, 0.1);
                border-color: var(--success-color);
                color: var(--success-color);
            }
            
            .alert-warning {
                background-color: rgba(255, 152, 0, 0.1);
                border-color: var(--warning-color);
                color: var(--warning-color);
            }
            
            .alert-danger {
                background-color: rgba(214, 39, 40, 0.1);
                border-color: var(--danger-color);
                color: var(--danger-color);
            }
            
            .footer {
                margin-top: 60px;
                padding-top: 24px;
                border-top: 2px solid var(--border-color);
                text-align: center;
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .footer p {
                margin: 8px 0;
            }
            
            /* Scroll progress indicator */
            .progress-bar {
                position: fixed;
                top: 0;
                left: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--accent-color), var(--success-color));
                width: 0%;
                z-index: 1000;
                transition: width 0.2s ease;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .container {
                    padding: 20px;
                }
                
                h1 {
                    font-size: 2rem;
                }
                
                h2 {
                    font-size: 1.5rem;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                    gap: 16px;
                }
                
                .metric-value {
                    font-size: 1.8rem;
                }
                
                table {
                    font-size: 0.85rem;
                }
                
                th, td {
                    padding: 10px;
                }
            }
            
            @media print {
                body {
                    background: white;
                    padding: 0;
                }
                
                .container {
                    box-shadow: none;
                    padding: 20px;
                }
                
                .metric-card:hover {
                    transform: none;
                }
                
                .progress-bar {
                    display: none;
                }
                
                @page {
                    margin: 2cm;
                }
            }
            
            /* Smooth scrolling */
            html {
                scroll-behavior: smooth;
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 12px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--accent-color);
                border-radius: 6px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--text-secondary);
            }
            
            /* Dark mode toggle button */
            .theme-toggle {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                background: var(--bg-card);
                border: 2px solid var(--border-color);
                border-radius: 50px;
                padding: 12px 20px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
                font-weight: 600;
                color: var(--text-primary);
                box-shadow: 0 4px 12px var(--shadow);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                user-select: none;
            }
            
            .theme-toggle:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px var(--shadow-hover);
                border-color: var(--accent-color);
            }
            
            .theme-toggle:active {
                transform: translateY(0);
            }
            
            .theme-icon {
                font-size: 18px;
                transition: transform 0.3s ease;
            }
            
            .theme-toggle:hover .theme-icon {
                transform: rotate(20deg);
            }
            
            @media (max-width: 768px) {
                .theme-toggle {
                    top: 10px;
                    right: 10px;
                    padding: 10px 16px;
                    font-size: 12px;
                }
            }
        </style>
        <script>
            // Dark mode toggle with localStorage
            const initTheme = () => {
                const savedTheme = localStorage.getItem('theme');
                const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const isDark = savedTheme ? savedTheme === 'dark' : systemDark;
                
                document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
                updateToggleButton(isDark);
            };
            
            const toggleTheme = () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                updateToggleButton(newTheme === 'dark');
            };
            
            const updateToggleButton = (isDark) => {
                const btn = document.querySelector('.theme-toggle');
                if (!btn) return;
                
                const icon = btn.querySelector('.theme-icon');
                const text = btn.querySelector('.theme-text');
                
                if (isDark) {
                    icon.textContent = '☀️';
                    text.textContent = 'Modo Claro';
                } else {
                    icon.textContent = '🌙';
                    text.textContent = 'Modo Oscuro';
                }
            };
            
            // Initialize theme on load
            initTheme();
            
            // Scroll progress indicator
            window.addEventListener('scroll', function() {
                const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
                const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrolled = (winScroll / height) * 100;
                const progressBar = document.querySelector('.progress-bar');
                if (progressBar) {
                    progressBar.style.width = scrolled + '%';
                }
            });
            
            // Smooth reveal on scroll
            document.addEventListener('DOMContentLoaded', function() {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }
                    });
                }, { threshold: 0.1 });
                
                document.querySelectorAll('.section').forEach(section => {
                    observer.observe(section);
                });
            });
        </script>
        """
    
    def _encode_image(self, image_path: str | Path) -> str:
        """
        Encode image file as base64 for embedding.
        
        Args:
            image_path: Path to image file
        
        Returns:
            str: Base64 encoded image data URI
        """
        try:
            with open(image_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            warnings.warn(f"Failed to encode image {image_path}: {e}")
            return ""
    
    def _format_currency(self, value: float) -> str:
        """Format value as currency."""
        return f"${value:,.2f}"
    
    def _format_percentage(self, value: float) -> str:
        """Format value as percentage."""
        return f"{value:.2f}%"
    
    def _get_value_class(self, value: float) -> str:
        """Get CSS class based on value (positive/negative)."""
        if value > 0:
            return "positive-value"
        elif value < 0:
            return "negative-value"
        return ""
    
    def generate_executive_summary(
        self,
        total_equity: float,
        cash_balance: float,
        total_pnl: float,
        roi_percent: float,
        num_positions: int,
        win_rate: Optional[float] = None
    ) -> str:
        """
        Generate executive summary section.
        
        Args:
            total_equity: Total portfolio equity
            cash_balance: Current cash balance
            total_pnl: Total P&L
            roi_percent: ROI percentage
            num_positions: Number of open positions
            win_rate: Win rate percentage (optional)
        
        Returns:
            str: HTML for executive summary
        """
        pnl_class = "positive" if total_pnl > 0 else "negative"
        roi_class = "positive" if roi_percent > 0 else "negative"
        
        win_rate_card = ""
        if win_rate is not None:
            win_rate_card = f"""
            <div class="metric-card">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{self._format_percentage(win_rate)}</div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Equity</div>
                    <div class="metric-value">{self._format_currency(total_equity)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Cash Balance</div>
                    <div class="metric-value">{self._format_currency(cash_balance)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Total P&L</div>
                    <div class="metric-value {pnl_class}">{self._format_currency(total_pnl)}</div>
                    <div class="metric-change">{self._format_percentage(roi_percent)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Open Positions</div>
                    <div class="metric-value">{num_positions}</div>
                </div>
                
                {win_rate_card}
            </div>
        </div>
        """
    
    def generate_performance_metrics(
        self,
        metrics: Dict
    ) -> str:
        """
        Generate performance metrics section.
        
        Args:
            metrics: Dictionary of performance metrics
        
        Returns:
            str: HTML for performance metrics
        """
        sharpe = metrics.get('sharpe_annual', 0)
        sortino = metrics.get('sortino_annual', 0)
        beta = metrics.get('beta', 0)
        alpha = metrics.get('alpha_annual', 0)
        max_dd = metrics.get('max_drawdown', 0)
        volatility = metrics.get('annual_volatility', 0)
        
        return f"""
        <div class="section">
            <h2>📈 Performance Metrics</h2>
            
            <h3>Risk-Adjusted Returns</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">{sharpe:.2f}</div>
                    <div class="metric-change">Annualized</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Sortino Ratio</div>
                    <div class="metric-value">{sortino:.2f}</div>
                    <div class="metric-change">Downside risk-adjusted</div>
                </div>
            </div>
            
            <h3>CAPM Analysis (vs S&P 500)</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Beta</div>
                    <div class="metric-value">{beta:.2f}</div>
                    <div class="metric-change">Market sensitivity</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Alpha</div>
                    <div class="metric-value {self._get_value_class(alpha)}">{self._format_percentage(alpha * 100)}</div>
                    <div class="metric-change">Annualized excess return</div>
                </div>
            </div>
            
            <h3>Risk Metrics</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Maximum Drawdown</div>
                    <div class="metric-value negative">{self._format_percentage(max_dd)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Annual Volatility</div>
                    <div class="metric-value">{self._format_percentage(volatility * 100)}</div>
                </div>
            </div>
        </div>
        """
    
    def generate_trade_statistics(
        self,
        metrics: Dict
    ) -> str:
        """
        Generate trade statistics section.
        
        Args:
            metrics: Dictionary with trade statistics
        
        Returns:
            str: HTML for trade statistics
        """
        total_trades = metrics.get('total_trades', 0)
        winning_trades = metrics.get('winning_trades', 0)
        losing_trades = metrics.get('losing_trades', 0)
        win_rate = metrics.get('win_rate', 0)
        avg_win = metrics.get('avg_win', 0)
        avg_loss = metrics.get('avg_loss', 0)
        profit_factor = metrics.get('profit_factor', 0)
        
        return f"""
        <div class="section">
            <h2>💰 Trade Statistics</h2>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Trades</div>
                    <div class="metric-value">{total_trades}</div>
                    <div class="metric-change">{winning_trades} wins / {losing_trades} losses</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">{self._format_percentage(win_rate)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Average Win</div>
                    <div class="metric-value positive">{self._format_currency(avg_win)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Average Loss</div>
                    <div class="metric-value negative">{self._format_currency(avg_loss)}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Profit Factor</div>
                    <div class="metric-value">{profit_factor:.2f}</div>
                    <div class="metric-change">Win $ / Loss $</div>
                </div>
            </div>
        </div>
        """
    
    def _read_html_file(self, html_path: str) -> str:
        """
        Read HTML file and extract the body content (for Plotly charts).
        
        Args:
            html_path: Path to HTML file
        
        Returns:
            str: HTML content to embed
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract body content (Plotly puts everything in body)
            import re
            body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
            
            if body_match:
                return body_match.group(1)
            else:
                # If no body tag, return everything between html tags
                return content
                
        except Exception as e:
            warnings.warn(f"Failed to read HTML file {html_path}: {e}")
            return f'<p style="color: red;">Error loading chart: {e}</p>'
    
    def generate_charts_section(
        self,
        chart_paths: Dict[str, str],
        interactive: bool = True
    ) -> str:
        """
        Generate charts section with embedded content.
        
        Supports both:
        - Interactive HTML charts (Plotly) - embedded as iframes
        - Static PNG images (matplotlib) - embedded as base64
        
        Args:
            chart_paths: Dictionary mapping chart names to file paths
            interactive: If True, embed HTML charts as iframes; if False, use img tags
        
        Returns:
            str: HTML for charts section
        """
        html = '<div class="section"><h2>📊 Visual Analysis</h2>'
        
        chart_titles = {
            'performance_vs_benchmark': 'Portfolio vs S&P 500 Performance',
            'drawdown_analysis': 'Drawdown Analysis',
            'daily_performance': 'Daily Performance',
            'composition': 'Portfolio Composition',
            'win_loss_analysis': 'Win/Loss Analysis',
            'cash_position': 'Cash vs Invested Capital',
            'roi_bars': 'Stock ROI Analysis'
        }
        
        for chart_key, chart_path in chart_paths.items():
            chart_file = Path(chart_path)
            if not chart_file.exists():
                continue
            
            title = chart_titles.get(chart_key, chart_key.replace('_', ' ').title())
            
            # Check file extension to determine type
            if chart_file.suffix.lower() == '.html':
                # Interactive Plotly chart - embed HTML content directly
                embedded_html = self._read_html_file(chart_path)
                html += f"""
                <div class="chart-container interactive-chart">
                    <h3>🎮 {title} <span style="font-size: 0.7em; color: var(--text-secondary);">(Interactive - Zoom, pan, hover)</span></h3>
                    {embedded_html}
                </div>
                """
            else:
                # Static image (PNG) - embed as base64
                encoded_img = self._encode_image(chart_path)
                if encoded_img:
                    html += f"""
                    <div class="chart-container">
                        <h3>{title}</h3>
                        <img src="{encoded_img}" alt="{title}">
                    </div>
                    """
        
        html += '</div>'
        return html
    
    def generate_llm_insights_section(self, llm_insights: Optional[Dict] = None) -> str:
        """
        Generate LLM-powered insights section.
        
        Args:
            llm_insights: Dictionary with LLM-generated insights
        
        Returns:
            str: HTML for insights section
        """
        if not llm_insights:
            return ""
        
        html = """
        <div class="section" style="background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%); border-left: 4px solid var(--accent-color);">
            <h2>🤖 Análisis Inteligente (AI-Generated)</h2>
            <p style="font-size: 0.9em; color: var(--text-secondary); margin-bottom: 20px;">
                Análisis generado automáticamente usando inteligencia artificial para proporcionar contexto y recomendaciones personalizadas.
            </p>
        """
        
        # Executive Summary
        if 'executive_summary' in llm_insights:
            html += f"""
            <div style="margin: 30px 0; padding: 20px; background: var(--bg-primary); border-radius: 8px; box-shadow: 0 2px 8px var(--shadow);">
                <h3 style="color: var(--accent-color); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5em;">📝</span> Resumen Ejecutivo
                </h3>
                <div style="line-height: 1.8; color: var(--text-primary); font-size: 1.05em;">
                    {llm_insights['executive_summary'].replace(chr(10), '<br><br>')}
                </div>
            </div>
            """
        
        # Performance Analysis
        if 'performance_analysis' in llm_insights:
            html += f"""
            <div style="margin: 30px 0; padding: 20px; background: var(--bg-primary); border-radius: 8px; box-shadow: 0 2px 8px var(--shadow);">
                <h3 style="color: var(--success-color); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5em;">📊</span> Análisis de Rendimiento
                </h3>
                <div style="line-height: 1.8; color: var(--text-primary); font-size: 1.05em;">
                    {llm_insights['performance_analysis'].replace(chr(10), '<br><br>')}
                </div>
            </div>
            """
        
        # Risk Assessment
        if 'risk_assessment' in llm_insights:
            html += f"""
            <div style="margin: 30px 0; padding: 20px; background: var(--bg-primary); border-radius: 8px; box-shadow: 0 2px 8px var(--shadow); border-left: 3px solid var(--warning-color);">
                <h3 style="color: var(--warning-color); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5em;">⚠️</span> Evaluación de Riesgo
                </h3>
                <div style="line-height: 1.8; color: var(--text-primary); font-size: 1.05em;">
                    {llm_insights['risk_assessment'].replace(chr(10), '<br><br>')}
                </div>
            </div>
            """
        
        # Recommendations
        if 'recommendations' in llm_insights and llm_insights['recommendations']:
            html += """
            <div style="margin: 30px 0; padding: 20px; background: var(--bg-primary); border-radius: 8px; box-shadow: 0 2px 8px var(--shadow);">
                <h3 style="color: var(--info-color); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.5em;">💡</span> Recomendaciones
                </h3>
                <div style="display: grid; gap: 12px;">
            """
            
            for rec in llm_insights['recommendations']:
                html += f"""
                <div style="padding: 12px 16px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid var(--info-color); line-height: 1.6;">
                    {rec}
                </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def generate_holdings_table(
        self,
        holdings_df: pd.DataFrame
    ) -> str:
        """
        Generate current holdings table.
        
        Args:
            holdings_df: DataFrame with current holdings
        
        Returns:
            str: HTML table of holdings
        """
        if holdings_df.empty:
            return """
            <div class="section">
                <h2>📋 Current Holdings</h2>
                <div class="alert alert-warning">No open positions</div>
            </div>
            """
        
        table_rows = ""
        for _, row in holdings_df.iterrows():
            pnl_class = self._get_value_class(row.get('pnl', 0))
            roi_class = self._get_value_class(row.get('roi_percent', 0))
            
            table_rows += f"""
            <tr>
                <td>{row.get('ticker', 'N/A')}</td>
                <td>{row.get('shares', 0)}</td>
                <td>{self._format_currency(row.get('buy_price', 0))}</td>
                <td>{self._format_currency(row.get('current_price', 0))}</td>
                <td>{self._format_currency(row.get('current_value', 0))}</td>
                <td class="{pnl_class}">{self._format_currency(row.get('pnl', 0))}</td>
                <td class="{roi_class}">{self._format_percentage(row.get('roi_percent', 0))}</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>📋 Current Holdings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Shares</th>
                        <th>Buy Price</th>
                        <th>Current Price</th>
                        <th>Value</th>
                        <th>P&L</th>
                        <th>ROI %</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """
    
    def generate_full_report(
        self,
        output_path: str | Path,
        portfolio_summary: Dict,
        metrics: Dict,
        chart_paths: Dict[str, str],
        holdings_df: Optional[pd.DataFrame] = None,
        llm_insights: Optional[Dict] = None,
        report_date: Optional[datetime] = None
    ) -> str:
        """
        Generate complete HTML report.
        
        Args:
            output_path: Path to save HTML report
            portfolio_summary: Portfolio summary metrics
            metrics: Performance metrics dictionary
            chart_paths: Dictionary of chart file paths
            holdings_df: Optional current holdings DataFrame
            llm_insights: Optional AI-generated insights (from LLMInsightsGenerator)
            report_date: Optional report date (default: today)
        
        Returns:
            str: Path to generated report
        """
        if report_date is None:
            report_date = datetime.now()
        
        # Generate sections
        exec_summary = self.generate_executive_summary(
            total_equity=portfolio_summary.get('total_equity', 0),
            cash_balance=portfolio_summary.get('cash_balance', 0),
            total_pnl=portfolio_summary.get('total_pnl', 0),
            roi_percent=portfolio_summary.get('roi_percent', 0),
            num_positions=portfolio_summary.get('num_positions', 0),
            win_rate=metrics.get('win_rate')
        )
        
        perf_metrics = self.generate_performance_metrics(metrics)
        trade_stats = self.generate_trade_statistics(metrics)
        charts = self.generate_charts_section(chart_paths)
        
        # LLM insights section (if provided)
        llm_section = ""
        if llm_insights:
            llm_section = self.generate_llm_insights_section(llm_insights)
        
        holdings_table = ""
        if holdings_df is not None and not holdings_df.empty:
            holdings_table = self.generate_holdings_table(holdings_df)
        
        # Build complete HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="color-scheme" content="light dark">
            <title>📊 Trading Report - {report_date.strftime('%Y-%m-%d')}</title>
            
            <!-- Plotly.js for interactive charts -->
            <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>
            
            {self.css_style}
        </head>
        <body>
            <button class="theme-toggle" onclick="toggleTheme()" aria-label="Cambiar tema">
                <span class="theme-icon">🌙</span>
                <span class="theme-text">Modo Oscuro</span>
            </button>
            <div class="progress-bar"></div>
            <div class="container">
                <div class="header">
                    <h1>📈 Trading Performance Report</h1>
                    <div class="subtitle">Generated on {report_date.strftime('%B %d, %Y at %I:%M %p')}</div>
                </div>
                
                {exec_summary}
                {perf_metrics}
                {trade_stats}
                {holdings_table}
                {charts}
                {llm_section}
                
                <div class="footer">
                    <p><strong>Agente Agno v3.8.0</strong> - Advanced Trading Analytics with Interactive Charts & AI Insights</p>
                    <p>© {report_date.year} - Automated Trading System | Generated with ❤️</p>
                    <p style="margin-top: 8px; font-size: 0.85em; opacity: 0.7;">
                        💡 Tip: Gráficos interactivos - Zoom (arrastra), Pan, Hover para detalles. Usa el botón 🌙/☀️ para modo oscuro
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(output_path)
