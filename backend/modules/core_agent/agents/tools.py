# 👇 Importando as ferramentas isoladas de cada módulo
from backend.modules.chest_xray.agents.xray_tools import xray_tool

# ATENÇÃO: Descomente e ajuste os imports abaixo conforme você for movendo as outras tools!
from backend.modules.arbovirus.agents.arbovirus_tools import arbovirus_tool
from backend.modules.glaucoma.agents.glaucoma_tools import glaucoma_tool
from backend.modules.laboratory.agents.lab_tools import lab_manager_tool
from backend.modules.integrations.agents.health_tools import health_metrics_tool
# from backend.modules.core_agent.agents.audio_analysis_tools import audio_analysis_tool

# O Core Agent empacota todas elas aqui:
MEDICAL_TOOLS = [
    xray_tool,
    arbovirus_tool,
    glaucoma_tool,
    lab_manager_tool,
    health_metrics_tool,
    # audio_analysis_tool
]