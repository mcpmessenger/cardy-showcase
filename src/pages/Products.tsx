import { useState, useMemo } from "react";
import { ShoppingBag, Star, Search, Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { products, getCategoriesWithCounts, getProductsByCategory, searchProducts } from "@/lib/products";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ProductImageCarousel } from "@/components/ui/product-image-carousel";

const Products = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const categories = useMemo(() => getCategoriesWithCounts(), []);

  const filteredProducts = useMemo(() => {
    let filtered = products;

    if (selectedCategory !== "all") {
      filtered = getProductsByCategory(selectedCategory);
    }

    if (searchQuery.trim()) {
      filtered = searchProducts(searchQuery).filter((p) =>
        selectedCategory === "all" || p.category === selectedCategory
      );
    }

    return filtered;
  }, [searchQuery, selectedCategory]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(price);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b glass-strong">
        <div className="container mx-auto flex h-14 sm:h-16 items-center justify-between px-4 sm:px-6">
          <a href="/" className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border bg-background">
              <ShoppingBag className="h-6 w-6" />
            </div>
            <span className="text-xl font-bold">AIPro Store</span>
          </a>
          <ThemeToggle />
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="border-b bg-muted/30 py-6 sm:py-8 md:py-12">
          <div className="container mx-auto px-4 sm:px-6">
            <h1 className="mb-2 sm:mb-4 text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold">All Products</h1>
            <p className="text-sm sm:text-base md:text-lg text-muted-foreground">
              Browse our complete catalog of {products.length} premium products
            </p>
          </div>
        </section>

        {/* Filters */}
        <section className="border-b bg-background py-4 sm:py-6">
          <div className="container mx-auto px-4 sm:px-6">
            <div className="flex flex-col gap-3 sm:gap-4 md:flex-row md:items-center md:justify-between">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <div className="flex items-center gap-4">
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((cat) => (
                      <SelectItem key={cat.name} value={cat.name}>
                        {cat.displayName} ({cat.count})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {(searchQuery || selectedCategory !== "all") && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedCategory("all");
                    }}
                  >
                    <X className="mr-2 h-4 w-4" />
                    Clear
                  </Button>
                )}
              </div>
            </div>

            {(searchQuery || selectedCategory !== "all") && (
              <div className="mt-4 text-sm text-muted-foreground">
                Showing {filteredProducts.length} of {products.length} products
              </div>
            )}
          </div>
        </section>

        {/* Products Grid */}
        <section className="py-6 sm:py-8 md:py-12">
          <div className="container mx-auto px-4 sm:px-6">
            {filteredProducts.length === 0 ? (
              <div className="py-20 text-center">
                <p className="text-lg text-muted-foreground">No products found. Try adjusting your filters.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-5 lg:grid-cols-3 lg:gap-6 xl:grid-cols-4">
                {filteredProducts.map((product) => (
                  <a
                    key={product.asin}
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group rounded-xl border bg-card shadow-[var(--shadow-card)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-lg)]"
                  >
                    <div className="relative">
                      <ProductImageCarousel
                        product={product}
                        showIndicators={true}
                        className="group"
                      />
                      {product.badge && (
                        <Badge className="absolute right-2 top-2 z-10">
                          {product.badge}
                        </Badge>
                      )}
                    </div>
                    <div className="p-3 sm:p-4">
                      <h3 className="mb-2 line-clamp-2 text-sm sm:text-base font-semibold group-hover:text-primary">
                        {product.name}
                      </h3>
                      <p className="mb-3 line-clamp-2 text-xs sm:text-sm text-muted-foreground">
                        {product.description}
                      </p>
                      <div className="mb-3 flex items-center gap-2">
                        <div className="flex items-center">
                          <Star className="h-3.5 w-3.5 sm:h-4 sm:w-4 fill-yellow-400 text-yellow-400" />
                          <span className="ml-1 text-xs sm:text-sm font-medium">{product.rating}</span>
                        </div>
                        <span className="text-xs sm:text-sm text-muted-foreground">
                          ({product.reviews.toLocaleString()} reviews)
                        </span>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-lg sm:text-xl lg:text-2xl font-bold text-primary">
                          {formatPrice(product.price)}
                        </span>
                        <Badge variant="outline" className="text-[10px] sm:text-xs shrink-0">
                          {product.category}
                        </Badge>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Products;

