export const formatTimeBR = (iso: string) => {
  const date = new Date(iso);
  const hour = date.toLocaleString("pt-BR", { hour: "2-digit", hour12: false, timeZone: "America/Sao_Paulo" });
  const minute = date.toLocaleString("pt-BR", { minute: "2-digit", timeZone: "America/Sao_Paulo" });
  return `${hour}h${minute}m`;
};

export const shortenAddress = (address: string, chars = 15) => {
  return `${address.substring(0, chars)}...`;
};