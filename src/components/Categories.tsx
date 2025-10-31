import { Headphones, Home, Sparkles, Shirt, Dumbbell, BookOpen, Car, Leaf, Briefcase } from "lucide-react";
import { getCategoriesWithCounts } from "@/lib/products";
import { useMemo } from "react";

const iconMap: Record<string, any> = {
  electronics: Headphones,
  home: Home,
  beauty: Sparkles,
  fashion: Shirt,
  sports: Dumbbell,
  books: BookOpen,
  toys: BookOpen,
  garden: Leaf,
  automotive: Car,
  office: Briefcase,
};

const colorMap: Record<string, string> = {
  electronics: "from-blue-500 to-blue-600",
  home: "from-green-500 to-green-600",
  beauty: "from-pink-500 to-pink-600",
  fashion: "from-purple-500 to-purple-600",
  sports: "from-orange-500 to-orange-600",
  books: "from-cyan-500 to-cyan-600",
  toys: "from-cyan-500 to-cyan-600",
  garden: "from-emerald-500 to-emerald-600",
  automotive: "from-gray-500 to-gray-600",
  office: "from-indigo-500 to-indigo-600",
};

const Categories = () => {
  const categories = useMemo(() => getCategoriesWithCounts(), []);

  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold md:text-4xl">Shop by Category</h2>
          <p className="text-lg text-muted-foreground">
            Browse our carefully curated collection across {categories.length} categories
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6 lg:gap-6">
          {categories.map((category) => {
            const Icon = iconMap[category.name] || Home;
            const color = colorMap[category.name] || "from-gray-500 to-gray-600";
            return (
              <button
                key={category.name}
                className="group relative overflow-hidden rounded-2xl bg-card p-6 shadow-[var(--shadow-card)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-lg)]"
              >
                <div className={`mb-4 inline-flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br ${color} text-white shadow-lg transition-transform duration-300 group-hover:scale-110`}>
                  <Icon className="h-8 w-8" />
                </div>
                <h3 className="mb-1 text-base font-semibold">{category.displayName}</h3>
                <p className="text-sm text-muted-foreground">{category.count} products</p>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Categories;
