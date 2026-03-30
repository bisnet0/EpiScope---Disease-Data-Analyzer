# 👇 Importando as ferramentas isoladas de cada módulo
from backend.modules.chest_xray.agents.xray_tools import xray_tool

# ATENÇÃO: Descomente e ajuste os imports abaixo conforme você for movendo as outras tools!
# from backend.modules.arbovirus.agents.arbovirus_tools import arbovirus_specialist
# from backend.modules.glaucoma.agents.glaucoma_tools import glaucoma_specialist
# from backend.modules.laboratory.agents.lab_tools import lab_manager
# from backend.modules.core_agent.agents.audio_analysis_tools import audio_analysis_tool

# O Core Agent empacota todas elas aqui:
MEDICAL_TOOLS = [
    xray_tool,
    # arbovirus_specialist,
    # glaucoma_specialist,
    # lab_manager,
    # audio_analysis_tool
]