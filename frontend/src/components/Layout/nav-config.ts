import { Activity, Calendar, Calendar2, Calendar2Date, Calendar2MonthFill } from "react-bootstrap-icons";
import { FaMosquito, FaRegEye } from "react-icons/fa6";
import { PiDrop, PiSignatureLight } from "react-icons/pi";
import { GiBlood, GiLungs } from "react-icons/gi";
import { BsHeartPulseFill } from "react-icons/bs";
import { SlUserFemale } from "react-icons/sl";
import { FiActivity, FiVideo } from "react-icons/fi"; // Ícones para os submenus
import { FaTheaterMasks } from "react-icons/fa";

// 1. Atualizamos o AppMode com os novos IDs dos submenus
export type AppMode =
  | "dashboard"
  | "web2"
  | "web3"
  | "image"
  | "x-ray"
  | "health-stats-panel"
  | "WomensHealth" // O menu pai
  | "womens-biomarkers" // Submenu 1: Áudio e Vídeo
  | "womens-surgery" // Submenu 2: Cirurgia YOLO
  | "womens-predictive"; // Submenu 3: Previsão de Ciclo

// 2. Criamos a interface para o TypeScript entender o dropdown
export interface NavItem {
  id: AppMode;
  label: string;
  icon: any;
  children?: NavItem[]; // A mágica do dropdown acontece aqui
}

// 3. Montamos o array final
export const NAV_ITEMS: NavItem[] = [
  { id: "dashboard", label: "Dashboard", icon: Activity },
  { id: "web2", label: "Arboviroses", icon: FaMosquito },
  { id: "image", label: "Glaucoma", icon: FaRegEye },
  { id: "web3", label: "Assinatura", icon: PiSignatureLight },
  { id: "x-ray", label: "Análise Pulmonar", icon: GiLungs },
  { id: "health-stats-panel", label: "Bem-estar", icon: BsHeartPulseFill },
  {
    id: "WomensHealth",
    label: "Saúde da Mulher",
    icon: SlUserFemale,
    children: [
      {
        id: "womens-biomarkers",
        label: "Biomarcadores",
        icon: FaTheaterMasks,
      },
      {
        id: "womens-surgery",
        label: "Análise Cirúrgica",
        icon: FiVideo,
      },
      {
        id: "womens-predictive",
        label: "Previsão de Ciclo",
        icon: PiDrop,
      },
    ],
  },
];
