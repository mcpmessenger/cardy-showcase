import { Link } from "react-router-dom";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import Footer from "@/components/Footer";

const Terms = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b glass-strong">
        <div className="container mx-auto flex h-14 sm:h-16 items-center justify-end px-4 sm:px-6">
          <a href="/" className="mr-auto text-lg font-semibold hover:text-primary">← Back</a>
          <ThemeToggle />
        </div>
      </header>

      <main className="container mx-auto px-4 sm:px-6 py-8 sm:py-12 max-w-4xl">
        <article className="max-w-none">
          {/* Header Section */}
          <div className="mb-12 text-center border-b pb-8">
            <h1 className="mb-4 text-3xl sm:text-4xl font-bold">Terms of Service</h1>
            <p className="text-muted-foreground italic">
              Last Updated: November 2, 2025
            </p>
          </div>

          {/* Important Notice */}
          <div className="mb-8 p-5 bg-destructive/10 border-l-4 border-destructive rounded-md">
            <p className="font-semibold">
              <strong>IMPORTANT:</strong> By using tubbyAI, you agree to these Terms of Service. Please read them carefully before using our Alexa skill.
            </p>
          </div>

          {/* Section 1 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">1. Acceptance of Terms</h2>
            <p className="mb-4">
              By accessing and using tubbyAI (the "Skill"), you accept and agree to be bound by these Terms of Service. If you do not agree, please do not use our Skill.
            </p>
          </section>

          {/* Section 2 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">2. Description of Service</h2>
            <p className="mb-3">tubbyAI is a voice-activated shopping assistant for Amazon Alexa that provides:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Product search and recommendations from our curated catalog of 108+ premium Amazon products</li>
              <li>Voice-activated product discovery and information</li>
              <li>Affiliate links to Amazon.com for product purchases</li>
              <li>Shopping history and results storage</li>
              <li><strong>Future integration</strong> with Amazon's full catalog via Product Advertising API</li>
            </ul>
          </section>

          {/* Section 3 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">3. Eligibility</h2>
            <p className="mb-4">
              You must be <strong>at least 18 years old</strong> to use this Skill. By using tubbyAI, you represent that you are at least 18 years of age. If you are under 18, you may only use the Skill with parental or guardian consent.
            </p>
          </section>

          {/* Section 4 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">4. Product Information and Purchases</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">Product Listings</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Product information is provided "as is" from our curated catalog and Amazon</li>
              <li>We strive for accuracy but cannot guarantee all information is current</li>
              <li>Prices, availability, and specifications may change without notice</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Affiliate Relationships</h3>
            <div className="mb-4 p-5 bg-primary/10 border-l-4 border-primary rounded-md">
              <p>
                <strong>Amazon Associates Disclosure:</strong> tubbyAI is an Amazon Associate and earns commissions on qualifying purchases. You pay the same price whether you use our links or not. Commissions help us maintain and improve the Skill.
              </p>
            </div>

            <h3 className="mb-3 mt-4 text-xl font-semibold">No Warranty on Products</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>We are <strong>not the seller</strong> of any products</li>
              <li>Product quality, delivery, and returns are governed by Amazon's policies</li>
              <li>Contact Amazon directly for order issues, returns, or refunds</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Future API Integration</h3>
            <p className="mb-3">When Amazon Product Advertising API access is obtained:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Product data will be real-time with millions of products available</li>
              <li>Current catalog is curated and manually maintained</li>
              <li>Expanded access subject to Amazon's API terms and availability</li>
            </ul>
          </section>

          {/* Section 5 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">5. User Responsibilities</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">You Agree NOT To:</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Use the Skill for any illegal or unauthorized purpose</li>
              <li>Attempt to hack, reverse engineer, or compromise security</li>
              <li>Use automated systems or bots to interact with the Skill</li>
              <li>Abuse, harass, or harm others through the Skill</li>
            </ul>
          </section>

          {/* Section 6 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">6. Disclaimer of Warranties</h2>
            
            <div className="mb-4 p-5 bg-destructive/10 border-l-4 border-destructive rounded-md">
              <p className="mb-3 font-semibold">
                <strong>TUBBYAI IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND:</strong>
              </p>
              <ul className="ml-6 list-disc space-y-2">
                <li>We do not warrant product information accuracy</li>
                <li>The Skill may be unavailable due to maintenance</li>
                <li>We do not guarantee error-free operation</li>
                <li>We are not responsible for Amazon or Alexa service interruptions</li>
              </ul>
            </div>
          </section>

          {/* Section 7 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">7. Limitation of Liability</h2>
            <p className="mb-3 font-semibold">TO THE MAXIMUM EXTENT PERMITTED BY LAW:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>We are <strong>NOT LIABLE</strong> for product quality, delivery, or satisfaction</li>
              <li>We are <strong>NOT LIABLE</strong> for pricing errors or discrepancies</li>
              <li>All order issues are between you and Amazon</li>
              <li>Our total liability shall not exceed $100</li>
            </ul>
          </section>

          {/* Section 8 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">8. Privacy</h2>
            <p className="mb-4">
              Your use of tubbyAI is governed by our <a href="/privacy" className="text-primary hover:underline">Privacy Policy</a>. By using the Skill, you consent to our data practices.
            </p>
          </section>

          {/* Section 9 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">9. Modifications</h2>
            <p className="mb-4">
              We reserve the right to modify or discontinue the Skill at any time. We may also update these Terms - changes are effective immediately upon posting to tubbyAI.com/terms.
            </p>
          </section>

          {/* Section 10 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">10. Termination</h2>
            <p className="mb-4">
              You may stop using the Skill anytime by disabling it in your Alexa app. We may terminate your access for violations of these Terms.
            </p>
          </section>

          {/* Section 11 */}
          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold border-b pb-2">11. Governing Law</h2>
            <p className="mb-4">
              These Terms are governed by the laws of the United States. Disputes shall be resolved through binding arbitration (except small claims court).
            </p>
          </section>

          {/* Summary Box */}
          <div className="mb-8 p-6 bg-gradient-to-br from-primary to-purple-600 text-white rounded-lg">
            <h3 className="mb-3 text-xl font-semibold text-white">📋 Summary (Not Legally Binding)</h3>
            <p className="mb-3 text-white/95">In plain English:</p>
            <ul className="ml-6 list-disc space-y-2 text-white/95">
              <li>✅ We help you shop on Amazon with voice commands</li>
              <li>✅ We earn small commissions when you buy (no extra cost to you)</li>
              <li>✅ All purchases happen on Amazon (we're not the seller)</li>
              <li>✅ We protect your privacy and don't sell your data</li>
              <li>✅ We're working on expanding to Amazon's full catalog</li>
              <li>✅ Use responsibly and verify product info before buying</li>
            </ul>
          </div>

          {/* Contact Box */}
          <div className="mb-8 p-6 bg-muted border-2 rounded-lg text-center">
            <h3 className="mb-3 text-xl font-semibold">Questions About These Terms?</h3>
            <p className="mb-3">Contact us at:</p>
            <p className="mb-2">
              <strong>Legal:</strong> <a href="mailto:legal@tubbyai.com" className="text-primary hover:underline font-semibold">legal@tubbyai.com</a>
            </p>
            <p className="mb-2">
              <strong>Support:</strong> <a href="mailto:support@tubbyai.com" className="text-primary hover:underline font-semibold">support@tubbyai.com</a>
            </p>
            <p>
              <strong>Website:</strong> <a href="https://tubbyai.com" className="text-primary hover:underline font-semibold">tubbyai.com</a>
            </p>
          </div>

          {/* Footer Note */}
          <div className="mt-12 pt-8 text-center border-t text-sm text-muted-foreground">
            <p className="mb-2">
              <strong className="text-foreground">tubbyAI Voice Assistant</strong>
            </p>
            <p className="mb-2">Since 2026 • Powered by Amazon Associates</p>
            <p className="mb-4">© {new Date().getFullYear()} tubbyAI.com. All rights reserved.</p>
            <p>
              <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link> | {" "}
              <a href="https://tubbyai.com/contact" className="text-primary hover:underline">Contact Us</a>
            </p>
          </div>
        </article>
      </main>
      <Footer />
    </div>
  );
};

export default Terms;

