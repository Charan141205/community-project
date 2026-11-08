import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "flood-ews | Smart Community Flood & Urban Drainage Early Warning System",
  description:
    "Real-time IoT storm drain monitoring, automated floodgate actuation, multilingual alerts, and dynamic evacuation routing.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
