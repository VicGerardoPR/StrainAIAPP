"use client";

import { useState, useEffect } from "react";
import { useStrainStore, LabReportData } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Save, Download, Eye, Sparkles } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ReviewDialog() {
  const { reports, activeReportId, setActiveReport, updateReport } = useStrainStore();
  const report = reports.find((r) => r.id === activeReportId);
  
  const [editedData, setEditedData] = useState<LabReportData | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  useEffect(() => {
    if (report) setEditedData({ ...report });
  }, [report]);

  if (!report || !editedData) return null;

  const handleSave = async () => {
    updateReport(report.id, { ...editedData });
    toast.success("Data saved locally");
  };

  const handleGeneratePreview = async () => {
    setIsPreviewLoading(true);
    try {
      const resp = await axios.post(`${API_BASE_URL}/generate-preview`, editedData);
      updateReport(report.id, { preview_url: resp.data.image_data, status: 'completed' });
      toast.success("Premium Dashboard Generated!");
    } catch (e) {
      toast.error("Generation failed");
    } finally {
      setIsPreviewLoading(false);
    }
  };

  return (
    <Dialog open={!!activeReportId} onOpenChange={(open) => !open && setActiveReport(null)}>
      <DialogContent className="max-w-4xl h-[85vh] flex flex-col glass border-white/10 p-0 overflow-hidden">
        <DialogHeader className="p-6 border-b border-white/5">
          <DialogTitle className="text-2xl font-outfit flex items-center gap-2">
            <Eye className="w-6 h-6 text-primary" /> Review Results: {report.file_name}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 flex overflow-hidden">
          {/* Editor Side */}
          <div className="w-1/2 border-r border-white/5 p-6 overflow-y-auto">
            <div className="space-y-6">
              <div className="grid gap-2">
                <Label>Strain Name</Label>
                <Input value={editedData.strain_name} onChange={(e) => setEditedData({...editedData, strain_name: e.target.value})} className="bg-white/5 border-white/10" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>Strain Type</Label>
                  <Input value={editedData.strain_type} onChange={(e) => setEditedData({...editedData, strain_type: e.target.value})} className="bg-white/5 border-white/10" />
                </div>
                <div className="grid gap-2">
                  <Label>Lab Name</Label>
                  <Input value={editedData.lab_name} onChange={(e) => setEditedData({...editedData, lab_name: e.target.value})} className="bg-white/5 border-white/10" />
                </div>
              </div>

              <div className="space-y-4">
                <h5 className="font-bold border-b border-white/5 pb-2">Cannabinoids (%)</h5>
                {editedData.cannabinoids.map((c, idx) => (
                  <div key={idx} className="grid grid-cols-2 gap-4 items-center">
                    <Label className="text-muted-foreground">{c.name}</Label>
                    <Input type="number" value={c.value} onChange={(e) => {
                      const newC = [...editedData.cannabinoids];
                      newC[idx].value = parseFloat(e.target.value);
                      setEditedData({...editedData, cannabinoids: newC});
                    }} className="h-8 bg-white/5 border-white/10" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Preview Side */}
          <div className="w-1/2 bg-black/40 flex flex-col">
            <div className="flex-1 flex items-center justify-center p-8">
              {report.preview_url ? (
                <img src={`data:image/png;base64,${report.preview_url}`} className="max-w-full max-h-full rounded-lg shadow-2xl neon-glow-purple" alt="Dashboard Preview" />
              ) : (
                <div className="text-center space-y-4">
                  <div className="w-24 h-24 rounded-3xl glass mx-auto flex items-center justify-center opacity-40">
                    <Eye className="w-10 h-10" />
                  </div>
                  <p className="text-muted-foreground">No preview generated yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <DialogFooter className="p-6 border-t border-white/5 gap-3">
          <Button variant="outline" className="glass" onClick={handleSave}>
            <Save className="w-4 h-4 mr-2" /> Save Draft
          </Button>
          <Button onClick={handleGeneratePreview} className="neon-glow-purple" disabled={isPreviewLoading}>
            {isPreviewLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            Generate Premium PNG
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
