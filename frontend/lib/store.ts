import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Cannabinoid {
  name: string
  value: number
  unit: string
  display_label?: string
}

export interface Terpene {
  name: string
  value: number
  unit: string
  display_effects?: string[]
}

export interface LabReportData {
  id: string
  strain_name: string
  strain_type?: string
  dominance?: string
  lab_name?: string
  producer?: string
  batch?: string
  lot_number?: string
  sample_id?: string
  test_date?: string
  origin?: string
  genetics?: string
  cannabinoids: Cannabinoid[]
  terpenes: Terpene[]
  confidence: number
  source_type: string
  file_name: string
  preview_url?: string
  status: 'pending' | 'extracting' | 'reviewing' | 'completed' | 'failed'
}

interface StrainState {
  reports: LabReportData[]
  activeReportId: string | null
  isProcessing: boolean
  addReport: (report: LabReportData) => void
  updateReport: (id: string, updates: Partial<LabReportData>) => void
  removeReport: (id: string) => void
  setActiveReport: (id: string | null) => void
  setProcessing: (val: boolean) => void
  loadDemo: () => void
}

export const useStrainStore = create<StrainState>()(
  persist(
    (set) => ({
      reports: [],
      activeReportId: null,
      isProcessing: false,
      addReport: (report) => set((state) => ({ 
        reports: [report, ...state.reports],
        activeReportId: report.id 
      })),
      updateReport: (id, updates) => set((state) => ({
        reports: state.reports.map((r) => r.id === id ? { ...r, ...updates } : r)
      })),
      removeReport: (id) => set((state) => ({
        reports: state.reports.filter((r) => r.id !== id),
        activeReportId: state.activeReportId === id ? null : state.activeReportId
      })),
      setActiveReport: (id) => set({ activeReportId: id }),
      setProcessing: (val) => set({ isProcessing: val }),
      loadDemo: () => {
        const demoId = 'demo-report-123';
        const demoReport: LabReportData = {
          id: demoId,
          strain_name: "Blue Dream",
          strain_type: "Sativa-dominant",
          dominance: "60% Sativa",
          lab_name: "GSI Labs",
          producer: "Pacific Green",
          batch: "BD-2024-001",
          lot_number: "L-8829",
          sample_id: "SAMPLE-X",
          test_date: "2024-03-24",
          origin: "California, USA",
          genetics: "Blueberry x Haze",
          cannabinoids: [
            { name: "Total THC", value: 22.5, unit: "%", display_label: "High Potency" },
            { name: "Total CBD", value: 0.1, unit: "%" },
            { name: "CBG", value: 1.2, unit: "%" }
          ],
          terpenes: [
            { name: "Myrcene", value: 0.85, unit: "%", display_effects: ["Relaxing", "Sedating"] },
            { name: "Pinene", value: 0.45, unit: "%" },
            { name: "Caryophyllene", value: 0.32, unit: "%" }
          ],
          confidence: 0.99,
          source_type: "image",
          file_name: "blue_dream_coa.png",
          status: 'reviewing'
        };
        set((state) => ({
          reports: [demoReport, ...state.reports.filter(r => r.id !== demoId)],
          activeReportId: demoId
        }));
      }
    }),
    {
      name: 'strain-ai-history',
    }
  )
)
