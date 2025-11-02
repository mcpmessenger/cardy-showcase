import { Search, ShoppingCart, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { VoiceSearchButton } from "@/components/ui/voice-search-button";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

const Hero = () => {
  const { theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [searchValue, setSearchValue] = useState("");

  useEffect(() => {
    setMounted(true);
  }, []);

  // Determine which banner to use based on theme
  const bannerPath = mounted && (resolvedTheme === "dark" || theme === "dark")
    ? "/banner-dark.png"
    : "/banner-light.png";

  const handleTranscription = (text: string) => {
    setSearchValue(text);
  };

  return (
    <section className="relative overflow-hidden border-b bg-background py-12 sm:py-16 md:py-24 lg:py-32">
      <div className="container relative mx-auto px-4 sm:px-6">
        <div className="mx-auto max-w-4xl text-center">
          {/* Hero Logo */}
          <div className="flex justify-center mb-8">
            <img 
              src={bannerPath} 
              alt="tubbyAI" 
              className="w-full max-w-4xl"
              style={{ imageRendering: "auto" }}
            />
          </div>
          
          <p className="mt-0 mb-6 sm:mb-8 text-base sm:text-lg md:text-xl text-muted-foreground">
            Discover handpicked products from top brands on Amazon.
            <br className="hidden sm:block" />
            <span className="sm:hidden"> </span>
            Quality guaranteed, shipped fast, backed by reviews.
          </p>

          <div className="mx-auto mb-8 sm:mb-10 max-w-2xl">
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 sm:left-4 top-1/2 h-4 w-4 sm:h-5 sm:w-5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search products..."
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  className="h-12 sm:h-14 glass-strong pl-10 sm:pl-12 pr-12 text-sm sm:text-base"
                />
                <VoiceSearchButton 
                  onTranscription={handleTranscription}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                />
              </div>
              <Button size="lg" variant="default" className="h-12 sm:h-14 px-6 sm:px-8 w-full sm:w-auto" asChild>
                <a href={`/products${searchValue ? `?q=${encodeURIComponent(searchValue)}` : ''}`}>
                  Search
                </a>
              </Button>
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
