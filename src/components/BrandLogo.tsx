import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

interface BrandLogoProps {
  className?: string;
  withSubtitle?: boolean;
}

export function BrandLogo({ className = "", withSubtitle = false }: BrandLogoProps) {
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
        className="h-8 md:h-10"
        style={{ imageRendering: "auto" }}
      />
      {withSubtitle && (
        <div className="flex flex-col">
          <span className="text-xl md:text-2xl font-bold">tubbyAI.com</span>
          <span className="text-xs md:text-sm text-muted-foreground">Voice Assistant</span>
        </div>
      )}
    </div>
  );
}

