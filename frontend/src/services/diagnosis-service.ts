import api from "../middleware/api";


export const processAuditAndDecision = async (rawDiagnosis: string) => {
  
  const response = await api.post('/diagnose/workflow', { 
    diagnosis: rawDiagnosis 
  });
  return response.data; 
};