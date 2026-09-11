import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Central de Atendimento | Nhora",
  description: "Central de atendimento, vendas e suporte da Nhora",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
