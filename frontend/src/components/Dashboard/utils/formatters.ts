export const formatDateBR = (iso: string) => {
  if (!iso) return "--/--";

  const date = new Date(iso);
  if (isNaN(date.getTime())) return iso;

  date.setHours(date.getHours() - 3);

  const day = date.toLocaleString("pt-BR", { day: "2-digit" });
  const month = date.toLocaleString("pt-BR", { month: "2-digit" });
  const hour = date.toLocaleString("pt-BR", { hour: "2-digit", hour12: false });
  const minute = date.toLocaleString("pt-BR", { minute: "2-digit" });

  return `${day}/${month} — ${hour}h${minute}m`;
};