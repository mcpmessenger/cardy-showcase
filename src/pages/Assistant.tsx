import { VoiceChat } from "@/components/ui/voice-chat";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";
import { Home } from "lucide-react";
import { Link } from "react-router-dom";

const Assistant = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b glass-strong">
        <div className="container mx-auto flex h-14 sm:h-16 items-center justify-between px-4 sm:px-6">
          <Link to="/">
            <Button variant="ghost" size="sm">
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
          </Link>
          <ThemeToggle />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-6">
        <div className="max-w-5xl mx-auto">
          <div className="mb-6 text-center">
            <h1 className="text-3xl font-bold mb-2">AI Voice Assistant</h1>
            <p className="text-muted-foreground">
              Talk to tubbyAI - search products, ask questions, and get help with your shopping
            </p>
          </div>
          
          <div className="bg-card border rounded-lg shadow-lg h-[calc(100vh-200px)] min-h-[600px]">
            <VoiceChat className="h-full" />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Assistant;

