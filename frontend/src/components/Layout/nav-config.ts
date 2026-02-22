import { Activity } from "react-bootstrap-icons";
import { FaMosquito, FaRegEye } from "react-icons/fa6";
import { PiSignatureLight } from "react-icons/pi";

export type AppMode = "dashboard" | "web2" | "web3" | "image";

export const NAV_ITEMS = [
  { id: "dashboard" as AppMode, label: "Dashboard", icon: Activity },
  { id: "web2" as AppMode, label: "Arboviroses", icon: FaMosquito },
  { id: "image" as AppMode, label: "Glaucoma", icon: FaRegEye },
  { id: "web3" as AppMode, label: "Ledger Web3", icon: PiSignatureLight },
];