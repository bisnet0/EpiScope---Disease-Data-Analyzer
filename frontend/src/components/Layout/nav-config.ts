import { Activity } from "react-bootstrap-icons";
import { FaMosquito, FaRegEye } from "react-icons/fa6";
import { PiSignatureLight } from "react-icons/pi";
import { GiLungs } from "react-icons/gi";
import { BsHeartPulseFill } from "react-icons/bs";

export type AppMode = "dashboard" | "web2" | "web3" | "image" | "x-ray" | "health-stats-panel";

export const NAV_ITEMS = [
  { id: "dashboard" as AppMode, label: "Dashboard", icon: Activity },
  { id: "web2" as AppMode, label: "Arboviroses", icon: FaMosquito },
  { id: "image" as AppMode, label: "Glaucoma", icon: FaRegEye },
  { id: "web3" as AppMode, label: "Assinatura", icon: PiSignatureLight },
  { id: "x-ray" as AppMode, label: "Análise Pulmonar", icon: GiLungs },
  { id: "health-stats-panel" as AppMode, label: "Bem-estar", icon: BsHeartPulseFill },
];