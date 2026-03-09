import { ethers } from "ethers";
import { INPUT_BOX_ADDRESS, DAPP_ADDRESS, INPUTBOX_ABI } from "../utils/constants";
import { type HistoryItem } from "../types";

export const sendDiagnosisToCartesi = async (
  item: HistoryItem, 
  signer: ethers.Signer, 
  walletAddress: string
) => {
  const payload = JSON.stringify({
    action: "register_diagnosis",
    diagnosis_id: item.id,
    type: item.type,
    timestamp: item.date,
    data_hash: ethers.id(JSON.stringify(item.result)),
    submitter: walletAddress,
  });

  const inputBytes = ethers.toUtf8Bytes(payload);
  const inputBox = new ethers.Contract(INPUT_BOX_ADDRESS, INPUTBOX_ABI, signer);

  return await inputBox.addInput(DAPP_ADDRESS, inputBytes);
};