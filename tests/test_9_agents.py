"""
Test del Sistema de 9 Agentes con Consenso Multi-Perspectiva
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "agente-agno" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from advanced_trading_team_v2 import create_trading_team

def test_team_structure():
    """Verificar que el equipo tiene 9 agentes"""
    print("=" * 80)
    print("TEST: Estructura del Equipo de 9 Agentes")
    print("=" * 80)
    
    team = create_trading_team(use_openrouter=False)
    
    print(f"\n✓ Equipo creado: {team.name}")
    print(f"✓ Total de agentes: {len(team.members)}")
    
    assert len(team.members) == 9, f"Expected 9 agents, got {len(team.members)}"
    
    print("\nAgentes en el equipo:")
    for i, agent in enumerate(team.members, 1):
        print(f"  {i}. {agent.name} ({agent.role})")
    
    # Verificar nombres esperados
    expected_names = [
        "Market Researcher",
        "Risk Analyst Conservador",
        "Risk Analyst Moderado",
        "Risk Analyst Agresivo",
        "Strategist Técnico",
        "Strategist Fundamental",
        "Strategist Momentum",
        "Portfolio Manager",
        "Daily Reporter"
    ]
    
    actual_names = [agent.name for agent in team.members]
    
    print("\nVerificando nombres de agentes:")
    for expected in expected_names:
        if expected in actual_names:
            print(f"  ✓ {expected}")
        else:
            print(f"  ✗ {expected} - NO ENCONTRADO")
            raise AssertionError(f"Agent '{expected}' not found in team")
    
    print("\n" + "=" * 80)
    print("✓ TODOS LOS TESTS PASARON")
    print("=" * 80)
    print("\nEstructura del equipo:")
    print("  1 Market Researcher")
    print("  3 Risk Analysts (Conservador, Moderado, Agresivo)")
    print("  3 Trading Strategists (Técnico, Fundamental, Momentum)")
    print("  1 Portfolio Manager (sintetiza 6 opiniones)")
    print("  1 Daily Reporter")
    print("\nSistema listo para análisis multi-perspectiva! 🚀")

if __name__ == "__main__":
    try:
        test_team_structure()
    except Exception as e:
        print(f"\n✗ TEST FALLIDO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
