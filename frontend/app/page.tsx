import { Hero } from "@/components/landing/hero";
import { Uploader } from "@/components/upload/uploader";
import { ReviewDialog } from "@/components/review/review-dialog";
import { Gallery } from "@/components/results/gallery";

export default function Home() {
  return (
    <main className="min-h-screen pb-24">
      <Hero />
      <div id="upload-section" className="scroll-mt-24">
        <Uploader />
      </div>
      <ReviewDialog />
      <Gallery />
      <footer className="w-full mt-32 py-8 text-center text-sm text-muted-foreground border-t border-border/40">
        <p>Creado por Arcano Intelligence</p>
      </footer>
    </main>
  );
}
