"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowRight, Leaf, Sparkles, ShieldCheck } from "lucide-react";
import { useStrainStore } from "@/lib/store";

export function Hero() {
  const { loadDemo } = useStrainStore();
  return (
    <section className="relative overflow-hidden py-24 px-6">
      {/* Ambient backgrounds */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-6xl h-full pointer-events-none opacity-20">
        <div className="absolute top-0 left-0 w-96 h-96 bg-primary blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent blur-[120px] rounded-full animate-pulse delay-1000" />
      </div>

      <div className="container mx-auto max-w-5xl relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-8"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary-foreground text-sm font-medium backdrop-blur-sm mb-4">
            <Sparkles className="w-4 h-4 text-accent" />
            <span>AI-Powered Lab Analysis</span>
          </div>

          <h1 className="text-6xl md:text-8xl font-outfit font-bold tracking-tight text-white leading-[1.1]">
            Transform Lab Reports into <span className="text-transparent bg-clip-text bg-neon-gradient px-2 py-1">Premium Profiles</span>
          </h1>

          <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-sans leading-relaxed">
            Upload your COA, and let our AI extract total cannabinoids, terpenes, and genetic data to generate professional, high-end dashboard images for your brand.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-12">
            <Button 
              size="lg" 
              className="rounded-full px-8 h-14 text-lg font-semibold bg-primary hover:bg-primary/90 transition-all hover:scale-105 neon-glow-purple"
              onClick={() => {
                const uploadSection = document.getElementById('upload-section');
                uploadSection?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Start Analyzing <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="rounded-full px-8 h-14 text-lg font-semibold glass hover:bg-white/10 transition-all"
              onClick={() => loadDemo()}
            >
              View Example
            </Button>
          </div>
        </motion.div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24">
          {[
            { 
              icon: <Leaf className="w-6 h-6 text-neon-green" />, 
              title: "Smart Extraction", 
              desc: "Precise identification of THC, CBD, and over 40+ terpenes directly from PDFs." 
            },
            { 
              icon: <Sparkles className="w-6 h-6 text-neon-purple" />, 
              title: "Premium Rendering", 
              desc: "Generate professional, glass-styled dashboard images ready for social media." 
            },
            { 
              icon: <ShieldCheck className="w-6 h-6 text-neon-blue" />, 
              title: "Verified Data", 
              desc: "Each result includes a confidence score and full manual correction tools." 
            }
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 * idx }}
              className="glass p-8 rounded-3xl space-y-4 hover:border-white/20 transition-all"
            >
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.desc}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
