import { ThemeToggle } from "@/components/ui/theme-toggle";
import Footer from "@/components/Footer";

const Privacy = () => {
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
          <h1 className="mb-4 text-3xl sm:text-4xl font-bold">Privacy Policy for tubbyAI</h1>
          
          <p className="mb-8 text-muted-foreground">
            <strong>Last Updated: November 2, 2025</strong>
          </p>

          <section className="mb-8">
            <h2 className="mb-3 text-2xl font-semibold">Introduction</h2>
            <p>
              Welcome to tubbyAI ("we," "our," or "us"). This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Alexa skill and website (tubbyAI.com). Please read this privacy policy carefully. If you do not agree with the terms of this privacy policy, please do not access the skill.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Information We Collect</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">Information You Provide</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Alexa User ID</strong>: We receive your unique Alexa user ID when you interact with our skill</li>
              <li><strong>Voice Commands</strong>: Your spoken queries are processed by Amazon Alexa and sent to our service</li>
              <li><strong>Shopping Queries</strong>: Product searches and preferences you express through voice commands</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Automatically Collected Information</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Session Data</strong>: Conversation context to provide relevant responses</li>
              <li><strong>Usage Statistics</strong>: Skill usage patterns and interaction logs</li>
              <li><strong>Device Information</strong>: Device type and capabilities (e.g., Echo Show vs Echo Dot)</li>
              <li><strong>Timestamp Information</strong>: When you use the skill</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Information from Third Parties</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Amazon Alexa</strong>: User identification and voice transcription</li>
              <li><strong>Amazon Product Data</strong>: Product information, prices, ratings, and images</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">How We Use Your Information</h2>
            <p className="mb-3">We use the information we collect to:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Provide Services</strong>: Process your shopping queries and return relevant product results</li>
              <li><strong>Maintain Session Context</strong>: Remember your conversation for follow-up questions</li>
              <li><strong>Improve Our Service</strong>: Analyze usage patterns to enhance functionality</li>
              <li><strong>Store Shopping History</strong>: Save your search results for access via our web portal</li>
              <li><strong>Send Product Links</strong>: Deliver Amazon affiliate links to your Alexa app</li>
              <li><strong>Troubleshoot Issues</strong>: Debug and resolve technical problems</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Data Storage and Security</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">Storage</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>AWS DynamoDB</strong>: User preferences and shopping history stored in encrypted databases</li>
              <li><strong>AWS CloudWatch</strong>: Temporary logs for debugging (automatically deleted after 30 days)</li>
              <li><strong>Session Data</strong>: Maintained only during active conversations, then cleared</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Security Measures</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Encryption</strong>: All data encrypted in transit (HTTPS/TLS) and at rest (AWS encryption)</li>
              <li><strong>Access Controls</strong>: Strict AWS IAM permissions limiting data access</li>
              <li><strong>No Payment Information</strong>: We never collect or store payment information</li>
              <li><strong>No Passwords</strong>: No authentication credentials are stored</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Data Retention</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Active Users</strong>: Shopping history retained while skill is in use</li>
              <li><strong>Inactive Users</strong>: Data deleted after 365 days of inactivity</li>
              <li><strong>Log Data</strong>: CloudWatch logs auto-deleted after 30 days</li>
              <li><strong>Session Data</strong>: Cleared immediately when session ends</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Third-Party Services</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">Amazon Services</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Amazon Alexa</strong>: Processes voice commands and returns audio responses</li>
              <li><strong>Amazon Associates</strong>: Provides affiliate links for product purchases</li>
              <li><strong>AWS Services</strong>: Hosts our infrastructure (Lambda, DynamoDB, CloudWatch)</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Future Integration</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Amazon Product Advertising API</strong>: When available, will provide real-time product data</li>
              <li>Your consent will be requested before any new data collection methods</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Third-Party Links</h3>
            <p className="mb-3">
              Our skill provides affiliate links to Amazon.com. When you click these links and make purchases:
            </p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Amazon may collect additional information per their privacy policy</li>
              <li>We may earn affiliate commissions (at no extra cost to you)</li>
              <li>Amazon's privacy policy governs your purchases on their platform</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Your Privacy Rights</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">Access and Control</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>View Your Data</strong>: Contact us to request a copy of your data</li>
              <li><strong>Delete Your Data</strong>: Request deletion of your information at any time</li>
              <li><strong>Opt-Out</strong>: Disable the skill to stop data collection immediately</li>
              <li><strong>Correct Information</strong>: Request corrections to any stored data</li>
            </ul>

            <h3 className="mb-3 mt-4 text-xl font-semibold">How to Exercise Your Rights</h3>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Email us at: <a href="mailto:privacy@tubbyai.com" className="text-primary hover:underline">privacy@tubbyai.com</a></li>
              <li>Disable the skill in your Alexa app</li>
              <li>Delete your data by saying "Alexa, tell tubbyAI to delete my data"</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Children's Privacy</h2>
            <p>
              tubbyAI is not intended for children under 13. We do not knowingly collect personal information from children under 13. If you believe we have collected information from a child under 13, please contact us immediately at <a href="mailto:privacy@tubbyai.com" className="text-primary hover:underline">privacy@tubbyai.com</a>.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Changes to This Privacy Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last Updated" date. Continued use of the skill after changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">California Privacy Rights (CCPA)</h2>
            <p className="mb-3">California residents have the right to:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li>Know what personal information is collected</li>
              <li>Know if personal information is sold or shared (we do not sell data)</li>
              <li>Access their personal information</li>
              <li>Request deletion of personal information</li>
              <li>Opt-out of the sale of personal information (not applicable - we don't sell data)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">European Privacy Rights (GDPR)</h2>
            <p className="mb-3">For users in the European Economic Area:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Legal Basis</strong>: Consent and legitimate business interests</li>
              <li><strong>Data Controller</strong>: tubbyAI (contact: <a href="mailto:privacy@tubbyai.com" className="text-primary hover:underline">privacy@tubbyai.com</a>)</li>
              <li><strong>Data Transfers</strong>: Data may be transferred to the United States</li>
              <li><strong>Rights</strong>: Access, rectification, erasure, restriction, portability, objection</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Cookies and Tracking</h2>
            
            <h3 className="mb-3 mt-4 text-xl font-semibold">Alexa Skill</h3>
            <p>The Alexa skill does not use cookies or tracking technologies.</p>

            <h3 className="mb-3 mt-4 text-xl font-semibold">Website (tubbyAI.com)</h3>
            <p className="mb-3">Our website may use:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Essential Cookies</strong>: Required for website functionality</li>
              <li><strong>Analytics</strong>: To understand how visitors use our site</li>
              <li><strong>No Advertising Cookies</strong>: We do not use advertising trackers</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Do Not Track Signals</h2>
            <p>
              We do not currently respond to Do Not Track (DNT) browser signals, as there is no industry standard for compliance.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Contact Us</h2>
            <p className="mb-3">If you have questions about this Privacy Policy, please contact us:</p>
            <ul className="mb-4 ml-6 list-disc space-y-2">
              <li><strong>Email</strong>: <a href="mailto:privacy@tubbyai.com" className="text-primary hover:underline ml-1">privacy@tubbyai.com</a></li>
              <li><strong>Website</strong>: <a href="https://tubbyai.com/contact" className="text-primary hover:underline ml-1">https://tubbyai.com/contact</a></li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">Amazon Associates Disclosure</h2>
            <p>
              tubbyAI is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. We may earn commissions on qualifying purchases made through our affiliate links, at no additional cost to you.
            </p>
          </section>

          <hr className="my-8" />

          <p className="text-sm text-muted-foreground">
            <strong>Effective Date</strong>: November 2, 2025
          </p>
          <p>
            By using tubbyAI, you acknowledge that you have read and understood this Privacy Policy.
          </p>
        </article>
      </main>
      <Footer />
    </div>
  );
};

export default Privacy;

