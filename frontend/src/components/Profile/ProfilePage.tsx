import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Box,
  Button,
  Container,
  Divider,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Select,
  SimpleGrid,
  VStack,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { InviteGenerator } from "./components/InviteGenerator";
import { useToast } from "../Toast/components/ToastContext";
import { useToastThemeFx } from "../Toast/styles/theme-fx";
// 👇 1. Importe o seu contexto de autenticação
import { useAuth } from "../../context/AuthContext";

interface UserProfile {
  full_name: string;
  biological_sex: string;
  blood_type: string;
  birth_date: string;
}

export const ProfilePage: React.FC = () => {
  const { showToast } = useToast();
  const toastThemeFx = useToastThemeFx();

  // 👇 2. Puxe o usuário do contexto e defina a role dinamicamente
  const { user } = useAuth();
  const userRole = user?.role || "user";

  const [profile, setProfile] = useState<UserProfile>({
    full_name: "",
    biological_sex: "",
    blood_type: "",
    birth_date: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await axios.get("/api/profile/", {
          withCredentials: true,
        });
        if (data.profile) {
          setProfile(data.profile);
        }
      } catch (err) {
        console.error("Erro ao buscar perfil", err);
        showToast({
          title: "Erro ao carregar dados",
          message: "Não foi possível buscar as informações do seu perfil.",
          type: "error",
          duration: 5000,
        });
      }
    };
    fetchProfile();
  }, [showToast]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await axios.put("/api/profile/", profile, { withCredentials: true });
      showToast({
        title: "Perfil Atualizado!",
        message: "Suas alterações foram salvas com sucesso no banco de dados.",
        type: "success",
        duration: 3000,
      });
    } catch (err) {
      console.error("Erro ao salvar", err);
      showToast({
        title: "Erro ao salvar",
        message: "Ocorreu um problema ao tentar atualizar seu perfil.",
        type: "error",
        duration: 5000,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Box
        bg={toastThemeFx.cardBg}
        p={{ base: 4, md: 8 }}
        borderRadius="xl"
        border="1px solid"
        borderColor={toastThemeFx.cardBorder}
        backdropFilter="blur(16px)"
        boxShadow="lg"
        w="full"
        overflow="hidden"
      >
        <VStack spacing={8} align="stretch" as="form" onSubmit={handleSave}>
          <Box textAlign="center">
            <Heading
              as="h1"
              size="lg"
              fontWeight="light"
              color={toastThemeFx.textColor}
              letterSpacing="tight"
            >
              Meu Perfil
            </Heading>
            <Text color={toastThemeFx.labelColor} mt={2}>
              Mantenha seus dados atualizados para diagnósticos mais precisos da
              IA.
            </Text>
          </Box>

          <VStack spacing={5} align="stretch">
            <FormControl isRequired>
              <FormLabel color={toastThemeFx.labelColor} fontWeight="medium">
                Nome Completo
              </FormLabel>
              <Input
                type="text"
                value={profile.full_name || ""}
                onChange={(e) =>
                  setProfile({ ...profile, full_name: e.target.value })
                }
                placeholder="Ex: João da Silva"
                bg={toastThemeFx.inputBg}
                borderColor={toastThemeFx.inputBorder}
                _hover={{ borderColor: "blue.300" }}
                focusBorderColor={toastThemeFx.inputFocusBorder}
                color={toastThemeFx.textColor}
                borderRadius="lg"
              />
            </FormControl>

            <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={5}>
              <FormControl isRequired>
                <FormLabel color={toastThemeFx.labelColor} fontWeight="medium">
                  Data de Nascimento
                </FormLabel>
                <Input
                  type="date"
                  value={
                    profile.birth_date ? profile.birth_date.split("T")[0] : ""
                  }
                  onChange={(e) =>
                    setProfile({ ...profile, birth_date: e.target.value })
                  }
                  bg={toastThemeFx.inputBg}
                  borderColor={toastThemeFx.inputBorder}
                  _hover={{ borderColor: "blue.300" }}
                  focusBorderColor={toastThemeFx.inputFocusBorder}
                  color={toastThemeFx.textColor}
                  borderRadius="lg"
                  css={{
                    "&::-webkit-calendar-picker-indicator": {
                      filter: useColorModeValue("invert(0)", "invert(1)"),
                    },
                  }}
                />
              </FormControl>

              <FormControl>
                <FormLabel color={toastThemeFx.labelColor} fontWeight="medium">
                  Tipo Sanguíneo
                </FormLabel>
                <Select
                  value={profile.blood_type || ""}
                  onChange={(e) =>
                    setProfile({ ...profile, blood_type: e.target.value })
                  }
                  placeholder="Selecione..."
                  bg={toastThemeFx.inputBg}
                  borderColor={toastThemeFx.inputBorder}
                  _hover={{ borderColor: "blue.300" }}
                  focusBorderColor={toastThemeFx.inputFocusBorder}
                  color={toastThemeFx.textColor}
                  borderRadius="lg"
                >
                  <option value="A+">A+</option>
                  <option value="O+">O+</option>
                  <option value="B+">B+</option>
                  <option value="AB+">AB+</option>
                  <option value="A-">A-</option>
                  <option value="O-">O-</option>
                  <option value="B-">B-</option>
                  <option value="AB-">AB-</option>
                </Select>
              </FormControl>
            </SimpleGrid>

            <FormControl>
              <FormLabel color={toastThemeFx.labelColor} fontWeight="medium">
                Sexo Biológico
              </FormLabel>
              <Select
                value={profile.biological_sex || ""}
                onChange={(e) =>
                  setProfile({ ...profile, biological_sex: e.target.value })
                }
                placeholder="Selecione..."
                bg={toastThemeFx.inputBg}
                borderColor={toastThemeFx.inputBorder}
                _hover={{ borderColor: "blue.300" }}
                focusBorderColor={toastThemeFx.inputFocusBorder}
                color={toastThemeFx.textColor}
                borderRadius="lg"
              >
                <option value="M">Masculino</option>
                <option value="F">Feminino</option>
              </Select>
            </FormControl>
          </VStack>

          <Button
            type="submit"
            colorScheme="blue"
            size="lg"
            fontSize="md"
            fontWeight="bold"
            w="full"
            borderRadius="xl"
            isLoading={saving}
            loadingText="Salvando Alterações..."
            boxShadow="0 4px 14px 0 rgba(0, 118, 255, 0.39)"
          >
            Salvar Alterações
          </Button>

          {/* 👇 Agora só aparece se a API confirmou que é admin */}
          {userRole === "admin" && (
            <VStack spacing={6} align="stretch" mt={4}>
              <Divider borderColor={toastThemeFx.inputBorder} />
              <Heading
                as="h3"
                size="sm"
                color={toastThemeFx.labelColor}
                textAlign="center"
                textTransform="uppercase"
                letterSpacing="widest"
              >
                Zona do Administrador
              </Heading>
              <InviteGenerator userRole={userRole} />
            </VStack>
          )}
        </VStack>
      </Box>
    </>
  );
};
