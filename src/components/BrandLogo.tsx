import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

interface BrandLogoProps {
  className?: string;
}

export function BrandLogo({ className = "" }: BrandLogoProps) {
  const { theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Determine which logo to use based on theme
  const logoPath = mounted && (resolvedTheme === "dark" || theme === "dark")
    ? "/tubbyAI-logo-dark.png"
    : "/tubbyAI-logo-light.png";

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <img 
        src={logoPath} 
        alt="tubbyAI Logo" 
        className="h-32 md:h-40"
        style={{ imageRendering: "auto" }}
      />
    </div>
  );
}

