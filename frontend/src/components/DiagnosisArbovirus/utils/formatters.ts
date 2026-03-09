export const formatResponseHtml = (text: string) => {
  if (!text) return "";
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br />');
};