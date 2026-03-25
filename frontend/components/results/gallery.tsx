"use client";

import { useStrainStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Download, LayoutGrid, Trash2, FileJson } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function Gallery() {
  const { reports, removeReport } = useStrainStore();
  const completedReports = reports.filter(r => r.status === 'completed');

  if (completedReports.length === 0) return null;

  const downloadImage = (report: any) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${report.preview_url}`;
    link.download = `${report.strain_name.replace(/\s+/g, '_')}_Dashboard.png`;
    link.click();
  };

  const downloadJson = (report: any) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const link = document.createElement('a');
    link.href = dataStr;
    link.download = `${report.strain_name.replace(/\s+/g, '_')}_Data.json`;
    link.click();
  };

  return (
    <section className="container mx-auto max-w-6xl py-24 px-6">
      <div className="flex items-center justify-between mb-12">
        <h2 className="text-4xl font-outfit font-bold flex items-center gap-3">
          <LayoutGrid className="w-8 h-8 text-primary" /> Generated Dashboards
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <AnimatePresence>
          {completedReports.map((report) => (
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              key={report.id}
            >
              <Card className="glass border-white/5 overflow-hidden group hover:border-primary/30 transition-all duration-500">
                <CardContent className="p-4">
                  <div className="relative aspect-[4/5] overflow-hidden rounded-xl bg-black/40">
                    <img 
                      src={`data:image/png;base64,${report.preview_url}`} 
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" 
                      alt={report.strain_name} 
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-6">
                       <h3 className="text-xl font-bold">{report.strain_name}</h3>
                       <p className="text-sm text-primary">{report.strain_type}</p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="p-4 pt-0 flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1 glass border-white/10 hover:bg-primary/20" onClick={() => downloadImage(report)}>
                    <Download className="w-4 h-4 mr-2" /> PNG
                  </Button>
                  <Button variant="outline" size="sm" className="glass border-white/10 hover:bg-secondary/20" onClick={() => downloadJson(report)}>
                    <FileJson className="w-4 h-4 mr-2" /> JSON
                  </Button>
                  <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive transition-colors" onClick={() => removeReport(report.id)}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </CardFooter>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </section>
  );
}
