"use client";

import { useState, useEffect } from "react";
import { useStrainStore, LabReportData } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Loader2, Save, Download, Eye, Sparkles, 
  Plus, Trash2, Smartphone, Monitor, ChevronRight 
} from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ReviewDialog() {
  const { reports, activeReportId, setActiveReport, updateReport } = useStrainStore();
  const report = reports.find((r) => r.id === activeReportId);
  
  const [editedData, setEditedData] = useState<LabReportData | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [is4KLoading, setIs4KLoading] = useState(false);

  useEffect(() => {
    if (report && !editedData) setEditedData({ ...report });
  }, [report, editedData]);

  if (!report || !editedData) return null;

  const handleSave = async () => {
    updateReport(report.id, { ...editedData });
    toast.success("Data saved locally");
  };

  const handleGeneratePreview = async (width = 1920, height = 1080) => {
    const isHighRes = width > 2000;
    if (isHighRes) setIs4KLoading(true);
    else setIsPreviewLoading(true);
    
    try {
      const resp = await axios.post(`${API_BASE_URL}/generate-preview`, {
        data: editedData,
        width,
        height
      });
      
      if (isHighRes) {
        const link = document.createElement('a');
        link.href = `data:image/png;base64,${resp.data.image_data}`;
        link.download = `${editedData.strain_name.replace(/\s+/g, '_')}_4K_Dashboard.png`;
        link.click();
        toast.success("4K Dashboard Downloaded!");
      } else {
        updateReport(report.id, { preview_url: resp.data.image_data, status: 'completed' });
        toast.success("Preview Generated!");
      }
    } catch (e) {
      toast.error("Generation failed");
    } finally {
      if (isHighRes) setIs4KLoading(false);
      else setIsPreviewLoading(false);
    }
  };

  const addCannabinoid = () => {
    setEditedData({
      ...editedData,
      cannabinoids: [...editedData.cannabinoids, { name: "NEW", value: 0, unit: "%" }]
    });
  };

  const removeCannabinoid = (idx: number) => {
    const newC = [...editedData.cannabinoids];
    newC.splice(idx, 1);
    setEditedData({ ...editedData, cannabinoids: newC });
  };

  const addTerpene = () => {
    setEditedData({
      ...editedData,
      terpenes: [...editedData.terpenes, { name: "NEW", value: 0, unit: "%" }]
    });
  };

  const removeTerpene = (idx: number) => {
    const newT = [...editedData.terpenes];
    newT.splice(idx, 1);
    setEditedData({ ...editedData, terpenes: newT });
  };

  return (
    <Dialog open={!!activeReportId} onOpenChange={(open) => {
        if (!open) {
            setActiveReport(null);
            setEditedData(null);
        }
    }}>
      <DialogContent className="max-w-6xl h-[90vh] flex flex-col glass border-white/10 p-0 overflow-hidden backdrop-blur-3xl">
        <DialogHeader className="p-6 border-b border-white/5 flex flex-row items-center justify-between space-y-0">
          <DialogTitle className="text-2xl font-outfit flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary animate-pulse" /> Editor de Dashboard: {editedData.strain_name}
          </DialogTitle>
          <div className="flex gap-2">
             <Button variant="outline" size="sm" className="glass border-white/10" onClick={handleSave}>
               <Save className="w-4 h-4 mr-2" /> Guardar Cambios
             </Button>
          </div>
        </DialogHeader>

        <div className="flex-1 flex overflow-hidden">
          {/* Editor Side */}
          <div className="w-2/5 border-r border-white/5 flex flex-col bg-black/20">
            <Tabs defaultValue="general" className="flex-1 flex flex-col">
              <div className="px-6 pt-4">
                <TabsList className="grid grid-cols-4 bg-white/5 p-1">
                  <TabsTrigger value="general">Gral</TabsTrigger>
                  <TabsTrigger value="cann">Cann</TabsTrigger>
                  <TabsTrigger value="terp">Terp</TabsTrigger>
                  <TabsTrigger value="details">Dets</TabsTrigger>
                </TabsList>
              </div>

              <ScrollArea className="flex-1 px-6 py-4">
                <TabsContent value="general" className="mt-0 space-y-4">
                  <div className="grid gap-2">
                    <Label className="text-xs uppercase tracking-widest text-muted-foreground">Nombre de la Cepa</Label>
                    <Input value={editedData.strain_name} onChange={(e) => setEditedData({...editedData, strain_name: e.target.value})} className="bg-white/5 border-white/10 font-bold" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label className="text-xs uppercase tracking-widest text-muted-foreground">Tipo</Label>
                      <Input value={editedData.strain_type || ""} onChange={(e) => setEditedData({...editedData, strain_type: e.target.value})} placeholder="Indica/Sativa..." className="bg-white/5 border-white/10" />
                    </div>
                    <div className="grid gap-2">
                      <Label className="text-xs uppercase tracking-widest text-muted-foreground">Dominancia</Label>
                      <Input value={editedData.dominance || ""} onChange={(e) => setEditedData({...editedData, dominance: e.target.value})} placeholder="60% Sativa..." className="bg-white/5 border-white/10" />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs uppercase tracking-widest text-muted-foreground">Laboratorio</Label>
                    <Input value={editedData.lab_name || ""} onChange={(e) => setEditedData({...editedData, lab_name: e.target.value})} className="bg-white/5 border-white/10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs uppercase tracking-widest text-muted-foreground">Productor</Label>
                    <Input value={editedData.producer || ""} onChange={(e) => setEditedData({...editedData, producer: e.target.value})} className="bg-white/5 border-white/10" />
                  </div>
                </TabsContent>

                <TabsContent value="cann" className="mt-0 space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="text-sm font-bold text-primary tracking-widest uppercase">Cannabinoides (%)</h5>
                    <Button variant="ghost" size="icon" onClick={addCannabinoid} className="h-6 w-6 rounded-full bg-primary/20 text-primary hover:bg-primary/40">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-3">
                    {editedData.cannabinoids.map((c, idx) => (
                      <div key={idx} className="flex gap-2 items-center">
                        <Input value={c.name} onChange={(e) => {
                          const newC = [...editedData.cannabinoids];
                          newC[idx].name = e.target.value;
                          setEditedData({...editedData, cannabinoids: newC});
                        }} className="flex-1 h-8 bg-white/5 border-white/10 text-xs" />
                        <Input type="number" value={c.value} onChange={(e) => {
                          const newC = [...editedData.cannabinoids];
                          newC[idx].value = parseFloat(e.target.value) || 0;
                          setEditedData({...editedData, cannabinoids: newC});
                        }} className="w-20 h-8 bg-white/5 border-white/10 text-xs" />
                        <Button variant="ghost" size="icon" onClick={() => removeCannabinoid(idx)} className="h-8 w-8 text-muted-foreground hover:text-destructive">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="terp" className="mt-0 space-y-4">
                   <div className="flex items-center justify-between mb-2">
                    <h5 className="text-sm font-bold text-secondary tracking-widest uppercase">Perfil de Terpenos (%)</h5>
                    <Button variant="ghost" size="icon" onClick={addTerpene} className="h-6 w-6 rounded-full bg-secondary/20 text-secondary hover:bg-secondary/40">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="space-y-3">
                    {editedData.terpenes.map((t, idx) => (
                      <div key={idx} className="flex gap-2 items-center">
                        <Input value={t.name} onChange={(e) => {
                          const newT = [...editedData.terpenes];
                          newT[idx].name = e.target.value;
                          setEditedData({...editedData, terpenes: newT});
                        }} className="flex-1 h-8 bg-white/5 border-white/10 text-xs" />
                        <Input type="number" value={t.value} onChange={(e) => {
                          const newT = [...editedData.terpenes];
                          newT[idx].value = parseFloat(e.target.value) || 0;
                          setEditedData({...editedData, terpenes: newT});
                        }} className="w-20 h-8 bg-white/5 border-white/10 text-xs" />
                        <Button variant="ghost" size="icon" onClick={() => removeTerpene(idx)} className="h-8 w-8 text-muted-foreground hover:text-destructive">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="details" className="mt-0 space-y-4">
                   <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label className="text-xs uppercase tracking-widest text-muted-foreground">Origen</Label>
                      <Input value={editedData.origin || ""} onChange={(e) => setEditedData({...editedData, origin: e.target.value})} placeholder="California, USA..." className="bg-white/5 border-white/10" />
                    </div>
                    <div className="grid gap-2">
                      <Label className="text-xs uppercase tracking-widest text-muted-foreground">Genética</Label>
                      <Input value={editedData.genetics || ""} onChange={(e) => setEditedData({...editedData, genetics: e.target.value})} placeholder="Blueberry x Haze..." className="bg-white/5 border-white/10" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label className="text-xs uppercase tracking-widest text-muted-foreground">Lote / Batch</Label>
                      <Input value={editedData.batch || ""} onChange={(e) => setEditedData({...editedData, batch: e.target.value})} className="bg-white/5 border-white/10" />
                    </div>
                    <div className="grid gap-2">
                      <Label className="text-xs uppercase tracking-widest text-muted-foreground">Lot Number</Label>
                      <Input value={editedData.lot_number || ""} onChange={(e) => setEditedData({...editedData, lot_number: e.target.value})} className="bg-white/5 border-white/10" />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs uppercase tracking-widest text-muted-foreground">Fecha de Test</Label>
                    <Input value={editedData.test_date || ""} onChange={(e) => setEditedData({...editedData, test_date: e.target.value})} className="bg-white/5 border-white/10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs uppercase tracking-widest text-muted-foreground">Sample ID</Label>
                    <Input value={editedData.sample_id || ""} onChange={(e) => setEditedData({...editedData, sample_id: e.target.value})} className="bg-white/5 border-white/10" />
                  </div>
                </TabsContent>
              </ScrollArea>
            </Tabs>
          </div>

          {/* Preview Side */}
          <div className="flex-1 bg-black/40 flex flex-col relative group">
            <div className="flex-1 flex items-center justify-center p-8 overflow-hidden">
              {report.preview_url ? (
                <div className="relative max-w-full max-h-full">
                    <img 
                        src={`data:image/png;base64,${report.preview_url}`} 
                        className="max-w-full max-h-full rounded-lg shadow-2xl ring-1 ring-white/10 object-contain" 
                        alt="Dashboard Preview" 
                    />
                    <div className="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                         <div className="bg-black/60 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-bold tracking-widest flex items-center gap-1 border border-white/10">
                            <Monitor className="w-3 h-3" /> PREVIEW HD (1080p)
                         </div>
                    </div>
                </div>
              ) : (
                <div className="text-center space-y-4">
                  <div className="w-24 h-24 rounded-3xl glass mx-auto flex items-center justify-center opacity-40">
                    <Eye className="w-10 h-10" />
                  </div>
                  <p className="text-muted-foreground font-outfit uppercase tracking-widest text-xs">No hay vista previa generada</p>
                </div>
              )}
            </div>
            
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4">
                 <Button 
                    onClick={() => handleGeneratePreview(1920, 1080)} 
                    className="neon-glow-purple px-8 py-6 text-lg font-bold" 
                    disabled={isPreviewLoading}
                >
                    {isPreviewLoading ? <Loader2 className="w-5 h-4 mr-2 animate-spin" /> : <Eye className="w-5 h-5 mr-2" />}
                    Actualizar Vista Previa
                </Button>
            </div>
          </div>
        </div>

        <DialogFooter className="p-6 border-t border-white/5 bg-black/40 flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-muted-foreground uppercase tracking-tighter">
             <div className="flex items-center gap-1"><ChevronRight className="w-3 h-3 text-primary" /> IA Extraction: {Math.round(report.confidence * 100)}%</div>
             <div className="flex items-center gap-1"><ChevronRight className="w-3 h-3 text-primary" /> Template: Vercel Premium Dark</div>
          </div>
          <div className="flex gap-3">
             <Button 
                variant="outline" 
                className="glass border-white/10 h-12 px-6" 
                onClick={() => handleGeneratePreview(3840, 2160)}
                disabled={is4KLoading}
            >
                {is4KLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                Descargar Imagen 4K
             </Button>
             <Button 
                className="h-12 px-8 bg-white text-black hover:bg-white/90 font-bold" 
                onClick={() => setActiveReport(null)}
            >
                Cerrar Editor
             </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
