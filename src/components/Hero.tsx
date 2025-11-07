import { ShoppingCart, Star } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { VoiceChat } from "@/components/ui/voice-chat";

const Hero = () => {
  const { theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Determine which banner to use based on theme
  const bannerPath = mounted && (resolvedTheme === "dark" || theme === "dark")
    ? "/banner-dark.png"
    : "/banner-light.png";

  return (
    <section className="relative overflow-hidden border-b bg-background py-12 sm:py-16 md:py-24 lg:py-32">
      <div className="container relative mx-auto px-4 sm:px-6">
        <div className="mx-auto max-w-4xl text-center">
          {/* Hero Logo */}
          <div className="flex justify-center mb-8">
            <img 
              src={bannerPath} 
              alt="tubbyAI" 
              className="w-1/2 max-w-2xl"
              style={{ imageRendering: "auto" }}
            />
          </div>
          
          <p className="mt-0 mb-6 sm:mb-8 text-base sm:text-lg md:text-xl text-muted-foreground">
            Talk to tubbyAI - search products, ask questions, and get help with your shopping
          </p>

          {/* Integrated Assistant */}
          <div className="mx-auto mb-8 sm:mb-10 max-w-4xl">
            <div className="bg-card border rounded-lg shadow-lg h-[500px] sm:h-[600px] md:h-[650px]">
              <VoiceChat className="h-full" />
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 md:gap-6 text-muted-foreground text-xs sm:text-sm">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                <div className="h-8 w-8 rounded-full border-2 border-border bg-muted"></div>
                <div className="h-8 w-8 rounded-full border-2 border-border bg-muted"></div>
                <div className="h-8 w-8 rounded-full border-2 border-border bg-muted"></div>
              </div>
              <span className="text-sm font-medium">1000+ Happy Customers</span>
            </div>
            <div className="h-4 w-px bg-border"></div>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              <span className="text-sm font-medium">4.5 Average Rating</span>
            </div>
            <div className="h-4 w-px bg-border"></div>
            <div className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              <span className="text-sm font-medium">Fast Amazon Shipping</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
