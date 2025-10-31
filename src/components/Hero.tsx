import { Search, ShoppingCart, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Hero = () => {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary via-primary to-primary-glow py-20 md:py-32">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRoLTJ2LTJoMnYyek0zOCAzMmgtMnYtMmgydjJ6bS0yLTJoLTJ2LTJoMnYyek0zNCAzMGgtMnYtMmgydjJ6bS04IDBoLTJ2LTJoMnYyem0yLTJoLTJ2LTJoMnYyem0yIDBoLTJ2LTJoMnYyem0yIDJoLTJ2LTJoMnYyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>
      
      <div className="container relative mx-auto px-4">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-2 text-sm font-medium text-white backdrop-blur-sm">
            <Star className="h-4 w-4 fill-current" />
            <span>108 Curated Premium Products</span>
          </div>
          
          <h1 className="mb-6 text-4xl font-bold text-white md:text-6xl lg:text-7xl">
            Shop Smart,
            <br />
            <span className="bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              Live Better
            </span>
          </h1>
          
          <p className="mb-8 text-lg text-white/90 md:text-xl">
            Discover handpicked products from top brands on Amazon.
            <br />
            Quality guaranteed, shipped fast, backed by reviews.
          </p>

          <div className="mx-auto mb-10 max-w-2xl">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search 108 products..."
                  className="h-14 bg-white pl-12 pr-4 text-base shadow-lg"
                />
              </div>
              <Button size="lg" variant="secondary" className="h-14 px-8 shadow-lg">
                Search
              </Button>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-white/90">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                <div className="h-8 w-8 rounded-full border-2 border-white bg-white/20"></div>
                <div className="h-8 w-8 rounded-full border-2 border-white bg-white/20"></div>
                <div className="h-8 w-8 rounded-full border-2 border-white bg-white/20"></div>
              </div>
              <span className="text-sm font-medium">1000+ Happy Customers</span>
            </div>
            <div className="h-4 w-px bg-white/30"></div>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 fill-current text-white" />
              <span className="text-sm font-medium">4.5 Average Rating</span>
            </div>
            <div className="h-4 w-px bg-white/30"></div>
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
