"use client";

import { useState, useCallback } from "react";
import { useUpload } from "@/hooks/use-upload"; // We'll implement this hook
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { CloudUpload, FileText, X, CheckCircle2, AlertCircle } from "lucide-react";
import { useStrainStore } from "@/lib/store";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export function Uploader() {
  const [isDragging, setIsDragging] = useState(false);
  const { handleUpload } = useUpload();
  const { reports, removeReport, isProcessing, setActiveReport } = useStrainStore();

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleUpload(files);
  }, [handleUpload]);

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-8">
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        className={cn(
          "relative group border-2 border-dashed rounded-3xl p-12 transition-all duration-300 flex flex-col items-center justify-center text-center gap-4",
          isDragging ? "border-primary bg-primary/5 scale-[1.01]" : "border-white/10 glass hover:border-primary/50"
        )}
      >
        <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
          <CloudUpload className="w-10 h-10 text-primary" />
        </div>
        <div>
          <h3 className="text-2xl font-bold mb-2">Upload Lab Reports</h3>
          <p className="text-muted-foreground text-lg max-w-md mx-auto">
            Drag and drop your COA files (PDF, PNG, JPG) or click to browse. We support up to 10 files at once.
          </p>
        </div>
        <Button size="lg" className="rounded-full px-8 mt-4 font-semibold">
          Select Files
        </Button>
        <input
          type="file"
          multiple
          className="absolute inset-0 opacity-0 cursor-pointer"
          onChange={(e) => handleUpload(Array.from(e.target.files || []))}
        />
      </div>

      <AnimatePresence>
        {reports.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <h4 className="text-xl font-bold flex items-center justify-between">
              Upload History
              <span className="text-sm font-normal text-muted-foreground">{reports.length} files</span>
            </h4>
            <div className="grid grid-cols-1 gap-3">
              {reports.map((report) => (
                <motion.div
                  layout
                  key={report.id}
                  className="glass p-4 rounded-2xl flex items-center gap-4 border-white/5 hover:border-white/10 transition-all"
                >
                  <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-muted-foreground" />
                  </div>
                  <div 
                    className="flex-1 min-w-0 cursor-pointer group/item"
                    onClick={() => setActiveReport(report.id)}
                  >
                    <p className="font-semibold truncate group-hover/item:text-primary transition-colors">{report.file_name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {report.status === 'extracting' && <span className="text-xs text-primary animate-pulse">Extracting AI Data...</span>}
                      {report.status === 'reviewing' && <span className="text-xs text-neon-blue font-medium">Click to Review & Generate</span>}
                      {report.status === 'completed' && <span className="text-xs text-neon-green flex items-center gap-1 font-medium"><CheckCircle2 className="w-3 h-3" /> Ready to Download</span>}
                      {report.status === 'failed' && <span className="text-xs text-destructive flex items-center gap-1 font-medium"><AlertCircle className="w-3 h-3" /> Extraction Failed</span>}
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="rounded-full hover:bg-destructive/10 hover:text-destructive transition-colors" onClick={() => removeReport(report.id)}>
                    <X className="w-5 h-5" />
                  </Button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
